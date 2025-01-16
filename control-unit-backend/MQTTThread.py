from threading import Thread
from managers import Manager
import paho.mqtt.client as mqtt
import json

class MQTTThread(Thread):
    BROKER = "broker.hivemq.com"
    TOPIC = "assignment03/temp-system"
    PORT = 1883
    def __init__(self, system_manager:Manager=None):
        super(MQTTThread, self).__init__()
        self.client = mqtt.Client(protocol=mqtt.MQTTv311)
        self.client.on_connect = self.establish_connection
        self.client.on_disconnect = self.destroy_connection
        self.client.on_message = self.receive_message
        self.client.on_subscribe = self.topic_subscribe
        self.client.on_publish = self.publish
        self.daemon = True
        self.running = True
        self.manager = system_manager

    def destroy_connection(self, userdata, flags, rc):
        print("MQTT Thread: Connection closed with code %d." % (rc))

    def establish_connection(self, client, userdata, flags, rc):
        print("MQTT Thread: Received CONNACK with code %d." % (rc))

    def receive_message(self, client, userdata, message:mqtt.MQTTMessage):
        fixed_payload = json.loads(str(message.payload))
        print("MQTT Thread: Received new message ", fixed_payload,
            " on topic ", message.topic,
            " with QoS ", str(message.qos))
        print("MQTT Thread: Sending next sample message on topic.")
        self.manager.receive_temperature(fixed_payload["temperature"])
        self.client.publish(self.TOPIC, self.manager.get_mqtt_frequency_packed())


    def topic_subscribe(self, client, userdata, mid, granted_qos):
        print("MQTT Thread: Successfully subscribed on topic.")

    def publish(self, client, userdata, mid, reason_code):
        print("MQTT Thread: Publishing message with frequency.")


    def run(self):
        self.client.connect(host=self.BROKER, port=self.PORT)
        while self.running:
            self.client.loop_forever(timeout=1)

    def close(self):
        self.running = False
        self.client.disconnect()