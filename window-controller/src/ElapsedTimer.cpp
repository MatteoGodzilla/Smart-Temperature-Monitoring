#include "ElapsedTimer.h"

ElapsedTimer::ElapsedTimer(unsigned long msToWait){
    ms = msToWait;
    reset();
}

void ElapsedTimer::reset(){
    startTime = millis();
}

void ElapsedTimer::update(){
    elapsed = millis() - startTime;
}

bool ElapsedTimer::isOver(){
    return elapsed >= ms;
}