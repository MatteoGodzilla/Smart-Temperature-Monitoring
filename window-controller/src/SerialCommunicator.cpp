#include "SerialCommunicator.h"

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

//Mandiamo lo stato vero e proprio oppure un comando di cambio stato???
//Method to send the state of the FSM to control unit
void SerialCommunicator::sendState(){
    Serial.print("CS");
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
        //Per assicurarsi che vengano eliminati spazi iniziali, spazi finali e caratteri di controllo
        input.trim();
        if(input.length() > 0) {
            String c = input.substring(0,2);
            //Dopo c c'è il valore [0,1] di apertura della finestra
            if(c.equals("P:")) {
                String value = input.substring(2);
                lcd->setWindowLevel(value.toFloat());
            }
            //S indica il cambio di stato della FSM
            else if(c.equals("CS")) {
                if(fsm->state == AUTOMATIC) {
                    fsm->state = MANUAL;
                } else {
                    fsm->state = AUTOMATIC;
                }
            }
            //Dopo c c'è il valore della temperatura
            else if(fsm->state == MANUAL && c.equals("T:")) {
                String tempValue = input.substring(2);
                lcd->setTemperature(tempValue.toFloat());
            }
        }
    }
}