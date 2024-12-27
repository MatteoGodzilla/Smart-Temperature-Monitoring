import deamons
import time

if __name__=="__main__":
    flask = deamons.FlaskDeamon()
    flask.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down control unit...")
        exit(0)