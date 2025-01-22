from flask import Flask, jsonify, Response, request
from threading import Thread
from managers import *
from werkzeug.serving import BaseWSGIServer, make_server
import logging
import flask_cors

class FlaskThread(Thread):
    def __init__(self, system_manager:Manager):
        super(FlaskThread, self).__init__()
        self.flask_app:Flask = Flask(__name__)
        flask_cors.CORS(self.flask_app)
        # Disable flask logger
        logging.getLogger("werkzeug").disabled = True
        self.manager:Manager = system_manager
        self.flask_app.add_url_rule(rule="/api/status", view_func=self.send_temperature)
        self.flask_app.add_url_rule(rule="/api/history", view_func=self.send_all_data)
        self.flask_app.add_url_rule(rule="/api/isFree", view_func=self.can_take_control)
        self.flask_app.add_url_rule(rule="/api/takeControl", view_func=self.take_control)
        self.flask_app.add_url_rule(rule="/api/control", view_func=self.control_action, methods=["POST"])
        self.flask_app.add_url_rule(rule="/api/fixAlarm", view_func=self.manage_alarm)
        self.flask_app.add_url_rule(rule="/api/releaseControl", view_func=self.release_control)
        self.control_timer:Timer = Timer(wait_time=100)
        self.SERVER_IP:str = '0.0.0.0'
        self.SERVER_PORT:int = 80
        self.server:BaseWSGIServer = make_server(host=self.SERVER_IP, port=self.SERVER_PORT, app=self.flask_app)

    def generate_cors_response(self, data="") -> Response:
        response = jsonify(message=data)
        #response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    def send_temperature(self) -> Response:
        print("Flask Thread - Sending latest datapoint...")
        return self.generate_cors_response(data=self.manager.get_latest())

    def send_all_data(self) -> Response :
        print("Flask Thread - Sending datapoint history...")
        return self.generate_cors_response(data=self.manager.generate_history())

    def can_take_control(self) -> Response:
        print("Flask Thread - Received window control status request.")
        return self.generate_cors_response(data={"free": self.manager.check_if_active(Mode.AUTOMATIC)})

    def control_action(self) -> Response:
        try:
            if self.manager.check_if_active(Mode.REMOTE_MANUAL):
                print("Flask Thread - Control command received: ", request.get_json(force=True))
            else:
                print("Flask Thread - Control command ignored, the control unit is not in REMOTE MANUAL mode.")
            return self.generate_cors_response(data=True)
        except Exception:
            print("Flask Thread - Received something unusual on api/control: ", request.get_json(force=True))
            return self.generate_cors_response(data=False)


    def manage_alarm(self) -> Response:
        print("Flask Thread - Fixing alarm.")
        self.manager.alarm_fix()
        return self.generate_cors_response()

    def take_control(self) -> Response:
        if self.manager.check_if_active(Mode.AUTOMATIC):
            print("Flask Thread - Enabled remote control")
            self.manager.change_mode(Mode.REMOTE_MANUAL)
            return self.generate_cors_response(data=True)
        else:
            print("Flask Thread - Request to remote control rejected.")
            return self.generate_cors_response(data=False)

    def release_control(self) -> Response:
        print("Flask Thread - Received release remote control request.")
        if not ( self.manager.check_if_active(Mode.AUTOMATIC) or self.manager.check_if_active(Mode.LOCAL_MANUAL) ):
            self.manager.change_mode(Mode.AUTOMATIC)
            return self.generate_cors_response(data=True)
        return self.generate_cors_response(data=False)


    def run(self):
        print("Flask Thread - Running...")
        self.server.serve_forever()

    def close(self):
        print("Flask Thread - Shutting down server...")
        self.server.shutdown()