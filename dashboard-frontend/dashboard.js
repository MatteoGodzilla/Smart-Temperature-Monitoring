const ctx = document.getElementById("plotCanvas");

const route = "http://localhost:80/"

const chart = new Chart(ctx, {
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


async function updateHistory(){
    const url = route + "/history"
    const json = await fetch(url).then(res => res.json())


    console.log(json);
}


async function getStatus(){
    const url = route = "/status"
}

//updateHistory();
