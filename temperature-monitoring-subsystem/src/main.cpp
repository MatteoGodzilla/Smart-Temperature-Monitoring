#include <Arduino.h>

#define GREEN_LED 15
#define RED_LED 4
#define TEMP_SENSOR 1

void setup() {
    pinMode(GREEN_LED, OUTPUT);
    pinMode(RED_LED, OUTPUT);
    pinMode(TEMP_SENSOR, INPUT);
    Serial.begin(115200);
}

void loop() {
    if(Serial){
        digitalWrite(GREEN_LED, HIGH);
        digitalWrite(RED_LED, LOW);
        Serial.println("aaaa");
        Serial.flush();
    } else {
        digitalWrite(GREEN_LED, LOW);
        digitalWrite(RED_LED, HIGH);
    }
}
