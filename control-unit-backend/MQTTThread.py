from threading import Thread
from managers import Manager
import paho.mqtt.client as mqtt

class MQTTThread(Thread):
    BROKER = "broker.hivemq.com"
    PORT = 1883
    def __init__(self, system_manager:Manager=None):
        super(MQTTThread, self).__init__()
        self.client = mqtt.Client(protocol=mqtt.MQTTv311)
        self.client.on_connect = self.establish_connection
        self.client.on_disconnect = self.destroy_connection
        self.daemon = True
        self.manager = system_manager

    def destroy_connection(client, userdata, flags, rc):
        print("MQTT Thread: Connection closed with message %d." % (rc))

    def establish_connection(client, userdata, flags, rc):
        print("MQTT Thread: Received CONNACK with code %d." % (rc))

    def run(self):
        self.client.connect(host=self.BROKER, port=self.PORT)

    def close(self):
        self.client.disconnect()