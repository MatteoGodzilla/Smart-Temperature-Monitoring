import ThreadLogics
import time

if __name__=="__main__":
    flask = ThreadLogics.FlaskThread()
    flask.daemon = True
    flask.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down control unit...")
        exit(0)