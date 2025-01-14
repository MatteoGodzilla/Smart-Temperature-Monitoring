from flask import Flask, jsonify
import logging
from threading import Thread
from managers import Manager
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
        self.SERVER_IP:str = '0.0.0.0'
        self.SERVER_PORT:int = 80
        self.daemon:bool = True

    def generate_cors_response(self, data=""):
        response = jsonify(message=data)
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    def send_temperature(self):
        return self.generate_cors_response(data=self.manager.getLatest())

    def send_all_data(self):
        return self.generate_cors_response(data=self.manager.generateHistory())

    def run(self):
        self.httpserver.run(host=self.SERVER_IP, port=self.SERVER_PORT, debug=False)