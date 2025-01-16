from flask import Flask, jsonify, Response
from threading import Thread
from managers import *
from werkzeug.serving import make_server
import logging

'''
THINKING ABOUT USE DIRECTLY WERKZEUG SERVER INSTEAD OF FLASK, TO HAVE COMPLETE CONTROL ON SERVER BEHAVIOR.
FOR NOW ALL THE COMUNICATION COMPONENTS ARE IMPLEMENTED AS DEAMONS BUT IN FUTURE MAY BE CONVERTED TO NORMAL THREADS.
'''
class FlaskThread(Thread):
    def __init__(self, system_manager:Manager):
        super(FlaskThread, self).__init__()
        self.flask_app:Flask = Flask(__name__)
        # Disable flask logger
        logging.getLogger("werkzeug").disabled = True
        self.manager:Manager = system_manager
        self.flask_app.add_url_rule(rule="/status", endpoint="status", view_func=self.send_temperature)
        self.flask_app.add_url_rule(rule="/history", endpoint="history", view_func=self.send_all_data)
        self.flask_app.add_url_rule(rule="/isFree", endpoint="isFree", view_func=self.can_take_control)
        self.flask_app.add_url_rule(rule="/takeControl", endpoint="takeControl", view_func=self.take_control)
        self.flask_app.add_url_rule(rule="/releaseControl", endpoint="releaseControl", view_func=self.release_control)
        self.control_timer:Timer = Timer(wait_time=100)
        self.SERVER_IP:str = '0.0.0.0'
        self.SERVER_PORT:int = 80
        #self.daemon:bool = True
        self.server = make_server(host=self.SERVER_IP, port=self.SERVER_PORT, app=self.flask_app)

    def generate_cors_response(self, data="") -> Response:
        response = jsonify(message=data)
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    def send_temperature(self) -> Response:
        print("Flask Thread: Sending latest datapoint...")
        return self.generate_cors_response(data=self.manager.get_latest())

    def send_all_data(self) -> Response :
        print("Flask Thread: Sending datapoint history...")
        return self.generate_cors_response(data=self.manager.generate_history())

    def can_take_control(self) -> Response:
        print("Flask Thread: Received window control status request.")
        return self.generate_cors_response(data={"free": self.manager.check_if_active(Mode.AUTOMATIC)})

    def take_control(self) -> Response:
        if self.manager.check_if_active(Mode.AUTOMATIC):
            print("Flask Thread: Enabled remote control")
            self.manager.change_mode(Mode.REMOTE_MANUAL)
        print("Flask Thread: Request to remote control rejected.")
        return self.can_take_control()

    def release_control(self) -> Response:
        print("Flask Thread: Received release remote control request.")
        if not ( self.manager.check_if_active(Mode.AUTOMATIC) or self.manager.check_if_active(Mode.LOCAL_MANUAL) ):
            self.manager.change_mode(Mode.AUTOMATIC)
            return self.generate_cors_response(data=True) #TODO: Maybe change later
        return self.generate_cors_response(data=False) #TODO: Maybe change later


    def run(self):
        print("Flask Thread: Running...")
        self.server.serve_forever()

    def close(self):
        print("Flask Thread: Shutting down server...")
        self.server.shutdown()