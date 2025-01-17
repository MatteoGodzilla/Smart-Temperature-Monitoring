#pragma once

enum State{
    AUTOMATIC, //equal to 0
    MANUAL //equal to 1
};

class FiniteStateMachine{
    public:
        State state;
        FiniteStateMachine();
};