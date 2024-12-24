#include "Scheduler.h"

void Scheduler::init(){
    nTask = 0;
}

bool Scheduler::addTask(Task* task){
    if(nTask < NUMTASKS) {
        tasks[nTask] = task;
        nTask++;
        return true;
    } else {
        return false;
    }
}

void Scheduler::schedule(){
    for(int i = 0; i < nTask; i++) {
        if(tasks[i]->isActive()) {
            tasks[i]->excecute();
        }
    }
}