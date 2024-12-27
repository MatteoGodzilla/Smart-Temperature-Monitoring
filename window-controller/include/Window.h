#pragma once
#include <Servo.h>
#include "Task.h"
#include "pins.h"
#include "FiniteStateMachine.h"
#include "SerialCommunicator.h"
#include "LCDManager.h"

#define CLOSED_WINDOW 0
#define FULL_OPEN 90

class Window : public Task{
    private:
        FiniteStateMachine* fsm;
        SerialCommunicator* sc;
        LCDManager* lcd;
        Servo servoMotor;
        bool stateChanged;
        int lastCurrentPot;

    public:
        Window();
        void bindFSM(FiniteStateMachine* fsmTask);
        void bindSerialCommunicator(SerialCommunicator* scTask);
        void bindLCD(LCDManager* lcdTask);
        void setWindowPercentage(float percentage);
        virtual void execute() override;
};