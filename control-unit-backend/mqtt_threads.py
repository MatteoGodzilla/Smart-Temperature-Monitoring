from threading import Thread
from managers import Manager
import paho.mqtt.client as mqtt
import json

class MQTTThread(Thread):
    BROKER = "broker.hivemq.com"
    TEMPERATURE_TOPIC = "assignment03/temperature"
    FREQUENCY_TOPIC = "assignment03/nextSample"
    PORT = 1883
    def __init__(self, system_manager:Manager=None):
        super(MQTTThread, self).__init__()
        self.client = mqtt.Client(protocol=mqtt.MQTTv311)
        self.client.on_connect = self.establish_connection
        self.client.on_disconnect = self.destroy_connection
        self.client.on_message = self.receive_message
        self.client.on_subscribe = self.topic_subscribe
        self.client.on_publish = self.publish_on_topic
        self.running = True
        self.manager = system_manager

    def destroy_connection(self, userdata, flags, rc):
        print("MQTT Thread - Connection closed with code %d." % (rc))

    def establish_connection(self, client, userdata, flags, rc):
        print("MQTT Thread - Successfully connected, received CONNACK with code %d." % (rc))
        self.client.subscribe(topic=self.TEMPERATURE_TOPIC)
        self.client.subscribe(topic=self.FREQUENCY_TOPIC)

    def receive_message(self, client, userdata, message:mqtt.MQTTMessage):
        fixed_payload:dict = json.loads((message.payload).decode("utf-8"))
        try:
            print("MQTT Thread - Received new message: ", fixed_payload,
                " on topic:", message.topic,
                " with QoS:", str(message.qos))
            print("MQTT Thread - Sending next sample message on topic.")
            self.manager.receive_temperature(fixed_payload["temperature"])
            self.client.publish(self.FREQUENCY_TOPIC, self.manager.get_mqtt_frequency_packed())
        except (KeyError, UnicodeDecodeError, ValueError):
            print("MQTT Thread - Ignored received message.")

    def topic_subscribe(self, client, userdata, mid, granted_qos):
        print("MQTT Thread - Successfully subscribed on topic.")

    def publish_on_topic(self, client, userdata, mid):
        print("MQTT Thread - Publishing message with frequency.")


    def run(self):
        self.client.connect(host=self.BROKER, port=self.PORT)
        while self.running:
            self.client.loop_forever(timeout=1)

    def close(self):
        self.running = False
        self.client.disconnect()