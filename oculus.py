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
import ovr
import serial

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


def stream_loop(session, tx):
    '''
    Collect head orientation data from the Oculus Rift and stream it to the
    microcontroller, forever.
    
    Parameters
    ----------
    session : pointer to HmdDesc
        Interface for the head-moounted device
    tx : tx.Transmitter
        Interface for serial port
    '''
    
    while True:
        # Query the HMD for the current tracking state.
        ts  = ovr.getTrackingState(session, ovr.getTimeInSeconds(), True)
        if ts.StatusFlags & (ovr.Status_OrientationTracked | ovr.Status_PositionTracked):
            pose = ts.HeadPose
            print pose.ThePose
            #tx.transmit(pose)
            sys.stdout.flush()
        time.sleep(0.20)


def main():
    args = util.parse_args()
    session = init_oculus()
    
    port = args['port']
    baud = args['baud']
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
    ovr.destroy(session)
    ovr.shutdown()


if __name__ == "__main__":
    main()
    sys.exit(0)
