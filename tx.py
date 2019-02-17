# Transmitter.py

import serial
import numpy as np
import struct

def clamp(n, min, max):
    '''
    n is returned if it is in range [min, max], otherwise the closest of min and
    max to n is returned
    '''
    
    return min if n < min else max if n > max else n


class Transmitter:
    def __init__(self, ser):
        self.ser = ser
        
    def transmit(self, angles):
        '''
        Send camera angles to MCU
        
        Parameters
        ----------
        angles : np.ndarray
            Elements 0 and 1 of the vector are the pitch and yaw of the HMD,
            respectively
        '''
        
        pitch = np.round(angles[0])
        yaw = np.round(angles[1])
        
        # Don't allow values outside the range of the servos
        pitch = clamp(pitch, 0, 180)
        yaw = clamp(yaw, 0, 180)
        print("Pitch: {0}| Yaw: {1}".format(pitch, yaw))
        
        # Convert representations to binary
        raw_data = bytes(''.encode())
        raw_data = raw_data + struct.pack('<B', pitch) + struct.pack('<B', yaw)
        
        # Transfer data
        self.ser.write(raw_data)
        