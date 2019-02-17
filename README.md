# VRobot
VRobot contains a collection of embedded programs and an accompanying PC-side script which together allow a user to see through the eyes of a mobile robot using an Oculus Rift, and at the same time control it with their own motions and an Xbox controller.

# Requirements
The Arduino IDE is required to program the microcontrollers, which are an Arduino Uno 101 and Arduino Uno. For the PC-side script, the following Python libraries are required:
- os
- sys
- threading
- serial
- argparse
- numpy
- struct
- time
- ovr
- inputs

# Running the PC-side script
```Python
python oculus.py
```

# Command-line arguments
The PC-side script can be run from a terminal. It supports certain arguments related to communication with the microcontroller, which can be viewed by running:
```Python
python oculus.py --help
```

For example, we can specify a COM port and baud rate like so:
```Python
python oculus.py --port=COM24 --baud=230400
```
