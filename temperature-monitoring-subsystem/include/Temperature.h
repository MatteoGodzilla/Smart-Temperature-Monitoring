#pragma once
#include <Arduino.h>
#include <esp_adc_cal.h>

//the code is written to use ADC1, because we also have to use the wifi module, which conflicts with ADC2
#define TEMPERATURE_AVERAGE_SIZE 100

namespace Temperature{
    void init(uint8_t gpioPin, adc_channel_t adcChannel);
    void pushReading();
    double getAverageTemperature();
}