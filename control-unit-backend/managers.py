import time
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
class Timer():
    def __init__(self, wait_time:float=100.00):
        self.threshold = wait_time
        self.reset()

    def set(self):
        self.reset()
        self.started = True

    def reset(self) -> None:
        self.started = False
        self.start_time = time.time()
        self.elapsed = time.time()

    def update(self) -> None:
        self.elapsed = time.time() - self.start_time

    def is_over(self) -> bool:
        return ( self.elapsed >= self.threshold )

    def is_set(self) -> bool:
        return self.started
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

class TemperatureAccessManager():
    def __init__(self, max_len=5):
        self.temperatureAVG:float = 0
        self.temperatureSUM:float = 0
        self.DATAPOINT_BUFFER:int = max_len
        # The internal DataPoints collection.
        # One DataPoint represents a "screenshot" of the window situation.
        self.datapoints:deque = deque(maxlen=self.DATAPOINT_BUFFER)

        # TEST VALUES ZONE - REMOVE ON RELEASE
        self.enqueueDataPoint(1000.50, 34.55, 0.24)
        self.enqueueDataPoint(2000.23, 30.45, 0.14)
        self.enqueueDataPoint(2500.45, 38.50, 0.86)
        self.enqueueDataPoint(4250.00, 26.76, 0.03)
        self.enqueueDataPoint(4555.00, 28.73, 0.08)
        self.enqueueDataPoint(4650.00, 27.72, 0.01)
        # END TEST ZONE

    # This method will be called when a new datapoint is received from ESP32 using MQTT.
    # TODO: Manage race conditions between writer (Thread MQTT) and reader (Thread Flask).
    def enqueueDataPoint(self, timestamp:float, temperature:float, window:float) -> None:
        # If the deque is full, then remove the oldest datapoint inserted.
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
        self.position:float = 0.00
        self.active_mode = Mode.AUTOMATIC

    def move(self, position:float = 0.00) -> None:
        self.position = position

    def get_position(self) -> float:
        return self.position

    def set_mode(self, mode:Mode) -> None:
        self.active_mode = mode

    def get_mode(self) -> Mode:
        return self.active_mode

    def check_mode(self, mode_to_check:Mode) -> bool:
        return ( self.active_mode == mode_to_check )

class Manager():
    def __init__(self, max_datapoints=5):
        self.FIRST_FREQUENCY:int = 4
        self.SECOND_FREQUENCY:int = 8
        self.FIRST_THRESHOLD:float = 27.00
        self.SECOND_THRESHOLD:float = 35.00
        self.TIME_TO_ALARM:float = 10.00
        self.alarm_timer:Timer = Timer(wait_time=self.TIME_TO_ALARM)
        self.control_timer:Timer = Timer(wait_time=60.00)
        self.actual_state:Status = Status.NORMAL
        self.window_controller:WindowManager = WindowManager()
        self.temperature_access:TemperatureAccessManager = TemperatureAccessManager(max_len=max_datapoints)

    # TODO: Manage race conditions between writer (Thread MQTT) and reader (Thread Flask).
    def getLatest(self) -> dict:
        return {
            "status" : self.actual_state.value,                           # Actual integer value of active FSM status
            "mode" : (self.window_controller.get_mode()).value,                              # Actual control mode
            "datapoint" : self.temperature_access.getDataPoint(index=-1), # Latest datapoint inserted
            "nextStatus" : 100                                            # Time to wait to send another request - MAYBE ADD LOGIC BEHIND THIS VALUE
        }

    # TODO: Manage race conditions between writer (Thread MQTT) and reader (Thread Flask).
    def generateHistory(self) -> dict:
        return {
            "dataPoints" : list(self.temperature_access.getDataPoints()), # The datapoints list
            "minimum" : self.temperature_access.getMinTemperature(),      # Maximum temperature in memory
            "maximum" : self.temperature_access.getMaxTemperature(),      # Minimum temperature in memory
            "average" : self.temperature_access.getAverageTemperature()   # Average temperature between all temperature values in memory
        }

    def adjust_state(self):
        last_temperature = self.temperature_access.getDataPoint(index=-1).get("temperature")
        if self.alarm_timer.is_set():
            self.alarm_timer.update()
        if last_temperature < self.FIRST_THRESHOLD:
            self.actual_state = Status.NORMAL
            self.alarm_timer.reset()
        elif last_temperature >= self.FIRST_THRESHOLD and last_temperature <= self.SECOND_THRESHOLD:
            self.actual_state = Status.HOT
            self.alarm_timer.reset()
        elif last_temperature > self.SECOND_THRESHOLD and not self.alarm_timer.is_set():
            self.actual_state = Status.TOO_HOT
            self.alarm_timer.set()
        elif self.alarm_timer.is_over():
            self.actual_state = Status.ALARM
            self.alarm_timer.reset()
    def change_state(self, state:Status):
        self.actual_state = state

    def get_state(self) -> Status:
        return self.actual_state

    def change_mode(self, mode:Mode):
        if (self.window_controller.check_mode(Mode.AUTOMATIC)) or (self.control_timer.is_over()):
            self.window_controller.set_mode(mode)
            self.control_timer.set()
        else:
            self.control_timer.reset()

    def get_mode(self) -> Mode:
        return self.window_controller.get_mode()

    def receive_temperature(self, data:float) -> None:
        self.temperature_access.enqueueDataPoint(
            timestamp = time.time(),                        # Datapoint reception timestamp (optional)
            temperature = data,                             # Received temperature
            window = self.window_controller.get_position()  # Actual Window opening percentage
        )
        self.adjust_state() #FIXME: at the moment the temperaure situation is checked everytime one new temperature is received.

    def receive_opening_percentage(self, percentage:float = 0.00) -> None:
        if self.window_controller.check_mode(Mode.LOCAL_MANUAL) or self.window_controller.check_mode(Mode.REMOTE_MANUAL):
            self.window_controller.move(percentage)

    def get_opening_percentage(self) -> float:
        return self.window_controller.get_position()

    def check_if_active(self, mode:Mode) -> bool:
        return self.window_controller.check_mode(mode_to_check=mode)

    def check_and_fix_control(self):
        if self.control_timer.is_set():
            self.control_timer.update()
            if self.control_timer.is_over():
                self.control_timer.reset()
                self.window_controller.set_mode(Mode.AUTOMATIC)

    def update(self) -> None:
        self.check_and_fix_control()
        if self.window_controller.check_mode(Mode.AUTOMATIC):
            # some instruction to decide the new percentage
            self.window_controller.move()