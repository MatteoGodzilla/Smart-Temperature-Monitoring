import threading
from collections import deque

'''
TODO:
    -> MANAGE RACE CONDITIONS  BETWEEN WRITERS-READERS.
    -> ENUMS USAGE LOGIC IMPLEMENTATIONS.
    -> ADD LOGIC TO MANAGE REMOTE MANUAL CONTROL.
'''

class AccessManager():
    def __init__(self, max_len=5):
        self.temperatureAVG:float = 0
        self.temperatureSUM:float = 0
        self.DATAPOINT_BUFFER:int = max_len
        # This enum represents the Finite State Machine situation related to the temperature.
        self.statuses:enumerate = enumerate([
            "NORMAL",  # 0
            "HOT",     # 1
            "TOO_HOT", # 2
            "ALARM"    # 3
        ])
        # This enum represents the control mode of the window:
        # AUTOMATIC: The control-unit decide the window opening percentage.
        # REMOTE_MANUAL: The dashboard operator controls the window.
        # LOCAL_MANUAL: The in-site operator controls the window.
        self.modes:enumerate = enumerate([
            "AUTOMATIC",    # 0
            "LOCAL_MANUAL", # 1
            "REMOTE_MANUAL" # 2
        ])
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
    def enqueueDataPoint(self, timestamp:float, temperature:float, window:float):
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

    # TODO: Manage race conditions between writer (Thread MQTT) and reader (Thread Flask).
    def getLatest(self):
        return {
            "status" : "TODO",                 # actual FSM status
            "mode" : "TODO",                   # actual control mode
            "datapoint" : self.datapoints[-1], # latest datapoint inserted
            "nextStatus" : 100                 # Time to wait to send another request - MAYBE ADD LOGIC BEHIND THIS VALUE
        }

    # TODO: Manage race conditions between writer (Thread MQTT) and reader (Thread Flask).
    def generateHistory(self):
        return {
            "dataPoints" : list(self.datapoints),
            "minimum" : min(self.datapoints, key = lambda point : point['temperature'])['temperature'],
            "maximum" : max(self.datapoints, key = lambda point : point['temperature'])['temperature'],
            "average" : self.temperatureAVG
        }