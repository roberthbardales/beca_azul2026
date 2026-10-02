(function () {
    var canvas = document.getElementById('empresa-estado-trabajadores');
    var dataElement = document.getElementById('empresa-trabajadores-chart-data');
    if (!canvas || !dataElement || typeof window.Chart === 'undefined') return;

    var data;
    try {
        data = JSON.parse(dataElement.textContent);
    } catch (error) {
        return;
    }

    if (!data || !Array.isArray(data.labels) || !Array.isArray(data.data) || data.labels.length !== 2 || data.data.length !== 2) return;

    var textColor = '#475569';
    var gridColor = '#e8edf3';
    var emptyStatePlugin = {
        id: 'empresaEmptyState',
        afterDraw: function (chart) {
            if (chart.data.datasets[0].data.some(function (value) { return value !== 0; })) return;
            var area = chart.chartArea;
            var context = chart.ctx;
            context.save();
            context.textAlign = 'center';
            context.textBaseline = 'middle';
            context.fillStyle = '#94a3b8';
            context.font = '600 13px Inter, sans-serif';
            context.fillText('Sin información disponible', (area.left + area.right) / 2, (area.top + area.bottom) / 2);
            context.restore();
        }
    };

    new window.Chart(canvas, {
        type: 'doughnut',
        plugins: [emptyStatePlugin],
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Trabajadores',
                data: data.data,
                 backgroundColor: ['#16a34a', '#dc2626'],
                borderWidth: 0,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '62%',
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom',
                    labels: {
                        color: '#475569',
                        usePointStyle: true,
                        pointStyle: 'circle',
                        padding: 16,
                        generateLabels: function (chart) {
                            return chart.data.labels.map(function (label, index) {
                                return {
                                    text: label + ': ' + chart.data.datasets[0].data[index],
                                    fillStyle: chart.data.datasets[0].backgroundColor[index],
                                    strokeStyle: chart.data.datasets[0].backgroundColor[index],
                                    lineWidth: 0,
                                    hidden: false,
                                    index: index
                                };
                            });
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function (context) { return ' ' + context.raw + ' trabajadores'; }
                    }
                }
            }
        }
    });
})();
