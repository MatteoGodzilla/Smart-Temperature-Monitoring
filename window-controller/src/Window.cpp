#include "Window.h"

Window::Window(){
    active = true;
    servoMotor.attach(MOTOR);
    servoMotor.write(CLOSED_WINDOW);
    stateChanged = false;
    lastCurrentPot = 0;
}

void Window::bindFSM(FiniteStateMachine* fsmTask){
    fsm = fsmTask;
}

void Window::bindSerialCommunicator(SerialCommunicator* scTask){
    sc = scTask;
}

void Window::bindLCD(LCDManager* lcdTask){
    lcd = lcdTask;
}

void Window::setWindowPercentage(float percentage){
    int opening = round(percentage*100);
    int angle = map(opening, 1, 100, CLOSED_WINDOW, FULL_OPEN);
    servoMotor.write(angle);
}

//Method to provide a map function for float number
float mapFloat(float x, float in_min, float in_max, float out_min, float out_max) {
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}

void Window::execute(){
    switch(fsm->state){
        case AUTOMATIC:
            /*
            * In AUTOMATIC mode, if the button is pressed, the state must be changed into MANUAL and
            * send the message on the Serial Monitor
            */
            if(digitalRead(BTN) == HIGH) {
                if(!stateChanged) {
                    fsm->state = MANUAL;
                    sc->sendState("MANUAL");
                }
                stateChanged = true;
            } else {
                stateChanged = false;
            }
            break;
        case MANUAL:
            /*
            * In MANUAL mode, the opening level of the window can be modified with a potentiometer
            */
            int currentPot = analogRead(POT);
            if(currentPot != lastCurrentPot) {
                float convertedValue = mapFloat(currentPot, 0, 1023, 0.01, 1.00);
                lcd->setWindowLevel(convertedValue);
                setWindowPercentage(convertedValue);
            }
            lastCurrentPot = currentPot;
            /*
            * In MANUAL mode, if the button is pressed, the state must be changed into AUTOMATIC and
            * send the messagge on the Serial Monitor
            */
            if(digitalRead(BTN) == HIGH) {
                if(!stateChanged) {
                    fsm->state = AUTOMATIC;
                    sc->sendState("AUTOMATIC");
                }
                stateChanged = true;
            } else {
                stateChanged = false;
            }
            break;
    }
}