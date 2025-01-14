from threading import Thread
from managers import Manager
import serial

class SerialThread(Thread):
    SERIALPORT = ""
    BAUDRATE = 9600

    def __init__(self, system_manager:Manager):
        super(SerialThread, self).__init__()
        self.manager:Manager = system_manager
        self.daemon = True
        self.running = True
        self.serial_line = serial.Serial(baudrate=self.BAUDRATE)
    def run(self):
        # Find a way to connect the serial port
        pass