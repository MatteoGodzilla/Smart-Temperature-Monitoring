import json
from flask import Flask
from threading import Thread
from managers import Manager
'''
THINKING ABOUT USE DIRECTLY WERKZEUG SERVER INSTEAD OF FLASK, TO HAVE COMPLETE CONTROL ON SERVER BEHAVIOR.
FOR NOW ALL THE COMUNICATION COMPONENTS ARE IMPLEMENTED AS DEAMONS BUT IN FUTURE MAY BE CONVERTED TO NORMAL THREADS.
'''
class FlaskDeamon(Thread):
    def __init__(self, system_manager:Manager):
        super(FlaskDeamon, self).__init__()
        self.httpserver:Flask = Flask(__name__)
        self.manager:Manager = system_manager
        self.httpserver.add_url_rule(rule="/status", endpoint="status", view_func=self.send_temperature)
        self.httpserver.add_url_rule(rule="/history", endpoint="history", view_func=self.send_all_data)
        self.SERVER_IP:str = '0.0.0.0'
        self.SERVER_PORT:int = 80
        self.daemon:bool = True

    def send_temperature(self):
        return json.dumps(self.manager.getLatest())

    def send_all_data(self):
        return json.dumps(self.manager.generateHistory())

    def run(self):
        self.httpserver.run(host=self.SERVER_IP, port=self.SERVER_PORT, debug=False)