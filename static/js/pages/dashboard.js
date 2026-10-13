(function () {
    var dataElement = document.getElementById('dashboard-charts-data');
    if (!dataElement) return;

    var chartIds = ['estado-cumplimiento', 'trabajadores-por-empresa', 'trabajadores-mensual', 'documentos-por-vencer'];

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

    if (!data || !Array.isArray(data.cumplimiento) || !data.trabajadores_empresa ||
            !Array.isArray(data.trabajadores_empresa.labels) ||
            !Array.isArray(data.trabajadores_empresa.habilitados) ||
            !Array.isArray(data.trabajadores_empresa.inhabilitados)) {
        showChartError('No hay datos válidos para generar las gráficas.');
        return;
    }
    if (!data.trabajadores_mensual || !Array.isArray(data.trabajadores_mensual.labels) ||
            !Array.isArray(data.trabajadores_mensual.habilitados) ||
            !Array.isArray(data.trabajadores_mensual.inhabilitados)) {
        showChartError('No hay datos válidos para generar las gráficas.');
        return;
    }
    if (!data.documentos_por_vencer || !Array.isArray(data.documentos_por_vencer.labels) ||
            !Array.isArray(data.documentos_por_vencer.data)) {
        showChartError('No hay datos válidos para generar las gráficas.');
        return;
    }
    var textColor = '#475569';
    var gridColor = '#e8edf3';
    var fontFamily = 'Inter, ui-sans-serif, system-ui, sans-serif';
    var doughnutLabels = ['Habilitados', 'No habilitados'];
    var doughnutColors = ['#22c55e', '#ef4444'];

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
            var chartTotal = chart.data.datasets.reduce(function (sum, dataset) {
                return sum + total(dataset.data);
            }, 0);
            if (chartTotal !== 0) return;
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
    var workersStatusCanvas = document.getElementById('trabajadores-por-empresa');
    var workersMonthlyCanvas = document.getElementById('trabajadores-mensual');
    var expiringDocumentsCanvas = document.getElementById('documentos-por-vencer');
    if (!complianceLegend || !complianceCanvas || !workersStatusCanvas || !workersMonthlyCanvas || !expiringDocumentsCanvas) {
        showChartError('No fue posible preparar las gráficas.');
        return;
    }

    var workersChartCanvas = workersStatusCanvas.parentElement;
    var workersChartAvailableWidth = workersChartCanvas.parentElement.clientWidth;
    workersChartCanvas.style.width = Math.max(600, workersChartAvailableWidth, data.trabajadores_empresa.labels.length * 72) + 'px';
    workersChartCanvas.style.height = '256px';

    complianceLegend.innerHTML = doughnutLabels.map(function (label, index) {
        var value = data.cumplimiento[index];
        var percentage = complianceTotal ? Math.round((value / complianceTotal) * 100) : 0;
        return '<div class="dashboard-chart-legend-item">' +
            '<span class="dashboard-chart-legend-dot" style="background:' + doughnutColors[index] + '"></span>' +
            '<span class="dashboard-chart-legend-label">' + label + '</span>' +
            '<span class="dashboard-chart-legend-value">' + value + ' trabajadores · ' + percentage + '%</span>' +
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
                            return ' ' + context.raw + ' trabajadores (' + percentage + '%)';
                        }
                    }
                }
            }
        }
    });

    new Chart(workersStatusCanvas, {
        type: 'bar', plugins: [emptyStatePlugin],
        data: { labels: data.trabajadores_empresa.labels, datasets: [
            { label: 'Habilitados', data: data.trabajadores_empresa.habilitados, backgroundColor: '#10b981', borderRadius: 4, borderSkipped: false, maxBarThickness: 32 },
            { label: 'No habilitados', data: data.trabajadores_empresa.inhabilitados, backgroundColor: '#ef4444', borderRadius: 4, borderSkipped: false, maxBarThickness: 32 }
        ] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom' }, tooltip: tooltipOptions(' trabajadores') }, scales: { x: { ticks: { autoSkip: false, maxRotation: 55, minRotation: 30, padding: 6 }, border: { display: false }, grid: { display: false } }, y: { beginAtZero: true, ticks: { precision: 0, padding: 8 }, border: { display: false }, grid: { color: gridColor } } } }
    });

    new Chart(workersMonthlyCanvas, {
        type: 'bar', plugins: [emptyStatePlugin],
        data: { labels: data.trabajadores_mensual.labels, datasets: [
            { label: 'Habilitados', data: data.trabajadores_mensual.habilitados, backgroundColor: '#10b981', borderRadius: 4, borderSkipped: false },
            { label: 'No habilitados', data: data.trabajadores_mensual.inhabilitados, backgroundColor: '#ef4444', borderRadius: 4, borderSkipped: false }
        ] },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'bottom' }, tooltip: tooltipOptions(' trabajadores') },
            scales: {
                x: { stacked: true, border: { display: false }, grid: { display: false } },
                y: { stacked: true, beginAtZero: true, ticks: { precision: 0 }, border: { display: false }, grid: { color: gridColor } }
            }
        }
    });

    new Chart(expiringDocumentsCanvas, {
        type: 'bar',
        plugins: [emptyStatePlugin],
        data: {
            labels: data.documentos_por_vencer.labels,
            datasets: [{
                label: 'Documentos por vencer',
                data: data.documentos_por_vencer.data,
                backgroundColor: '#f59e0b',
                borderRadius: 4,
                borderSkipped: false,
                maxBarThickness: 42
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: { legend: { display: false }, tooltip: tooltipOptions(' documentos') },
            scales: {
                x: { beginAtZero: true, ticks: { precision: 0 }, border: { display: false }, grid: { color: gridColor } },
                y: { ticks: { autoSkip: false }, border: { display: false }, grid: { display: false } }
            }
        }
    });

})();
