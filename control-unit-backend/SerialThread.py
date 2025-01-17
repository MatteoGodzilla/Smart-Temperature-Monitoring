from threading import Thread
from managers import *
import serial

class SerialThread(Thread):
    SERIALPORT = "COM3" # TODO: INSERT A VALID PORT
    BAUDRATE = 9600

    def __init__(self, system_manager:Manager):
        super(SerialThread, self).__init__()
        self.manager:Manager = system_manager
        #self.daemon = True
        self.running = True
        try:
            self.serial_line = serial.Serial(baudrate=self.BAUDRATE, port=self.SERIALPORT)
            self.serial_line.close()
        except serial.SerialException:
            self.serial_line = serial.Serial()
            self.serial_line.port = self.SERIALPORT
            self.serial_line.baudrate = self.BAUDRATE
            self.serial_line.close()


    def run(self):
        try:
            self.serial_line.open()
            while self.running:
                if self.serial_line.in_waiting > 0:
                    message = self.serial_line.read_until(expected=b";").strip().decode("utf-8")
                    print("Serial Thread - Reading from serial line: ", message)
                    try:
                        match message[0:2]:
                            case "P:":
                                    print("Serial Thread - Received window opening percentage: ", message[2:-1])
                                    if self.manager.get_mode() == Mode.LOCAL_MANUAL:
                                        print("Serial Thread - LOCAL MANUAL mode is active, modifying opening percentage")
                                        received_percentage = float(message[2:-1])
                                        self.manager.receive_opening_percentage(received_percentage)
                                    else:
                                        print("Serial Thread - Received percentage ignored because the FSM is not in LOCAL MANUAL mode")
                            case "S:":
                                if int(message[2:-1]) == Mode.LOCAL_MANUAL.value and not self.manager.check_if_active(Mode.REMOTE_MANUAL):
                                        print("Serial Thread - Received FSM LOCAL MANUAL Mode request from Arduino: ", message[2:-1])
                                        self.manager.change_mode(mode=Mode.LOCAL_MANUAL)
                                else:
                                        print("Serial Thread - Received FSM AUTOMATIC Mode request from Arduino: ", message[2:-1])
                                        self.manager.change_mode(mode=Mode.AUTOMATIC)
                            case _:
                                print("Serial Thread - Received something unusual: ", message)
                    except IndexError:
                        print("Serial Thread - Received some bytes, nothing useful")

                if self.manager.get_mode().value == Mode.LOCAL_MANUAL.value:
                    msg_temperature = "T:%.2f;" % float(self.manager.get_latest()["datapoint"]["temperature"])
                    self.serial_line.write(msg_temperature.encode("utf-8").strip())
                    self.serial_line.flush()
                else:
                    msg_percentage = "P:%.2f;" % float(self.manager.get_opening_percentage())
                    self.serial_line.write(msg_percentage.encode("utf-8").strip())
                    self.serial_line.flush()
                print("Serial Thread - Sending data")
                msg_mode = "S:" + str((self.manager.get_mode()).value) + ";"
                self.serial_line.write(msg_mode.encode("utf-8").strip())
                self.serial_line.flush()
            print("Serial Thread - Closed")
        except (Exception, serial.SerialException, FileNotFoundError) as exception:
                print("Critical problem encountered on Serial Thread: ", exception)
                print("Serial Thread - Closed")

    def close(self):
         self.running = False
         self.serial_line.close()