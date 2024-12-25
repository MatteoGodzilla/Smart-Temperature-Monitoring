#pragma once
#include <Arduino.h>

class ElapsedTimer{
private:
    unsigned long startTime;
    unsigned long elapsed;
    unsigned long ms;
public:
    ElapsedTimer(unsigned long msToWait);
    void reset();
    void update();
    bool isOver();
};