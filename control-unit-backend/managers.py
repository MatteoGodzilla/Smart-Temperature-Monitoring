import time
import json
from timers import Timer
from system_enums import Mode, Status
from secondary_managers import WindowManager, TemperatureAccessManager, StatusManager

# TODO: CHECK IF UPDATE METHOD NEED THREAD CONDITION VARIABLES
class Manager():
    TIME_FREQUENCY:int = 1000
    FIRST_FREQUENCY:int = 1
    SECOND_FREQUENCY:int = 5

    NEXT_SAMPLE_STATUS:int = 500

    MAX_CONTROL_TIME:float = 60.00
    def __init__(self, max_datapoints:int=10):
        self.temperature_access:TemperatureAccessManager = TemperatureAccessManager(max_len=max_datapoints)
        self.control_timer:Timer = Timer(wait_time=self.MAX_CONTROL_TIME)
        self.window_controller:WindowManager = WindowManager()
        self.state_manager:StatusManager = StatusManager()

    # Writer (Thread MQTT) | Reader (Thread Flask).
    def get_latest(self) -> dict:
        if not self.temperature_access.is_empty():
            datapoint = self.temperature_access.get_datapoint(index=-1)
        else:
            # Generate a placeholder point
            datapoint = {"timestamp" : time.time(), "temperature" : 0.00, "window" : self.window_controller.get_position()}
        return {
            "status" : (self.state_manager.get_active()).value,             # Actual integer value of active FSM status
            "mode" : (self.window_controller.get_mode()).value,             # Actual control mode
            "datapoint" : datapoint,                                        # Latest datapoint inserted
            "maximum" : self.temperature_access.get_max_temperature(),      # Maximum temperature in memory
            "minimum" : self.temperature_access.get_min_temperature(),      # Minimum temperature in memory
            "average" : self.temperature_access.get_average_temperature(),  # Average temperature between all temperature values in memory
            "nextStatus" : self.NEXT_SAMPLE_STATUS,                         # Time to wait to send another request
            "maxDatapoints" : self.temperature_access.DATAPOINT_BUFFER_SIZE # Number of maximum datapoints collected in memory
        }

    # Writer (Thread MQTT) | Reader (Thread Flask).
    def generate_history(self) -> dict:
        if not self.temperature_access.is_empty():
            datapoints:list = list(self.temperature_access.get_datapoints())
        else:
            # Generate a placeholder list
            datapoints:list = [{"timestamp" : time.time(), "temperature" : 0.00, "window" : self.window_controller.get_position()}]
        return {
            "dataPoints" : datapoints,                                      # The datapoints list
            "minimum" : self.temperature_access.get_min_temperature(),      # Maximum temperature in memory
            "maximum" : self.temperature_access.get_max_temperature(),      # Minimum temperature in memory
            "average" : self.temperature_access.get_average_temperature()   # Average temperature between all temperature values in memory
        }

    def change_state(self, state:Status) -> None:
        self.state_manager.set_state(state)

    def get_state(self) -> Status:
        return self.state_manager.get_active()

    def change_mode(self, mode:Mode) -> None:
        if mode.value == Mode.AUTOMATIC.value:
            self.window_controller.set_mode(mode)
            self.control_timer.reset()
        elif (self.window_controller.check_mode(Mode.AUTOMATIC)) or (self.control_timer.is_over()):
            self.window_controller.set_mode(mode)
            self.control_timer.set()

    def alarm_fix(self) -> None:
        self.state_manager.fix_alarm()

    def get_mode(self) -> Mode:
        return self.window_controller.get_mode()

    def receive_temperature(self, data:float) -> None:
        self.temperature_access.enqueue_datapoint(
            timestamp = time.time(),                        # Datapoint reception timestamp (optional)
            temperature = data,                             # Received temperature
            window = self.window_controller.get_position()  # Actual Window opening percentage
        )
        self.state_manager.adjust(self.temperature_access.get_datapoint(index=-1)["temperature"])

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
            match self.state_manager.get_active().value:
                case Status.NORMAL.value:
                    self.window_controller.move(0.00)
                case Status.HOT.value:
                    last_temperature = self.temperature_access.get_datapoint(index=-1)["temperature"]
                    if last_temperature != self.state_manager.FIRST_THRESHOLD:
                        delay_from_min = last_temperature - self.state_manager.FIRST_THRESHOLD
                        new_percentage = delay_from_min / self.state_manager.THRESHOLD_RANGE
                        self.window_controller.move(new_percentage)
                    else:
                        self.window_controller.move(0.01)
                case Status.TOO_HOT.value:
                    self.window_controller.move(1.00)
