#include <Arduino.h>

#define GREEN_LED 15
#define RED_LED 2
#define TEMP_SENSOR 36

#define TEMPERATURE_AVERAGE_SIZE 100
int readingBuffer[TEMPERATURE_AVERAGE_SIZE] = {};
int writeIndex = 0;

void setup() {
    pinMode(GREEN_LED, OUTPUT);
    pinMode(RED_LED, OUTPUT);
    pinMode(TEMP_SENSOR, INPUT);
    Serial.begin(115200);
    //connect to mqtt
}

void pushReading(){
    //note that the ADC in esp32 is not perfectly linear, but we'll pretent it is
    readingBuffer[writeIndex] = analogRead(TEMP_SENSOR);
    writeIndex = (writeIndex + 1) % TEMPERATURE_AVERAGE_SIZE;
}

//the ADC is very, VERY noisy, so we take an average of the last N samples and use that as a value
int getAverageReading(){
    long sum = 0;
    for(int i = 0; i < TEMPERATURE_AVERAGE_SIZE; i++){
        sum += readingBuffer[i];
    }
    return sum / TEMPERATURE_AVERAGE_SIZE;
}

void loop() {
    pushReading();
    //We're using milliVolts because if we store as Volts then we have too much error from floating point
    float voltagemV = (float)getAverageReading() * 3300 / 4095;
    //TMP36 provides a 750mV output at 25°C
    //it has an output scale of 10mV / °C
    float temperature = (voltagemV - 750) / 10 + 25.0;

    Serial.print(voltagemV);
    Serial.print("\t|");
    Serial.println(temperature);
}
