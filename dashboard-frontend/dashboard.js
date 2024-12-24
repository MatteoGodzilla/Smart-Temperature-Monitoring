const ctx = document.getElementById("plotCanvas");

new Chart(ctx, {
    type: 'line',
    data: {
        datasets: [{
            data: [20, 50, 100, 75, 25, 0],
            label: 'Temperature',

            // This binds the dataset to the left y axis
            yAxisID: 'temperatureAxis'
        }, {
            data: [0.1, 0.25, 0.5, 1.0, 1.0, 0],
            label: 'Window open %',

            // This binds the dataset to the right y axis
            yAxisID: 'windowAxis',
            fill:"origin"
        }],
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
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
