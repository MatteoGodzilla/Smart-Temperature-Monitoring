from managers import Manager
from FlaskThread import *
from SerialThread import *
from MQTTThread import *
import time

if __name__=="__main__":
    manager:Manager = Manager(max_datapoints=200)
    flask_server = FlaskDaemon(system_manager=manager)
    #serial_connection = SerialThread(system_manager=manager)
    mqtt_comunicator = MQTTThread(system_manager=manager)
    flask_server.start()
    #serial_connection.start()
    mqtt_comunicator.start()
    try:
        while True:
            time.sleep(1)
            # qui volendo si inserirebbe una chiamata di update situation ai vari thread
    except KeyboardInterrupt:
        print("Main Thread: Shutting down")
        mqtt_comunicator.close()
        exit(0)