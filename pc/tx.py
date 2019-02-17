# Transmitter.py

import serial
import numpy as np
import struct
import time


class Transmitter:
    def __init__(self, ser):
        self.ser = ser
        self.send_yaw = True
        self.send_pitch = False
        self.send_yvel = True
        self.send_xvel = False
        self.prev_time = time.time()
        self.time_threshold = 0.200
        
    def transmit(self, pitch, yaw, yvel, xvel):
        '''
        Send camera angles to MCU
        
        Parameters
        ----------
        pitch : double
            Pitch of the HMD
        yaw : double
            Yaw of the HMD
        yvel : double
            Represents the target forward velocity of the robot, where +y is
            forward in its frame of reference
        xvel : double
            Represents the target sideways velocity of the robot, where +x is
            right in its frame of reference
        '''
        
        cur_time = time.time()
        if cur_time - self.prev_time > self.time_threshold:
            self.prev_time = cur_time
        else:
            return
        
        # Convert representations to binary
        raw_data = bytes(''.encode()) + struct.pack('<B', 0xFF)
        
        if self.send_yaw:
            raw_data = raw_data + struct.pack('<B', yaw)
        
        if self.send_pitch:
            raw_data = raw_data + struct.pack('<B', pitch)
        
        if self.send_yvel:
            raw_data = raw_data + struct.pack('<b', yvel)
        
        if self.send_xvel:
            raw_data = raw_data + struct.pack('<b', xvel)
        
        # Transfer data
        self.ser.write(raw_data)
        