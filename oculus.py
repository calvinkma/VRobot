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
import ovr

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
    
    while True:
        # Query the HMD for the current tracking state.
        ts  = ovr.getTrackingState(session, ovr.getTimeInSeconds(), True)
        if ts.StatusFlags & (ovr.Status_OrientationTracked | ovr.Status_PositionTracked):
            pose = ts.HeadPose
            angles = np.array(pose.ThePose.Orientation.getEulerAngles())* 180 / np.pi
            angles[0] = angles[0] * -1 + 90
            angles[1] = angles[1] + 90
            if not dryrun:
                print("not dryrun")
                #tx.transmit(angles)
            else:
                print(angles)
            sys.stdout.flush()
        time.sleep(0.20)


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
    if dryrun:
        try:
            stream_loop(session, -1, True)
        except KeyboardInterrupt as e:
            print("Interrupted: {0}".format(e))
            exit(session)
    
    num_tries = 0
    while(True):
        try:
            with serial.Serial(port, baud, timeout=0) as ser:
                print("Connected to embedded")
                tx = Transmitter(ser)
                stream_loop(session, tx)
        
        except serial.serialutil.SerialException as e:
            try:
                if(num_tries % 100 == 0):
                    if(str(e).find("FileNotFoundError")):
                        print("Port not found. Retrying...(attempt {0})".format(num_tries))
                    else:
                        print("Serial exception. Retrying...(attempt {0})".format(num_tries))
                
                time.sleep(0.01)
                num_tries = num_tries + 1
            except KeyboardInterrupt as e:
                print("Interrupted: {0}".format(e))
                break
        except KeyboardInterrupt as e:
            print("Interrupted: {0}".format(e))
            break
    exit(session)

if __name__ == "__main__":
    main()
    sys.exit(0)
