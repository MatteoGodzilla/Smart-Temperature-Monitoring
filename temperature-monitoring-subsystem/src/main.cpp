#include <Arduino.h>
#include "esp_adc_cal.h"

#define GREEN_LED 15
#define RED_LED 2
//TEMP_SENSOR_GPIO AND TEMP_SENSOR_ADC_CHANNEL MUST REFER TO THE SAME
#define TEMP_SENSOR_GPIO 36
#define TEMP_SENSOR_ADC_CHANNEL ADC_CHANNEL_0
//the code is written to use ADC1, because we also have to use the wifi module, which conflicts with ADC2

esp_adc_cal_characteristics_t adcCurve;

#define TEMPERATURE_AVERAGE_SIZE 100
uint32_t readingBuffer[TEMPERATURE_AVERAGE_SIZE] = {};
int writeIndex = 0;

void setup() {
    pinMode(GREEN_LED, OUTPUT);
    pinMode(RED_LED, OUTPUT);
    pinMode(TEMP_SENSOR_GPIO, INPUT);
    Serial.begin(115200);
    //setup adc curve
    analogSetPinAttenuation(TEMP_SENSOR_GPIO, ADC_11db);
    esp_adc_cal_value_t returnType = esp_adc_cal_characterize(ADC_UNIT_1, ADC_ATTEN_DB_12, ADC_WIDTH_BIT_12, ESP_ADC_CAL_VAL_EFUSE_VREF, &adcCurve);
    //connect to mqtt
}

void pushReading(){
    //note that the ADC in esp32 is not perfectly linear, but we'll pretent it is
    uint32_t voltagemV;
    esp_adc_cal_get_voltage(TEMP_SENSOR_ADC_CHANNEL, &adcCurve, &voltagemV);
    readingBuffer[writeIndex] = voltagemV;
    writeIndex = (writeIndex + 1) % TEMPERATURE_AVERAGE_SIZE;
}

//the ADC is very, VERY noisy, so we take an average of the last N samples and use that as a value
double getAverageReading(){
    double sum = 0;
    for(int i = 0; i < TEMPERATURE_AVERAGE_SIZE; i++){
        sum += readingBuffer[i];
    }
    return sum / TEMPERATURE_AVERAGE_SIZE;
}

void loop() {
    pushReading();
    double voltagemV = getAverageReading();
    //TMP36 provides a 750mV output at 25°C
    //it has an output scale of 10mV / °C
    double temperature = (voltagemV - 750.0) / 10 + 25.0;

    Serial.print(voltagemV);
    Serial.print("\t|");
    Serial.println(temperature);
}
