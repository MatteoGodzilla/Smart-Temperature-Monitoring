#include <Arduino.h>
#include <Wire.h>
#include "pins.h"
#include "Scheduler.h"
#include "FiniteStateMachine.h"
#include "LCDManager.h"

Scheduler scheduler;

void setup() {
  //Initialize pins
  pinMode(BTN, INPUT);
  pinMode(POT, INPUT);
  pinMode(MOTOR, OUTPUT);

  //Initialize scheduler and create tasks
  scheduler.init();
  FiniteStateMachine* fsm = new FiniteStateMachine();

  LCDManager* lcd = new LCDManager();
  scheduler.addTask(lcd);

  //Bind tasks each other if necessary
  lcd->bindFSM(fsm);
}

void loop() {
  //Starting the execution
  scheduler.schedule();
}
