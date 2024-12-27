from flask import Flask
from threading import Thread

class FlaskDeamon(Thread):
    httpserver:Flask = Flask(__name__)
    SERVER_PORT:int = 80
    SERVER_IP:str = '0.0.0.0'
    daemon = True

    @httpserver.route('/status')
    def send_temperature():
        return "temperatura e finestra"

    @httpserver.route('/history')
    def send_all_data():
        return "all"

    def run(self):
        self.httpserver.run(host=self.SERVER_IP, port=self.SERVER_PORT, debug=False)