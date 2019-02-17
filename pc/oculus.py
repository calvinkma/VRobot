# oculus.py
#
# This program collects head orientation data from an Oculus Rift and streams
# it over virtual COM port.
#
# The ovr libraries used are from github.com/cmbruns/pyovr and this project
# builts on top of the example code there for interfacing with the Oculus.

# Libraries
import sys
import time
import serial
import numpy as np
from threading import Thread, Lock
import ovr
import inputs

# Local files
import utility as util
from tx import Transmitter

def init_oculus():
    '''
    Initialize a session with the Oculus Rift. The session will allow us to
    query it for data
    '''
    ovr.initialize(None)
    session, luid = ovr.create()
    print("Connected to Oculus")
    return session


def clamp(n, min, max):
    '''
    n is returned if it is in range [min, max], otherwise the closest of min and
    max to n is returned
    '''
    
    return min if n < min else max if n > max else n


lock = Lock()
def gamepad_loop():
    '''
    Reads from the Xbox controller
    '''
    
    # Read from gamepad forever, and store the y data (vertical deviation of
    # left thumbstick) in the global variable, protected by a lock
    print("Starting gamepad loop")
    global y_data
    y_data = 0
    while 1:
        event = inputs.get_gamepad()[-1]
        if event.code == 'ABS_Y' and lock.acquire(True):
            y_data = event.state
            lock.release()
        time.sleep(0.050)


def stream_loop(session, tx, dryrun=False):
    '''
    Collect head orientation data from the Oculus Rift and stream it to the
    microcontroller, forever.
    
    Parameters
    ----------
    session : pointer to HmdDesc
        Interface for the head-moounted device
    tx : tx.Transmitter
        Interface for serial port
    dryrun : bool
        If True, runs the test mode of the loop where there is no MCU
        communication
    '''
    
    print("Starting stream loop")
    velocity = 0
    while True:
        # Query the HMD for the current tracking state.
        ts  = ovr.getTrackingState(session, ovr.getTimeInSeconds(), True)
        if ts.StatusFlags & (ovr.Status_OrientationTracked | ovr.Status_PositionTracked):
            pose = ts.HeadPose
            angles = np.array(pose.ThePose.Orientation.getEulerAngles())* 180 / np.pi
            pitch = np.round(angles[0] * -1 + 90)
            yaw = np.round(angles[1] + 90)
            
            # Don't allow values outside the range of the servos
            pitch = clamp(pitch, 0, 180)
            yaw = clamp(yaw, 0, 180)
            
            # Get data from gamepad thread
            if lock.acquire(True):
                velocity = y_data * 127 / 32768.0 # Scale to int8_t
                lock.release()
            
            print("Pitch: {0}| Yaw: {1}| Yvel: {2}".format(pitch, yaw, velocity))
            if not dryrun:
                tx.transmit(angles, velocity)
            
            sys.stdout.flush()
        time.sleep(0.050)


def exit(session):
    '''
    Exit program.
    
    Parameters
    ----------
    session : pointer to HmdDesc
        Interface for the head-moounted device
    '''
    
    ovr.destroy(session)
    ovr.shutdown()


def main():
    args = util.parse_args()
    session = init_oculus()
    
    port = args['port']
    baud = args['baud']
    dryrun = args['dryrun']

    if 'microsoft' not in str(inputs.devices.gamepads[0]).lower():
        print("Xbox controller not detected")
        exit(session)
        return
    
    # Read from the gamepad in a different thread since the inputs library
    # blocks program execution
    try:
        gamepad_thread = Thread(target=gamepad_loop)
        gamepad_thread.daemon = True
        gamepad_thread.start()
    
        # If we are developing, we don't worry about the serial port
        if dryrun:
            stream_loop(session, -1, True)
        
        num_tries = 0
        while(True):
            try:
                with serial.Serial(port, baud, timeout=0) as ser:
                    print("Connected to embedded")
                    tx = Transmitter(ser)
                    stream_loop(session, tx)
            
            except serial.serialutil.SerialException as e:
                if(num_tries % 100 == 0):
                    if(str(e).find("FileNotFoundError")):
                        print("Port not found. Retrying...(attempt {0})".format(num_tries))
                    else:
                        print("Serial exception. Retrying...(attempt {0})".format(num_tries))
                
                time.sleep(0.01)
                num_tries = num_tries + 1
    except (KeyboardInterrupt, SystemExit) as e:
        print("Interrupted: {0}".format(e))
        pass

    exit(session)


if __name__ == "__main__":
    main()
    sys.exit(0)
