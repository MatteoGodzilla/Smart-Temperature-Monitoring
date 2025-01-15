from flask import Flask, jsonify, Response
import logging
from threading import Thread
from managers import *
'''
THINKING ABOUT USE DIRECTLY WERKZEUG SERVER INSTEAD OF FLASK, TO HAVE COMPLETE CONTROL ON SERVER BEHAVIOR.
FOR NOW ALL THE COMUNICATION COMPONENTS ARE IMPLEMENTED AS DEAMONS BUT IN FUTURE MAY BE CONVERTED TO NORMAL THREADS.
'''
class FlaskDaemon(Thread):
    def __init__(self, system_manager:Manager):
        super(FlaskDaemon, self).__init__()
        self.httpserver:Flask = Flask(__name__)
        # Disable flask logger
        logging.getLogger("werkzeug").disabled = True
        self.manager:Manager = system_manager
        self.httpserver.add_url_rule(rule="/status", endpoint="status", view_func=self.send_temperature)
        self.httpserver.add_url_rule(rule="/history", endpoint="history", view_func=self.send_all_data)
        self.httpserver.add_url_rule(rule="/isFree", endpoint="isFree", view_func=self.can_take_control)
        self.httpserver.add_url_rule(rule="/takeControl", endpoint="takeControl", view_func=self.take_control)
        self.httpserver.add_url_rule(rule="/releaseControl", endpoint="releaseControl", view_func=self.release_control)
        self.control_timer:Timer = Timer(wait_time=100)
        self.SERVER_IP:str = '0.0.0.0'
        self.SERVER_PORT:int = 80
        self.daemon:bool = True

    def generate_cors_response(self, data="") -> Response:
        response = jsonify(message=data)
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    def send_temperature(self) -> Response:
        return self.generate_cors_response(data=self.manager.getLatest())

    def send_all_data(self) -> Response :
        return self.generate_cors_response(data=self.manager.generateHistory())

    def can_take_control(self) -> Response:
        return self.generate_cors_response(data={"free": self.manager.check_if_active(Mode.AUTOMATIC)})

    def take_control(self) -> Response:
        if self.manager.check_if_active(Mode.AUTOMATIC):
            self.manager.change_mode(Mode.REMOTE_MANUAL)
        return self.can_take_control()

    def release_control(self) -> None:
        if not ( self.manager.check_if_active(Mode.AUTOMATIC) or self.manager.check_if_active(Mode.LOCAL_MANUAL) ):
            self.manager.change_mode(Mode.AUTOMATIC)

    def run(self):
        self.httpserver.run(host=self.SERVER_IP, port=self.SERVER_PORT, debug=False)