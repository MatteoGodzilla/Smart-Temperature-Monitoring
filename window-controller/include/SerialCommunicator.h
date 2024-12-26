#pragma once
#include "Task.h"
#include "LCDManager.h"
#include "FiniteStateMachine.h"

class SerialCommunicator : public Task{
    private:
        LCDManager* lcd;
        FiniteStateMachine* fsm;

    public:
        SerialCommunicator();
        void bindLCD(LCDManager* lcdTask);
        void bindFSM(FiniteStateMachine* fsmTask);
        void sendState();
        void sendOpeningWindow(float val);
        virtual void execute() override;
};