#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>

#include "credentials.h"
#include "temperature.h"

#define GREEN_LED 15
#define RED_LED 2
//TEMP_SENSOR_GPIO AND TEMP_SENSOR_ADC_CHANNEL MUST REFER TO THE SAME
#define TEMP_SENSOR_GPIO 36
#define TEMP_SENSOR_ADC_CHANNEL ADC_CHANNEL_0

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

void loop() {
    if(!client.connected()){
        digitalWrite(RED_LED, HIGH);
        digitalWrite(GREEN_LED, LOW);

        if(!client.connect(CLIENT_NAME)){
            //there was an error
            Serial.println("Connection to MQTT Broker failed!");
            Serial.println(client.state());
            delay(5000);
        }
    } else {
        digitalWrite(RED_LED, LOW);
        digitalWrite(GREEN_LED, HIGH);

        Temperature::pushReading();

        long now = millis();
        if(now - lastPush > nextSample){
            double temperature = Temperature::getAverageTemperature();
            //send through mqtt
            //Serial.println(temperature);
            lastPush = now;
        }

    }
}
