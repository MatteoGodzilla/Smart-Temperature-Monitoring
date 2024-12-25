#pragma once

//Ho fatto un solo stato MANUAL perché quando arduino è in MANUAL l'apertura della finestra può essere decisa
//dal potenziometro oppure dallo slider della web app, perché rileggendo il testo l'ho inteso così.
//DOMANDA: facciamo come scritto sopra o preferite 2 stati separati??????
enum State{
    AUTOMATIC,
    MANUAL
};

class FiniteStateMachine{
    public:
        State state;
        FiniteStateMachine();
};