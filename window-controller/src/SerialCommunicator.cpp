#include "SerialCommunicator.h"

#include "Window.h"

SerialCommunicator::SerialCommunicator(){
    active = true;
    Serial.begin(9600);
}

void SerialCommunicator::bindLCD(LCDManager* lcdTask){
    lcd = lcdTask;
}

void SerialCommunicator::bindFSM(FiniteStateMachine* fsmTask){
    fsm = fsmTask;
}

void SerialCommunicator::bindWindow(Window* windowTask){
    window = windowTask;
}

//Method to send the state of the FSM to control unit
void SerialCommunicator::sendState(int desiredState){
    Serial.print("S:");
    Serial.print(desiredState);
    Serial.println(";");
    Serial.flush();
}

void SerialCommunicator::sendOpeningWindow(float val){
    Serial.print("P:");
    Serial.print(val);
    Serial.println(";");
    Serial.flush();
}

void SerialCommunicator::execute(){
    if(Serial.available() > 0) {
        String input = Serial.readStringUntil(';');
        //To ensure that leading spaces, trailing spaces and control characters are removed
        input.trim();
        if(input.length() > 0) {
            String c = input.substring(0,2);
            //After c there is the value [0.00,1.00] for opening the window when the status is AUTOMATIC
            if(fsm->state == AUTOMATIC && c.equals("P:")) {
                String value = input.substring(2);
                //Casting the value read in float
                float percentage = value.toFloat();
                //Check if the value is in the range [0.00,1.00]
                percentage = (percentage > 1.00) ? 1.00 : percentage;
                percentage = (percentage < 0.00) ? 0.00 : percentage;
                lcd->setWindowLevel(percentage);
                window->setWindowPercentage(percentage);
            }
            //S indicates the change of status of the FSM
            else if(c.equals("S:")) {
                String stateValue = input.substring(2);
                int stateNumber = stateValue.toInt();
                if(stateNumber != 1) {
                    fsm->state = AUTOMATIC;
                    Serial.print(";");
                    Serial.flush();
                } else {
                    fsm->state = MANUAL;
                }
            }
            //After c there is the temperature value when the status is MANUAL
            else if(fsm->state == MANUAL && c.equals("T:")) {
                String tempValue = input.substring(2);
                lcd->setTemperature(tempValue.toFloat());
            }
        }
    }
}