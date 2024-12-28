from managers import AccessManager
import deamons
import time

if __name__=="__main__":
    manager:AccessManager = AccessManager(max_len=200)
    flask = deamons.FlaskDeamon(data_manager=manager)
    flask.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down control unit...")
        exit(0)