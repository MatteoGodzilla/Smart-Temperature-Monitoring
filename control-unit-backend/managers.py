import threading
from collections import deque

'''
TODO:
    -> MANAGE RACE CONDITIONS  BETWEEN WRITERS-READERS.
    -> ADD ENUM FOR FINITE STATE MACHINE STATUS.
    -> ADD ENUM FOR FINITE STATE MACHINE CONTROL MODE.
    -> ADD LOGIC TO MANAGE REMOTE MANUAL CONTROL.
'''

class AccessManager():
    DATAPOINT_BUFFER = 20
    temperatureAVG = 0
    temperatureSUM = 0
    def __init__(self):
        self.datapoints:deque = deque(maxlen=self.DATAPOINT_BUFFER)

    def putDataPoint(self, timestamp:float, temperature:float, window:float):
        if self.datapoints.count() == self.DATAPOINT_BUFFER:
            self.temperatureSUM -= self.datapoints[0]['temperature']
            self.datapoints.popleft()
        self.datapoints.append({
            "timestamp" : timestamp,
            "temperature" : temperature,
            "window" : window
        })
        self.temperatureSUM += temperature
        self.temperatureAVG = self.temperatureSUM / self.datapoints.count()

    def getLatest(self):
        return {
            "status" : "TODO",
            "mode" : "TODO",
            "datapoint" : self.datapoints[-1],
            "nextStatus" : "TODO"
        }

    def generateHistory(self):
        return {
            "dataPoints" : self.datapoints,
            "minimum" : min(self.datapoints, key = lambda point : point['temperature'])['temperature'],
            "maximum" : max(self.datapoints, key = lambda point : point['temperature'])['temperature'],
            "average" : self.temperatureAVG
        }