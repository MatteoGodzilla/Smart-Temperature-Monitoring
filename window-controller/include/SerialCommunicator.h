#pragma once
#include "Task.h"
#include "LCDManager.h"
#include "FiniteStateMachine.h"

//forward declaration of tasks required, in order to break the cyclic dependency
class Window;

class SerialCommunicator : public Task{
    private:
        LCDManager* lcd;
        FiniteStateMachine* fsm;
        Window* window;

    public:
        SerialCommunicator();
        void bindLCD(LCDManager* lcdTask);
        void bindFSM(FiniteStateMachine* fsmTask);
        void bindWindow(Window* windowTask);
        void sendState(int desiredState);
        void sendOpeningWindow(float val);
        virtual void execute() override;
};