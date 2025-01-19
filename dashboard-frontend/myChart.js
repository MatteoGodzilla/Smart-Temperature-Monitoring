//chart stuff
const ctx = document.getElementById("plotCanvas");
const chart = new Chart(ctx, {
    type: 'line',
    data: {
        datasets: [{
            label: 'Window open %',
            // This binds the dataset to the right y axis
            yAxisID: 'windowAxis',
            fill:"origin",
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
                },
                min:0,
                max:1
            }
        },
        maintainAspectRatio:false
    }
});