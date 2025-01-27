from managers import Manager
from http_threads import *
from serial_threads import *
from mqtt_threads import *
import time
'''
    This is the main thread and the control-unit entry point that initialize, starts and close all other threads.
    -> The system manager will be passed in threads constructors and will be used to manage all common data safely.
    -> The Flask thread will manage HTTP communication between the control-unit and the web dashboard subsystem.
    -> The Serial thread will manage Serial communication between the control-unit and Arduino subsystem using RS232.
    -> The MQTT thread will manage communication via MQTT broker between control-unit and ESP32 subsystem.
'''
if __name__=="__main__":
    SERIAL_PORT:str = "COM5"
    SERIAL_BAUDRATE:int = 9600
    TUPDATE:float = 0.5
    manager:Manager = Manager(max_datapoints=20)          # Common manager initialization.
    flask_server = FlaskThread(system_manager=manager)    # Initialization of Flask thread.
    serial_connection = SerialThread(                     # Initialization of Serial Line thread.
        system_manager = manager,
        baudrate = SERIAL_BAUDRATE,
        port = SERIAL_PORT
    )
    mqtt_comunicator = MQTTThread(system_manager=manager) # Initialization of MQTT thread.
    # Main thread starts all communication threads
    mqtt_comunicator.start()
    flask_server.start()
    serial_connection.start()
    # Neverending loop that updates the manager and wait to external Keyboard Interrupt to end the execution.
    try:
        while True:
            time.sleep(TUPDATE)
            manager.update()
    except (KeyboardInterrupt, Exception):
        # Closing all threads and shutting down the main thread.
        print("Main Thread - Shutting down")
        flask_server.close()
        mqtt_comunicator.close()
        serial_connection.close()
        exit(0)