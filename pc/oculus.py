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
    global y_data, x_data
    y_data = 0
    x_data = 0
    while 1:
        events = inputs.get_gamepad()
        sys.stdout.flush()
        event = events[-1]
        if lock.acquire(True):
            if event.code == 'ABS_Y':
                y_data = event.state
            elif event.code == 'ABS_X':
                x_data = event.state
            lock.release()
            
        time.sleep(0.001)


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
    
    print_after = 10
    count = 0
    print("Starting stream loop")
    yvel = 0
    xvel = 0
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
                yvel = y_data * 127 / 32768.0 # Scale to int8_t
                xvel = x_data * 127 / 32768.0 # Scale to int8_t
                lock.release()
            
            if count % print_after == 0:
                print("Pitch: {0}| Yaw: {1}| Yvel: {2} | Xvel: {3}".format(pitch, yaw, yvel, xvel))
            
            if not dryrun:
                tx.transmit(pitch=pitch, yaw=yaw, yvel=yvel, xvel=xvel)
            
            sys.stdout.flush()
            count = count + 1
        time.sleep(0.010)


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

    gp = inputs.devices.gamepads
    if len(gp) == 0 or 'microsoft' not in str(gp[0]).lower():
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
