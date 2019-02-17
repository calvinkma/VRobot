# utility.py

import argparse
import serial.tools.list_ports
import os
import sys

def list_ports():
    ports = serial.tools.list_ports.comports()
    msg = ""
    if(len(ports) == 0):
        msg = "Error: No COM ports have been detected"
    else:
        ports = [port.device for port in ports]
        msg = "Available ports are: " + " ".join(ports)
    return msg

def get_script_path():
    return os.path.dirname(os.path.realpath(sys.argv[0]))
    
def parse_args():
    os.chdir(get_script_path())
    print("Starting PC-side application")
    
    parser = argparse.ArgumentParser(description='Oculus position stream')

    parser.add_argument(
        '--port',
        help='The serial port used for communication. Default: COM7',
        default='COM7'
    )
    
    parser.add_argument(
        '--baud',
        help='Serial port symbol rate. Default: 230400',
        default=230400
    )

    parser.add_argument(
        '--dryrun',
        help='Get Oculus data and print without sending to MCU. Default: False',
        default=False
    )

    return vars(parser.parse_args())