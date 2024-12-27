#include "LCDManager.h"

LCDManager::LCDManager() :
    lcd(LiquidCrystal_I2C(0x27,20,4)),
    timerPrint(TIMEPRINT)
{
    lcd.init();
    lcd.backlight();
    active = true;
    openingLevel = 0;
}

void LCDManager::bindFSM(FiniteStateMachine* fsmTask){
    fsm = fsmTask;
}

//To take the level opening of window from SerialCommunicator
void LCDManager::setWindowLevel(float windowLevel){
    openingLevel = round(windowLevel*100);
}

//To take the value of temperature from SerialCommunicator
void LCDManager::setTemperature(float tempValue){
    temp = tempValue;
}

void LCDManager::execute(){
    if(timerPrint.isOver()) {
        timerPrint.reset();
        lcd.clear();
        switch(fsm->state){
            case AUTOMATIC:
                lcd.setCursor(0,0);
                lcd.printstr("WINDOW OPENING: ");
                lcd.print(openingLevel);
                lcd.printstr("%");
                lcd.setCursor(0,1);
                lcd.printstr("AUTOMATIC");
                break;
            case MANUAL:
                lcd.setCursor(0,0);
                lcd.printstr("WINDOW OPENING: ");
                lcd.print(openingLevel);
                lcd.printstr("%");
                lcd.setCursor(0,1);
                lcd.printstr("MANUAL");
                lcd.setCursor(0,2);
                lcd.printstr("TEMPERATURE: ");
                //lcd.print(temp);
                lcd.printstr(" C");
                break;
            default:
                lcd.setCursor(0,0);
                lcd.printstr("PROBLEM!!!");
                break;
        }
    }
    timerPrint.update();
}