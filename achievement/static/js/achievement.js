const data1 = {
    labels: labels,  // `labels` should be passed in from the template
    datasets: [{
        data: data,  // `data` should be passed in from the template
        backgroundColor: ['#ff2c2c', '#00b627', '#2196F3', '#535353'],
        borderColor: ['#ff2c2c', '#00b627', '#2196F3', '#535353'],
        hoverOffset: 4
    }]
};

const config1 = {
    type: 'pie',
    data: data1,
    options: {
        responsive: true,
        plugins: {
            title: {
                display: true,
                text: chart_name  // `chart_name` should be passed in from the template
            },
            legend: {
                position: 'right'
            },
            datalabels: {
                formatter: (value, context) => value > 0 ? value : '',
                color: '#fff',
                font: {
                    size: 14,
                },
            }
        }
    },
    plugins: [ChartDataLabels]
};

document.addEventListener("DOMContentLoaded", function() {
    const pieChart1 = new Chart(
        document.getElementById('myChart'),
        config1
    );
});