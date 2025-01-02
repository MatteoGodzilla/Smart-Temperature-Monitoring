//chart stuff
const ctx = document.getElementById("plotCanvas");
const chart = new Chart(ctx, {
    type: 'line',
    data: {
        datasets: [{
            label: 'Window open %',
            // This binds the dataset to the right y axis
            yAxisID: 'windowAxis',
            fill:"origin"
        }, {
            label: 'Temperature',
            // This binds the dataset to the left y axis
            yAxisID: 'temperatureAxis'
        },{
            label: 'Temperature Minimum',
            // This binds the dataset to the left y axis
            yAxisID: 'temperatureAxis'
        },{
            label: 'Temperature Average',
            // This binds the dataset to the left y axis
            yAxisID: 'temperatureAxis'
        },{
            label: 'Temperature Maximum',
            // This binds the dataset to the left y axis
            yAxisID: 'temperatureAxis'
        }],
    },
    options: {
        scales: {
            'temperatureAxis': {
                type: 'linear',
                position: 'left'
            },
            'windowAxis': {
                type: 'linear',
                position: 'right',
                ticks:{
                    format:{
                        style: "percent"
                    }
                }
            }
        },
        maintainAspectRatio:false
    }
});

//dashboard functions

const route = "http://localhost:80/"



async function updateHistory(){
    const url = route + "/history"
    //const json = await fetch(url).then(res => res.json())
    const json = {"dataPoints": [{"timestamp": 1000, "temperature": 34.55, "window": 0.24}, {"timestamp": 2000, "temperature": 30.45, "window": 0.14}, {"timestamp": 2500, "temperature": 38.5, "window": 0.86}, {"timestamp": 4250, "temperature": 26.76, "window": 0.03}], "minimum": 26.76, "maximum": 38.5, "average": 32.565}
    for (const dataPoint of json.dataPoints) {
        chart.data.labels.push(dataPoint.timestamp);
        chart.data.datasets[0].data.push(dataPoint.window);
        chart.data.datasets[1].data.push(dataPoint.temperature);
        chart.data.datasets[2].data.push(json.minimum);
        chart.data.datasets[3].data.push(json.average);
        chart.data.datasets[4].data.push(json.maximum);
    }
    chart.update();

    console.log(json);
}

async function getStatus(){
    const url = route = "/status"
}

updateHistory();
