# Transmitter.py

import serial
import numpy as np
import struct

class Transmitter:
    def __init__(self, ser):
        self.ser = ser
        
    def transmit(self, goal_angles):
        '''
        Converts the motor array from the coordinate system used by controls to
        that used by embedded and sends it to the MCU over serial
        '''
        goal_angles = ctrlToMcuAngles(goal_angles)
        
        self.send_packet_to_mcu(self.vec2bytes(goal_angles))
        self.num_transmissions = self.num_transmissions + 1