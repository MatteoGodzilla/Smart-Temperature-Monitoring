from managers import Manager
import deamons
import time

if __name__=="__main__":
    manager:Manager = Manager(max_datapoints=200)
    flask = deamons.FlaskDeamon(system_manager=manager)
    flask.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down control unit...")
        exit(0)