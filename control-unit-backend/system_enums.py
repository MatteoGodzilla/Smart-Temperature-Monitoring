from enum import Enum
'''
This enum represents the control mode of the window:
-> AUTOMATIC: The control-unit decide the window opening percentage.
-> LOCAL_MANUAL: The in-site operator controls the window.
-> REMOTE_MANUAL: The dashboard operator controls the window.
'''
class Mode(Enum):
    AUTOMATIC = 0
    LOCAL_MANUAL = 1
    REMOTE_MANUAL = 2

'''
This enum represents the Finite State Machine situation 
related to the temperature.
'''
class Status(Enum):
    NORMAL = 0
    HOT = 1
    TOO_HOT = 2
    ALARM = 3

