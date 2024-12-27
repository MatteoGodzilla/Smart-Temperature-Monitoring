from flask import Flask
from threading import Thread

class FlaskThread(Thread):

    def __init__(self):
        self.SERVER_PORT:int = 80
        self.SERVER_IP:str = '0.0.0.0'
        self.httpserver:Flask = Flask(__name__)

    @httpserver.route("/temperature")
    def main():
        return "temperatureeeeeeeee"

    @httpserver.route("/history")
    def main():
        return "storicooo"

    def run(self):
        self.httpserver.run(host=self.SERVER_IP, port=self.SERVER_PORT, debug=False)