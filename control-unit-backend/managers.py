import threading
from enum import Enum
from collections import deque

'''
TODO:
    -> MANAGE RACE CONDITIONS BETWEEN WRITERS-READERS.
    -> ADD LOGIC TO MANAGE:
        -> AUTOMATIC (based on temperature change status, calculate new percentage and send it on Serial Thread)
        -> REMOTE MANUAL CONTROL (read from dashboard and send on Serial Thread)
        -> LOCAL MANUAL CONTROL (only listen and save new percentage)
    -> FINISH IMPLEMENTATION OF THE MANAGERS.
'''
# This enum represents the control mode of the window:
# AUTOMATIC: The control-unit decide the window opening percentage.
# REMOTE_MANUAL: The dashboard operator controls the window.
# LOCAL_MANUAL: The in-site operator controls the window.
class Mode(Enum):
    AUTOMATIC = 0
    LOCAL_MANUAL = 1
    REMOTE_MANUAL = 2

# This enum represents the Finite State Machine situation related to the temperature.
class Status(Enum):
    NORMAL = 0
    HOT = 1
    TOO_HOT = 2
    ALARM = 3

class DataAccessManager():
    def __init__(self, max_len=5):
        self.temperatureAVG:float = 0
        self.temperatureSUM:float = 0
        self.DATAPOINT_BUFFER:int = max_len
        # The internal DataPoints collection.
        # One DataPoint represents a "screenshot" of the window situation.
        self.datapoints:deque = deque(maxlen=self.DATAPOINT_BUFFER)

        # TEST VALUES ZONE - REMOVE ON RELEASE
        self.enqueueDataPoint(1000, 34.55, 0.24)
        self.enqueueDataPoint(2000, 30.45, 0.14)
        self.enqueueDataPoint(2500, 38.50, 0.86)
        self.enqueueDataPoint(4250, 26.76, 0.03)
        # END TEST ZONE

    # This method will be called when a new datapoint is received from ESP32 using MQTT.
    # TODO: Manage race conditions between writer (Thread MQTT) and reader (Thread Flask).
    def enqueueDataPoint(self, timestamp:float, temperature:float, window:float) -> None:
        # IF the deque is full, then remove the oldest datapoint inserted.
        if len(self.datapoints) == self.DATAPOINT_BUFFER:
            # Remove from the sum the temperature value of the removed datapoint before the pop.
            self.temperatureSUM -= self.datapoints[0]['temperature']
            # Removing the oldest datapoint inside the deque.
            self.datapoints.popleft()
        self.datapoints.append({
            "timestamp" : timestamp,     # measurement moment expressed in seconds
            "temperature" : temperature, # measured temperature
            "window" : window            # window opening percentage, between [0, 1]
        })
        self.temperatureSUM += temperature
        self.temperatureAVG = self.temperatureSUM / len(self.datapoints)

    def getDataPoints(self) -> deque:
        return self.datapoints

    def getDataPoint(self, index=0) -> dict:
        return self.datapoints[index]

    def getMinTemperature(self) -> float:
        return min(self.datapoints, key = lambda point : point['temperature'])['temperature']

    def getMaxTemperature(self) -> float:
        return max(self.datapoints, key = lambda point : point['temperature'])['temperature']

    def getAverageTemperature(self) -> float:
        return self.temperatureAVG

class WindowManager():
    def __init__(self):
        self.active_mode = Mode.AUTOMATIC

class Manager():
    def __init__(self, max_datapoints=5):
        self.actual_state = Status.NORMAL
        self.data_access = DataAccessManager(max_len=max_datapoints)
        self.window_controller = WindowManager()

    # TODO: Manage race conditions between writer (Thread MQTT) and reader (Thread Flask).
    def getLatest(self) -> dict:
        return {
            "status" : self.actual_state.value,                    # Actual integer value of active FSM status
            "mode" : "TODO",                                       # Actual control mode
            "datapoint" : self.data_access.getDataPoint(index=-1), # Latest datapoint inserted
            "nextStatus" : 100                                     # Time to wait to send another request - MAYBE ADD LOGIC BEHIND THIS VALUE
        }

    # TODO: Manage race conditions between writer (Thread MQTT) and reader (Thread Flask).
    def generateHistory(self) -> dict:
        return {
            "dataPoints" : list(self.data_access.getDataPoints()), # The datapoints list
            "minimum" : self.data_access.getMinTemperature(),      # Maximum temperature in memory
            "maximum" : self.data_access.getMaxTemperature(),      # Minimum temperature in memory
            "average" : self.data_access.getAverageTemperature()   # Average temperature between all temperature values in memory
        }