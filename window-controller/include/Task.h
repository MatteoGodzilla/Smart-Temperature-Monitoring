#pragma once

class Task{
    public:
        bool isActive();
        virtual void excecute() = 0;

    protected:
        bool active;
};