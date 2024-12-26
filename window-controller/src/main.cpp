#include <Arduino.h>
#include <Wire.h>
#include "pins.h"
#include "Scheduler.h"
#include "FiniteStateMachine.h"
#include "LCDManager.h"
#include "SerialCommunicator.h"

Scheduler scheduler;

void setup() {
  //Initialize pins
  pinMode(BTN, INPUT);
  pinMode(POT, INPUT);
  pinMode(MOTOR, OUTPUT);

  //Initialize scheduler and create tasks
  scheduler.init();
  FiniteStateMachine* fsm = new FiniteStateMachine();

  SerialCommunicator* serialCommunicatorTask = new SerialCommunicator();
  scheduler.addTask(serialCommunicatorTask);

  LCDManager* lcdTask = new LCDManager();
  scheduler.addTask(lcdTask);

  //Bind tasks each other if necessary
  serialCommunicatorTask->bindFSM(fsm);
  serialCommunicatorTask->bindLCD(lcdTask);
  lcdTask->bindFSM(fsm);
}

void loop() {
  //Starting the execution
  scheduler.schedule();
}
