(function () {
    var dataElement = document.getElementById('dashboard-charts-data');
    if (!dataElement) return;

    var chartIds = ['estado-cumplimiento', 'trabajadores-por-empresa', 'altas-trabajadores'];

    function showChartError(message) {
        chartIds.forEach(function (id) {
            var canvas = document.getElementById(id);
            if (!canvas || !canvas.parentElement) return;
            canvas.hidden = true;
            var notice = document.createElement('p');
            notice.className = 'dashboard-chart-error';
            notice.textContent = message;
            canvas.parentElement.appendChild(notice);
        });
    }

    if (typeof Chart === 'undefined') {
        showChartError('No fue posible cargar las gráficas.');
        return;
    }

    var data;
    try {
        data = JSON.parse(dataElement.textContent);
    } catch (error) {
        showChartError('Los datos de las gráficas no son válidos.');
        return;
    }

    if (!data || !Array.isArray(data.cumplimiento) || !data.empresas ||
            !Array.isArray(data.empresas.labels) || !Array.isArray(data.empresas.data) ||
            !data.altas || !Array.isArray(data.altas.labels) || !Array.isArray(data.altas.data)) {
        showChartError('No hay datos válidos para generar las gráficas.');
        return;
    }
    var textColor = '#475569';
    var gridColor = '#e8edf3';
    var fontFamily = 'Inter, ui-sans-serif, system-ui, sans-serif';
    var doughnutLabels = ['Vigentes', 'Próximos a vencer', 'Vencidos'];
    var doughnutColors = ['#22c55e', '#fbbf24', '#ef4444'];

    Chart.defaults.color = textColor;
    Chart.defaults.font.family = fontFamily;
    Chart.defaults.animation = false;

    function total(values) {
        return values.reduce(function (sum, value) { return sum + value; }, 0);
    }

    function tooltipOptions(suffix) {
        return {
            backgroundColor: '#334155',
            titleColor: '#ffffff',
            bodyColor: '#e2e8f0',
            padding: 9,
            cornerRadius: 4,
            displayColors: false,
            callbacks: { label: function (context) { return context.raw + suffix; } }
        };
    }

    var emptyStatePlugin = {
        id: 'emptyState',
        afterDraw: function (chart) {
            if (total(chart.data.datasets[0].data) !== 0) return;
            var area = chart.chartArea;
            var ctx = chart.ctx;
            ctx.save();
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillStyle = '#94a3b8';
            ctx.font = '600 13px ' + fontFamily;
            ctx.fillText('Sin información disponible', (area.left + area.right) / 2, (area.top + area.bottom) / 2);
            ctx.restore();
        }
    };

    var centerTextPlugin = {
        id: 'centerText',
        afterDraw: function (chart) {
            var chartTotal = total(chart.data.datasets[0].data);
            var point = chart.getDatasetMeta(0).data[0];
            if (!chartTotal || !point) return;
            var ctx = chart.ctx;
            ctx.save();
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillStyle = '#0f172a';
            ctx.font = '700 28px ' + fontFamily;
            ctx.fillText(chartTotal, point.x, point.y - 9);
            ctx.font = '600 11px ' + fontFamily;
            ctx.fillStyle = textColor;
            ctx.fillText('Total', point.x, point.y + 17);
            ctx.restore();
        }
    };

    var complianceTotal = total(data.cumplimiento);
    var complianceLegend = document.getElementById('cumplimiento-legend');
    var complianceCanvas = document.getElementById('estado-cumplimiento');
    var companiesCanvas = document.getElementById('trabajadores-por-empresa');
    var registrationsCanvas = document.getElementById('altas-trabajadores');
    if (!complianceLegend || !complianceCanvas || !companiesCanvas || !registrationsCanvas) {
        showChartError('No fue posible preparar las gráficas.');
        return;
    }

    complianceLegend.innerHTML = doughnutLabels.map(function (label, index) {
        var value = data.cumplimiento[index];
        var percentage = complianceTotal ? Math.round((value / complianceTotal) * 100) : 0;
        return '<div class="dashboard-chart-legend-item">' +
            '<span class="dashboard-chart-legend-dot" style="background:' + doughnutColors[index] + '"></span>' +
            '<span class="dashboard-chart-legend-label">' + label + '</span>' +
            '<span class="dashboard-chart-legend-value">' + percentage + '% (' + value + ')</span>' +
            '</div>';
    }).join('');

    new Chart(complianceCanvas, {
        type: 'doughnut',
        plugins: [emptyStatePlugin, centerTextPlugin],
        data: { labels: doughnutLabels, datasets: [{ data: data.cumplimiento, backgroundColor: doughnutColors, borderColor: '#ffffff', borderWidth: 3 }] },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '55%',
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#334155',
                    titleColor: '#ffffff',
                    bodyColor: '#e2e8f0',
                    padding: 9,
                    cornerRadius: 4,
                    displayColors: false,
                    callbacks: {
                        label: function (context) {
                            var percentage = complianceTotal ? Math.round((context.raw / complianceTotal) * 100) : 0;
                            return ' ' + context.raw + ' certificados (' + percentage + '%)';
                        }
                    }
                }
            }
        }
    });

    var barColors = ['#ef4444', '#f97316', '#eab308', '#1677df', '#10b981'];
    new Chart(companiesCanvas, {
        type: 'bar',
        plugins: [emptyStatePlugin],
        data: {
            labels: data.empresas.labels,
            datasets: [{
                label: 'Trabajadores',
                data: data.empresas.data,
                backgroundColor: data.empresas.data.map(function (_, index) { return barColors[index % barColors.length]; }),
                borderRadius: 4,
                borderSkipped: false,
                maxBarThickness: 44
            }]
        },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false }, tooltip: tooltipOptions(' trabajadores') }, scales: { y: { beginAtZero: true, ticks: { precision: 0, padding: 8 }, border: { display: false }, grid: { color: gridColor } }, x: { border: { display: false }, grid: { display: false }, ticks: { maxRotation: 35, minRotation: 0, padding: 8 } } } }
    });

    new Chart(registrationsCanvas, {
        type: 'line',
        plugins: [emptyStatePlugin],
        data: {
            labels: data.altas.labels,
            datasets: [{
                label: 'Nuevos trabajadores',
                data: data.altas.data,
                borderColor: '#1677df',
                pointBackgroundColor: '#1677df',
                pointBorderColor: '#1677df',
                pointBorderWidth: 2,
                pointRadius: 4,
                pointHoverRadius: 5,
                borderWidth: 3,
                tension: .28,
                fill: false
            }]
        },
        options: { responsive: true, maintainAspectRatio: false, interaction: { intersect: false, mode: 'index' }, plugins: { legend: { display: false }, tooltip: tooltipOptions(' altas') }, scales: { y: { beginAtZero: true, ticks: { precision: 0, padding: 8 }, border: { display: false }, grid: { color: gridColor } }, x: { border: { display: false }, grid: { display: false }, ticks: { padding: 8 } } } }
    });
})();
