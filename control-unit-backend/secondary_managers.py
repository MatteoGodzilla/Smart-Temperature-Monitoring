from collections import deque
from system_enums import Mode, Status
from timers import Timer
from threading import Condition

class TemperatureAccessManager():
    def __init__(self, max_len=5):
        self.temperatureAVG:float = 0
        self.temperatureSUM:float = 0
        self.DATAPOINT_BUFFER_SIZE:int = max_len
        self.datapoint_condition = Condition()
        self.write_datapoint:bool = False
        self.read_datapoint:bool = False
        # The internal DataPoints collection.
        # One DataPoint represents a "screenshot" of the window situation.
        self.datapoints:deque = deque(maxlen=self.DATAPOINT_BUFFER_SIZE)

    # This method will be called when a new datapoint is received from ESP32 using MQTT.
    # TODO: Manage race conditions between writer (Thread MQTT) and reader (Thread Flask).
    def enqueueDataPoint(self, timestamp:float, temperature:float, window:float) -> None:
        with self.datapoint_condition:
            while self.read_datapoint or self.write_datapoint:
                self.datapoint_condition.wait()
            self.write_datapoint = True
            # If the deque is full, then remove the oldest datapoint inserted.
            if len(self.datapoints) >= self.DATAPOINT_BUFFER_SIZE:
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
            self.write_datapoint = False
            self.datapoint_condition.notify_all()

    def getDataPoints(self) -> deque:
        with self.datapoint_condition:
            while self.write_datapoint:
                self.datapoint_condition.wait()
            self.read_datapoint = True
            if len(self.datapoints) > 0:
                datapoints = self.datapoints
            else:
                datapoints = [{"timestamp" : 0.00, "temperature" : 0.00, "window" : 0.00}]
            self.read_datapoint = False
            self.datapoint_condition.notify_all()
        return datapoints

    def getDataPoint(self, index=0) -> dict:
        with self.datapoint_condition:
            while self.write_datapoint:
                self.datapoint_condition.wait()
            self.read_datapoint = True
            if len(self.datapoints) > 0:
                datapoint = self.datapoints[index]
            else:
                datapoint = {"timestamp" : 0.00, "temperature" : 0.00, "window" : 0.00}
            self.read_datapoint = False
            self.datapoint_condition.notify_all()
        return datapoint

    def getMinTemperature(self) -> float:
        with self.datapoint_condition:
            while self.write_datapoint:
                self.datapoint_condition.wait()
            self.read_datapoint = True
            if len(self.datapoints) > 0:
                min_temperature = min(self.datapoints, key = lambda point : point['temperature'])['temperature']
            else:
                min_temperature = 0.00
            self.read_datapoint = False
            self.datapoint_condition.notify_all()
        return min_temperature

    def getMaxTemperature(self) -> float:
        with self.datapoint_condition:
            while self.write_datapoint:
                self.datapoint_condition.wait()
            self.read_datapoint = True
            if len(self.datapoints) > 0:
                max_temperature = max(self.datapoints, key = lambda point : point['temperature'])['temperature']
            else:
                max_temperature = 0.00
            self.read_datapoint = False
            self.datapoint_condition.notify_all()
        return max_temperature

    def getAverageTemperature(self) -> float:
        with self.datapoint_condition:
            while self.write_datapoint:
                self.datapoint_condition.wait()
            self.read_datapoint = True
            average = self.temperatureAVG
            self.read_datapoint = False
            self.datapoint_condition.notify_all()
        return average

class WindowManager():
    def __init__(self):
        self.position:float = 0.00
        self.active_mode = Mode.AUTOMATIC
        self.window_condition = Condition()
        self.move_window:bool = False
        self.read_window:bool = False

        self.mode_condition = Condition()
        self.update_mode:bool = False
        self.read_mode:bool = False

    def move(self, position:float = 0.00) -> None:
        with self.window_condition:
            while self.read_window or self.move_window:
                self.window_condition.wait()
            self.move_window = True
            self.position = position
            self.move_window = False
            self.window_condition.notify_all()

    def get_position(self) -> float:
        with self.window_condition:
            while self.move_window:
                self.window_condition.wait()
            self.read_window = True
            position = self.position
            self.read_window = False
            self.window_condition.notify_all()
        return position

    def set_mode(self, mode:Mode) -> None:
        with self.mode_condition:
            while self.read_mode or self.update_mode:
                self.mode_condition.wait()
            self.update_mode = True
            self.active_mode = mode
            self.update_mode = False
            self.mode_condition.notify_all()

    def get_mode(self) -> Mode:
        with self.mode_condition:
            while self.update_mode:
                self.mode_condition.wait()
            self.read_mode = True
            active = self.active_mode
            self.read_mode = False
            self.mode_condition.notify_all()
        return active

    def check_mode(self, mode_to_check:Mode) -> bool:
        with self.mode_condition:
            while self.update_mode:
                self.mode_condition.wait()
            self.read_mode = True
            is_active = ( self.active_mode.value == mode_to_check.value )
            self.read_mode = False
            self.mode_condition.notify_all()
        return is_active

class StatusManager():
    TIME_TO_ALARM:float = 2.00
    FIRST_THRESHOLD:float = 27.00
    SECOND_THRESHOLD:float = 38.00
    THRESHOLD_RANGE:float = SECOND_THRESHOLD - FIRST_THRESHOLD

    def __init__(self):
        self.active:Status = Status.NORMAL
        self.condition:Condition = Condition()
        self.update_state:bool = False
        self.read_state:bool = False
        self.alarm_timer:Timer = Timer(wait_time=self.TIME_TO_ALARM)

    def adjust(self, temperature:float | None = None) -> None:
        if temperature is not None:
            with self.condition:
                while self.read_state or self.update_state:
                    self.condition.wait()
                self.update_state = True
                if self.active != Status.ALARM or not self.alarm_timer.is_set():
                    if self.alarm_timer.is_set():
                        self.alarm_timer.update()
                    if temperature < self.FIRST_THRESHOLD:
                        self.active = Status.NORMAL
                        self.alarm_timer.reset()
                    elif temperature >= self.FIRST_THRESHOLD and temperature <= self.SECOND_THRESHOLD:
                        self.active = Status.HOT
                        self.alarm_timer.reset()
                    elif temperature > self.SECOND_THRESHOLD and not self.alarm_timer.is_set():
                        self.active = Status.TOO_HOT
                        self.alarm_timer.set()
                    elif self.alarm_timer.is_over():
                        self.active = Status.ALARM
                self.update_state = False
                self.condition.notify_all()

    def fix_alarm(self) -> None:
        self.alarm_timer.reset()

    def get_active(self) -> Status:
        with self.condition:
            while self.update_state:
                self.condition.wait()
            self.read_state = True
            state = self.active
            self.read_state = False
            self.condition.notify_all()
        return state

    def set_state(self, new_state:Status) -> None:
        with self.condition:
            while self.read_state or self.update_state:
                self.condition.wait()
            self.update_state = True
            self.active = new_state
            self.update_state = False

