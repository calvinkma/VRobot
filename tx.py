# Transmitter.py

import serial
import numpy as np
import struct

class Transmitter:
    def __init__(self, ser):
        self.ser = ser
        
    def transmit(self, goal_angles):
        '''
        
        '''
        