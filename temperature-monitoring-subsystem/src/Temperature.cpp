#include "Temperature.h"

namespace Temperature{
    static esp_adc_cal_characteristics_t adcCurve;
    static uint32_t readingBuffer[TEMPERATURE_AVERAGE_SIZE] = {};
    static int writeIndex = 0;

    static adc_channel_t channel;

    void init(uint8_t gpioPin, adc_channel_t adcChannel){
        //setup adc curve
        analogSetPinAttenuation(gpioPin, ADC_11db);
        esp_adc_cal_value_t returnType = esp_adc_cal_characterize(ADC_UNIT_1, ADC_ATTEN_DB_12, ADC_WIDTH_BIT_12, ESP_ADC_CAL_VAL_EFUSE_VREF, &adcCurve);
        channel = adcChannel;
    }

    void pushReading(){
        //note that the ADC in esp32 is not perfectly linear, but we'll pretent it is
        uint32_t voltagemV;
        esp_adc_cal_get_voltage(channel, &adcCurve, &voltagemV);
        readingBuffer[writeIndex] = voltagemV;
        writeIndex = (writeIndex + 1) % TEMPERATURE_AVERAGE_SIZE;
    }

    //the ADC is very, VERY noisy, so we take an average of the last N samples and use that as a value
    double getAverageTemperature(){
        double sum = 0;
        for(int i = 0; i < TEMPERATURE_AVERAGE_SIZE; i++){
            sum += readingBuffer[i];
        }
        double voltagemV = sum / TEMPERATURE_AVERAGE_SIZE;
        //TMP36 provides a 750mV output at 25°C
        //it has an output scale of 10mV / °C
        return (voltagemV - 750.0) / 10 + 25.0;
    }
}