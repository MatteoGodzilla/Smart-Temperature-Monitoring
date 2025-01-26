from werkzeug.serving import BaseWSGIServer, make_server
from flask import Flask, jsonify, Response, request
from threading import Thread
from managers import *
import flask_cors
import logging

class FlaskThread(Thread):
    def __init__(self, system_manager:Manager):
        super(FlaskThread, self).__init__()
        self.flask_app:Flask = Flask(__name__)
        flask_cors.CORS(self.flask_app)
        # Disable flask logger
        logging.getLogger("werkzeug").disabled = True
        self.manager:Manager = system_manager
        self.flask_app.add_url_rule(rule="/api/status", view_func=self.send_latest_datapoint)
        self.flask_app.add_url_rule(rule="/api/history", view_func=self.send_datapoints_history)
        self.flask_app.add_url_rule(rule="/api/isFree", view_func=self.is_free_from_control)
        self.flask_app.add_url_rule(rule="/api/takeControl", view_func=self.take_control)
        self.flask_app.add_url_rule(rule="/api/releaseControl", view_func=self.release_control)
        self.flask_app.add_url_rule(rule="/api/control", view_func=self.execute_control_action, methods=["POST"])
        self.flask_app.add_url_rule(rule="/api/fixAlarm", view_func=self.manage_alarm)
        self.control_timer:Timer = Timer(wait_time=100)
        self.SERVER_IP:str = '0.0.0.0'
        self.SERVER_PORT:int = 80
        self.server:BaseWSGIServer = make_server(host=self.SERVER_IP, port=self.SERVER_PORT, app=self.flask_app)

    def generate_response(self, data="") -> Response:
        response = jsonify(message=data)
        return response

    def send_latest_datapoint(self) -> Response:
        print("Flask Thread - Sending latest datapoint...")
        return self.generate_response(data=self.manager.get_latest())

    def send_datapoints_history(self) -> Response :
        print("Flask Thread - Sending datapoint history...")
        return self.generate_response(data=self.manager.generate_history())

    def is_free_from_control(self) -> Response:
        print("Flask Thread - Received window control status request.")
        return self.generate_response(data={"free": self.manager.check_if_active(Mode.AUTOMATIC)})

    def execute_control_action(self) -> Response:
        try:
            if self.manager.check_if_active(Mode.REMOTE_MANUAL):
                post_data = request.get_json(force=True)
                print("Flask Thread - Control command received: ", post_data)
                self.manager.receive_opening_percentage(percentage=post_data["position"])
            else:
                print("Flask Thread - Control command received but ignored, the control unit is not in REMOTE MANUAL mode.")
            return self.generate_response(data=True)
        except Exception:
            print("Flask Thread - Received something unusual on api/control: ", request.get_json(force=True))
            return self.generate_response(data=False)

    def manage_alarm(self) -> Response:
        print("Flask Thread - Deactivating alarm.")
        self.manager.alarm_fix()
        return self.generate_response()

    def take_control(self) -> Response:
        if self.manager.check_if_active(Mode.AUTOMATIC):
            print("Flask Thread - Enabled remote control")
            self.manager.change_mode(Mode.REMOTE_MANUAL)
            return self.generate_response(data=True)
        else:
            print("Flask Thread - Request to remote control rejected.")
            return self.generate_response(data=False)

    def release_control(self) -> Response:
        print("Flask Thread - Received release remote control request.")
        if self.manager.check_if_active(Mode.REMOTE_MANUAL):
            self.manager.change_mode(Mode.AUTOMATIC)
            return self.generate_response(data=True)
        else:
            return self.generate_response(data=False)

    def run(self):
        print("Flask Thread - Running...")
        self.server.serve_forever()

    def close(self):
        print("Flask Thread - Shutting down server...")
        self.server.shutdown()