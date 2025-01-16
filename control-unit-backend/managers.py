import time
import json
from timers import Timer
from system_enums import Mode, Status
from secondary_managers import WindowManager, TemperatureAccessManager, StatusManager

'''
TODO:
    -> MANAGE RACE CONDITIONS BETWEEN WRITERS-READERS.
    -> ADD LOGIC TO MANAGE:
        -> AUTOMATIC (based on temperature change status, calculate new percentage and send it on Serial Thread)
        -> REMOTE MANUAL CONTROL (read from dashboard and send on Serial Thread)
        -> LOCAL MANUAL CONTROL (only listen and save new percentage)
    -> FINISH IMPLEMENTATION OF THE MANAGERS.
'''
class Manager():
    def __init__(self, max_datapoints=5):
        # Constants
        self.TIME_FREQUENCY:int = 1000
        self.FIRST_FREQUENCY:int = 4
        self.SECOND_FREQUENCY:int = 8

        self.MAX_CONTROL_TIME:float = 60.00

        # Variables
        self.alarm_timer:Timer = Timer(wait_time=self.TIME_TO_ALARM)
        self.control_timer:Timer = Timer(wait_time=self.MAX_CONTROL_TIME)
        self.actual_state:Status = Status.NORMAL
        self.window_controller:WindowManager = WindowManager()
        self.state_manager:StatusManager = StatusManager()
        self.temperature_access:TemperatureAccessManager = TemperatureAccessManager(max_len=max_datapoints)

    # Writer (Thread MQTT) | Reader (Thread Flask).
    def get_latest(self) -> dict:
        return {
            "status" : self.actual_state.value,                           # Actual integer value of active FSM status
            "mode" : (self.window_controller.get_mode()).value,           # Actual control mode
            "datapoint" : self.temperature_access.getDataPoint(index=-1), # Latest datapoint inserted
            "nextStatus" : 100                                            # Time to wait to send another request - MAYBE ADD LOGIC BEHIND THIS VALUE
        }

    # Writer (Thread MQTT) | Reader (Thread Flask).
    def generate_history(self) -> dict:
        return {
            "dataPoints" : list(self.temperature_access.getDataPoints()), # The datapoints list
            "minimum" : self.temperature_access.getMinTemperature(),      # Maximum temperature in memory
            "maximum" : self.temperature_access.getMaxTemperature(),      # Minimum temperature in memory
            "average" : self.temperature_access.getAverageTemperature()   # Average temperature between all temperature values in memory
        }

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
        self.state_manager.adjust(self.temperature_access.getDataPoint(index=-1))

    def receive_opening_percentage(self, percentage:float = 0.00) -> None:
        if self.window_controller.check_mode(Mode.LOCAL_MANUAL) or self.window_controller.check_mode(Mode.REMOTE_MANUAL):
            self.window_controller.move(percentage)

    def get_opening_percentage(self) -> float:
        return self.window_controller.get_position()

    def check_if_active(self, mode:Mode) -> bool:
        return self.window_controller.check_mode(mode_to_check=mode)

    def check_and_fix_control(self) -> None:
        if self.control_timer.is_set():
            self.control_timer.update()
            if self.control_timer.is_over():
                self.control_timer.reset()
                self.window_controller.set_mode(Mode.AUTOMATIC)

    def get_mqtt_frequency_packed(self) -> dict:
        match self.state_manager.get_active().value:
            case Status.NORMAL.value:
                return json.dumps({"nextSample": int(self.TIME_FREQUENCY / self.FIRST_FREQUENCY)})
            case Status.HOT.value | Status.TOO_HOT.value:
                return json.dumps({"nextSample": int(self.TIME_FREQUENCY / self.SECOND_FREQUENCY)})

    def update(self) -> None:
        self.check_and_fix_control()
        if self.window_controller.check_mode(Mode.AUTOMATIC):
            match self.actual_state.value:
                case Status.NORMAL.value:
                    self.window_controller.move(0.00)
                case Status.HOT.value:
                    last_temperature = self.temperature_access.getDataPoint(index=-1)["temperature"]
                    if last_temperature != self.FIRST_THRESHOLD:
                        delay_from_min = last_temperature - self.FIRST_THRESHOLD
                        new_percentage = delay_from_min / self.THRESHOLD_RANGE
                        self.window_controller.move(new_percentage)
                    else:
                        self.window_controller.move(0.01)
                case Status.TOO_HOT.value:
                    self.window_controller.move(1.00)
