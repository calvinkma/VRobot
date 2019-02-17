# Transmitter.py

import serial
import numpy as np
import struct


class Transmitter:
    def __init__(self, ser):
        self.ser = ser
        
    def transmit(self, pitch, yaw, velocity):
        '''
        Send camera angles to MCU
        
        Parameters
        ----------
        pitch : double
            Pitch of the HMD
        yaw : double
            Yaw of the HMD
        velocity : double
            Represents the velocity of the robot. Take forward to be positive
        '''
        
        # Convert representations to binary
        raw_data = bytes(''.encode())
        raw_data = raw_data + struct.pack('<B', pitch) + struct.pack('<B', yaw)
        raw_data = raw_data + struct.pack('<b', velocity)
        
        # Transfer data
        self.ser.write(raw_data)
        