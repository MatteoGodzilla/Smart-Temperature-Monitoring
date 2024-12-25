#include <Arduino.h>
#include "pins.h"
#include "Scheduler.h"

Scheduler scheduler;

void setup() {
  // put your setup code here, to run once:
  pinMode(BTN, INPUT);
  pinMode(POT, INPUT);
  pinMode(MOTOR, OUTPUT);

  scheduler.init();
}

void loop() {
  // put your main code here, to run repeatedly:
  scheduler.schedule();
}
