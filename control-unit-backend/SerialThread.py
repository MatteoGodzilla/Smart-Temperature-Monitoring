from threading import Thread
from managers import *
import serial

class SerialThread(Thread):
    SERIALPORT = "COM" # TODO: INSERT A VALID PORT
    BAUDRATE = 9600

    def __init__(self, system_manager:Manager):
        super(SerialThread, self).__init__()
        self.manager:Manager = system_manager
        #self.daemon = True
        self.running = True
        try:
            self.serial_line = serial.Serial(baudrate=self.BAUDRATE, port=self.SERIALPORT)
        except serial.SerialException:
             self.serial_line = serial.Serial()
             self.serial_line.port = self.SERIALPORT
             self.serial_line.baudrate = self.BAUDRATE

    def run(self):
        try:
            self.serial_line.open()
            while self.running: # TODO: Probably is necessary to decide every loop if read or write on serial line
                print("Serial Thread: Sending data...")
                msg_percentage = "P: %8.2f" % (self.manager.get_opening_percentage())
                self.serial_line.write(msg_percentage.encode("utf-8"))
                if self.manager.get_mode() == Mode.LOCAL_MANUAL:
                    msg_temperature = "T: %8.2f" % (self.manager.getLatest()["datapoint"]["temperature"])
                    self.serial_line.write(msg_temperature.encode("utf-8"))
                print("Serial Thread: Reading from serial line...")
                message = self.serial_line.read_until(expected=b";").decode("utf-8")
                try:
                    match message[0:2]:
                        case "P:":
                                print("Serial Thread: Received window opening percentage: ", message[2:])
                                if self.manager.get_mode() == Mode.LOCAL_MANUAL:
                                    print("Serial Thread: LOCAL MANUAL mode is active, modifying opening percentage")
                                    received_percentage = float(message[2:])
                                    self.manager.receive_opening_percentage(received_percentage)
                                else:
                                    print("Serial Thread: Received percentage ignored because the FSM is not in LOCAL MANUAL mode")
                        case "S:":
                            print("Serial Thread: Received FSM LOCAL MANUAL Mode request from Arduino: ", message[2:])
                            if message[2:] == "MANUAL":
                                    received_mode = Mode.LOCAL_MANUAL
                            else:
                                    received_mode = Mode.AUTOMATIC
                            self.manager.change_mode(mode=received_mode)
                        case _:
                            print("Serial Thread: Received something unusual: ", message[2:])
                except IndexError:
                     print("Serial Thread: Received some bytes, nothing useful")
            print("Serial Thread: Closed")
        except (Exception, serial.SerialException, FileNotFoundError) as exception:
                print("Serial Thread: The serial connection has encountered a critical problem.\n", exception)

    def close(self):
         self.running = False