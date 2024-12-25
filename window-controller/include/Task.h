#pragma once

class Task{
    public:
        bool isActive();
        virtual void execute() = 0;

    protected:
        bool active;
};