#pragma once
#include <LiquidCrystal_I2C.h>
#include "FiniteStateMachine.h"
#include "Task.h"
#include "ElapsedTimer.h"

#define TIMEPRINT 1000

class LCDManager : public Task{
    private:
        int openingLevel;
        float temp;
        LiquidCrystal_I2C lcd;
        FiniteStateMachine* fsm;
        ElapsedTimer timerPrint;

    public:
        LCDManager();
        void bindFSM(FiniteStateMachine* fsmtask);
        void setWindowLevel(float windowLevel);
        void setTemperature(float tempValue);
        virtual void execute() override;
};