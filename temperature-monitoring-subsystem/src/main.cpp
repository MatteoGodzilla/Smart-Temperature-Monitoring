#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

#include "credentials.h"
#include "temperature.h"

#define GREEN_LED 15
#define RED_LED 2
//TEMP_SENSOR_GPIO AND TEMP_SENSOR_ADC_CHANNEL MUST REFER TO THE SAME
#define TEMP_SENSOR_GPIO 36
#define TEMP_SENSOR_ADC_CHANNEL ADC_CHANNEL_0

#define JSON_OUTPUT_MAX_SIZE 30

WiFiClient espClient;
PubSubClient client(espClient);

long lastPush;
long nextSample = 3000;

void setup() {
    pinMode(GREEN_LED, OUTPUT);
    pinMode(RED_LED, OUTPUT);
    pinMode(TEMP_SENSOR_GPIO, INPUT);
    Serial.begin(115200);

    Temperature::init(TEMP_SENSOR_GPIO, TEMP_SENSOR_ADC_CHANNEL);

    digitalWrite(GREEN_LED, LOW);
    digitalWrite(RED_LED, HIGH);

    //connect to mqtt
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    while(WiFi.status() != WL_CONNECTED){
        delay(500);
        Serial.print(".");
    }

    //we can assume from this point on that wifi is already connected

    client.setServer(MQTT_BROKER, MQTT_PORT);
    lastPush = millis();
}

void receivingCallback(const char topic[], byte* payload, unsigned int length){
    // a message has been received, assume it's a json string
    JsonDocument doc;
    DeserializationError error = deserializeJson(doc, payload);

    if(!error){
        nextSample = doc["nextSample"];
        Serial.print("Received message, changed nextSample to ");
        Serial.println(nextSample);
    }
}

void loop() {
    if(!client.connected()){
        digitalWrite(RED_LED, HIGH);
        digitalWrite(GREEN_LED, LOW);

        if(!client.connect(CLIENT_NAME)){
            //there was an error
            Serial.println("Connection to MQTT Broker failed!");
            Serial.println(client.state());
            delay(5000);
        } else {
            client.setCallback(receivingCallback);
            client.subscribe(SUBSCRIBE_TOPIC);
        }
    } else {
        client.loop();
        digitalWrite(RED_LED, LOW);
        digitalWrite(GREEN_LED, HIGH);

        Temperature::pushReading();

        long now = millis();
        if(now - lastPush > nextSample){
            //send through mqtt
            char output[JSON_OUTPUT_MAX_SIZE];
            double temperature = Temperature::getAverageTemperature();;
            JsonDocument doc;
            doc["temperature"] = temperature;
            serializeJson(doc, output, JSON_OUTPUT_MAX_SIZE);
            client.publish(PUBLISH_TOPIC, output);

            Serial.println(temperature);
            lastPush = now;
        }

    }
}
