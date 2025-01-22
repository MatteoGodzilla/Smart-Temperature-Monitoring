//---CONFIG CONSTANTS---
const route = "http://localhost:80/api"

//---""ENUMS""---
//temperature state
const STATUS_NORMAL = 0;
const STATUS_HOT = 1;
const STATUS_TOO_HOT = 2;
const STATUS_ALARM = 3;
//mode
const MODE_AUTOMATIC = 0;
const MODE_LOCAL_MANUAL = 1;
const MODE_REMOTE_MANUAL = 2;

//---DOM ELEMENTS---
const statusSpan = document.getElementById("status");
const modeSpan = document.getElementById("mode");
const tempSpan = document.getElementById("temp");
const windowSpan = document.getElementById("window");
const pauseSpan = document.getElementById("pause");

const pauseChartButton = document.getElementById("pauseChart");
const requestControlButton = document.getElementById("requestControl");
const controlWindowSpan = document.getElementById("userWindow");
const controlSlider = document.getElementById("windowOpenSlider");
const fixAlarmButton = document.getElementById("fixAlarmButton");
//---VARIABLES---
let dashboardHasControl = false;
let lastTick = 0;
let chartPaused = false;
let dataPointsBuffer = [];
let isControlFree = false;

async function isFree(){
    const url = route + "/isFree";
    const response = await fetch(url).then(res => res.json());
    isControlFree = response.message.free;
}

async function takeControl(){
    if(!dashboardHasControl){
        const url = route + "/takeControl";
        const available = await fetch(url).then(res => res.json);
        if(available){
            console.log('Got Control!');
            enableControls();
        }
    }
}

async function control(){
    if(dashboardHasControl){
        const url = route + "/control";
        //update text on corresponding span
        controlWindowSpan.innerText = Math.round(controlSlider.value * 100) + "%";
        await fetch(url,{
            method:"POST",
            headers:{
                "Content-Type":"application/json"
            },
            body:JSON.stringify({
                "position":controlSlider.value
            })
        });
    }
}

async function releaseControl(){
    if(dashboardHasControl){
        const url = route + "/releaseControl";
        await fetch(url); //we don't need the response
        disableControls();
    }
}

async function fixAlarm(){
    const url = route + "/fixAlarm";
    await fetch(url);
    fixAlarmButton.setAttribute("disabled", "disabled");
}

async function history(){
    const url = route + "/history";
    const response = await fetch(url).then(res => res.json())
    const json = response.message;
    for (const dataPoint of json.dataPoints) {
        chart.data.labels.push(tsToHumanReadableTime(dataPoint.timestamp));
        chart.data.datasets[0].data.push(dataPoint.window);
        chart.data.datasets[1].data.push(dataPoint.temperature);
        chart.data.datasets[2].data.push(json.minimum);
        chart.data.datasets[3].data.push(json.average);
        chart.data.datasets[4].data.push(json.maximum);
        lastTick = dataPoint.timestamp;
    }
    chart.update();
    console.log(json);
}

async function getStatus(){
    const url = route + "/status";
    const response = await fetch(url).then(res=>res.json());
    const json = response.message;

    //parse json
    const status = json.status;
    const mode = json.mode;
    const dataPoint = json.datapoint;
    const min = json.minimum;
    const avg = json.average;
    const max = json.maximum;
    const nextStatus = json.nextStatus;
    const maxDataPoints = json.maxDatapoints;

    //update aside
    statusSpan.innerText = tempStatusToString(status);
    modeSpan.innerText = modeToString(mode);
    tempSpan.innerText = dataPoint.temperature + "°C"
    windowSpan.innerText = (dataPoint.window * 100).toFixed(0) + "%"
    pauseSpan.innerText = chartPaused ? "Paused" : "Running";

    pauseChartButton.innerText = chartPaused ? "Resume chart" : "Pause chart";

    if(dashboardHasControl){
        //this dashboard currently has the control
        requestControlButton.innerText = "Release control";
        requestControlButton.removeAttribute("disabled");
    } else {
        if(isControlFree){
            //we can take the control
            requestControlButton.innerText = "Request control";
            requestControlButton.removeAttribute("disabled");
        } else {
            //someone else has control, so we cannot get it
            requestControlButton.innerText = "Cannot request control";
            requestControlButton.setAttribute("disabled", "disabled");
        }
    }

    dataPointsBuffer.push(dataPoint);

    //update graph
    if(!chartPaused){
        while(dataPointsBuffer.length > 0){
            const point = dataPointsBuffer.shift();
            if(point.timestamp > lastTick){
                //remove old points from chart
                while(chart.data.labels.length > maxDataPoints - 1){
                    chart.data.labels.shift();
                    chart.data.datasets[0].data.shift();
                    chart.data.datasets[1].data.shift();
                    chart.data.datasets[2].data.shift();
                    chart.data.datasets[3].data.shift();
                    chart.data.datasets[4].data.shift();
                }
                //add new point to chart
                chart.data.labels.push(tsToHumanReadableTime(point.timestamp));
                chart.data.datasets[0].data.push(point.window);
                chart.data.datasets[1].data.push(point.temperature);
                chart.data.datasets[2].data.push(min);
                chart.data.datasets[3].data.push(avg);
                chart.data.datasets[4].data.push(max);
                lastTick = point.timestamp;
            }
        }
        chart.update();
    }

    //update controls
    isFree();
    if(dashboardHasControl && mode != MODE_REMOTE_MANUAL){
        //this means it has been disabled by the control unit
        disableControls();
    }

    if(status == STATUS_ALARM){
        fixAlarmButton.removeAttribute("disabled");
    }

    setTimeout(getStatus,nextStatus);
}

//button callbacks
function pauseChart(){
    chartPaused = !chartPaused;
}

async function requestButtonOnClick(){
    if(dashboardHasControl){
        await releaseControl();
    } else {
        await takeControl();
    }
}

//utility functions
function tempStatusToString(state){
    switch(state){
        case STATUS_NORMAL: return "NORMAL";
        case STATUS_HOT: return "HOT";
        case STATUS_TOO_HOT: return "TOO HOT";
        case STATUS_ALARM: return "!!!ALARM!!!";
        default: return "";
    }
}

function modeToString(mode){
    switch(mode){
        case MODE_AUTOMATIC: return "AUTOMATIC";
        case MODE_LOCAL_MANUAL: return "MANUAL (LOCAL)";
        case MODE_REMOTE_MANUAL: return "MANUAL (REMOTE)";
        default: return "";
    }
}

function enableControls(){
    dashboardHasControl = true;
    controlSlider.removeAttribute("disabled");
}

function disableControls(){
    dashboardHasControl = false;
    controlSlider.setAttribute("disabled", "disabled");
}

function tsToHumanReadableTime(timestamp){
    const date = new Date(timestamp * 1000);
    //return `${date.getHours()}:${date.getMinutes()}:${date.getSeconds()}`;
    return date.toLocaleString();
}

//startup
disableControls();
history();
getStatus();
