/**
 * PDSA Tracker - Advanced Chart.js Visualizations
 * Includes run charts, control charts, statistical annotations, and exports
 */

// Chart.js global configuration
Chart.defaults.font.family = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif";
Chart.defaults.plugins.legend.display = true;
Chart.defaults.plugins.tooltip.enabled = true;

/**
 * Create a run chart with baseline and target lines
 * @param {string} canvasId - Canvas element ID
 * @param {Array} dataPoints - Array of {date, value} objects
 * @param {number} baseline - Baseline value
 * @param {number} target - Target value
 * @param {string} unit - Measurement unit
 * @param {Object} controlLimits - Optional {ucl, lcl, mean} from ML analyzer
 */
function createRunChart(canvasId, dataPoints, baseline, target, unit, controlLimits = null) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    const dates = dataPoints.map(dp => dp.date);
    const values = dataPoints.map(dp => dp.value);

    const datasets = [
        {
            label: 'Measurements',
            data: values,
            borderColor: 'rgb(59, 130, 246)',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            borderWidth: 2,
            tension: 0.1,
            fill: false,
            pointRadius: 5,
            pointHoverRadius: 7,
            pointBackgroundColor: 'rgb(59, 130, 246)',
            pointBorderColor: '#fff',
            pointBorderWidth: 2
        }
    ];

    // Add baseline line
    if (baseline !== null && baseline !== undefined) {
        datasets.push({
            label: 'Baseline',
            data: Array(dates.length).fill(baseline),
            borderColor: 'rgb(239, 68, 68)',
            borderDash: [5, 5],
            borderWidth: 2,
            fill: false,
            pointRadius: 0
        });
    }

    // Add target line
    if (target !== null && target !== undefined) {
        datasets.push({
            label: 'Target',
            data: Array(dates.length).fill(target),
            borderColor: 'rgb(34, 197, 94)',
            borderDash: [5, 5],
            borderWidth: 2,
            fill: false,
            pointRadius: 0
        });
    }

    // Add control limits if provided (from ML analyzer)
    if (controlLimits) {
        if (controlLimits.ucl) {
            datasets.push({
                label: 'Upper Control Limit (UCL)',
                data: Array(dates.length).fill(controlLimits.ucl),
                borderColor: 'rgb(249, 115, 22)',
                borderDash: [10, 5],
                borderWidth: 1.5,
                fill: false,
                pointRadius: 0
            });
        }
        if (controlLimits.lcl) {
            datasets.push({
                label: 'Lower Control Limit (LCL)',
                data: Array(dates.length).fill(controlLimits.lcl),
                borderColor: 'rgb(249, 115, 22)',
                borderDash: [10, 5],
                borderWidth: 1.5,
                fill: false,
                pointRadius: 0
            });
        }
        if (controlLimits.mean) {
            datasets.push({
                label: 'Mean',
                data: Array(dates.length).fill(controlLimits.mean),
                borderColor: 'rgb(168, 85, 247)',
                borderDash: [2, 2],
                borderWidth: 1,
                fill: false,
                pointRadius: 0
            });
        }
    }

    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                title: {
                    display: true,
                    text: 'PDSA Run Chart',
                    font: { size: 16, weight: 'bold' }
                },
                legend: {
                    position: 'top',
                    labels: { usePointStyle: true }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            label += context.parsed.y.toFixed(2) + ' ' + unit;
                            return label;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    title: {
                        display: true,
                        text: 'Value (' + unit + ')'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Date'
                    }
                }
            }
        }
    });
}

/**
 * Create a multi-cycle comparison chart
 * @param {string} canvasId - Canvas element ID
 * @param {Array} cycles - Array of cycle objects with data
 */
function createMultiCycleChart(canvasId, cycles) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    const datasets = cycles.map((cycle, index) => {
        const colors = [
            'rgb(59, 130, 246)',    // Blue
            'rgb(34, 197, 94)',     // Green
            'rgb(249, 115, 22)',    // Orange
            'rgb(168, 85, 247)',    // Purple
            'rgb(236, 72, 153)',    // Pink
            'rgb(14, 165, 233)'     // Cyan
        ];
        const color = colors[index % colors.length];

        return {
            label: `Cycle ${cycle.cycle_number}`,
            data: cycle.data_points.map(dp => ({ x: dp.date, y: dp.value })),
            borderColor: color,
            backgroundColor: color.replace('rgb', 'rgba').replace(')', ', 0.1)'),
            borderWidth: 2,
            tension: 0.1,
            fill: false,
            pointRadius: 4,
            pointHoverRadius: 6
        };
    });

    return new Chart(ctx, {
        type: 'line',
        data: { datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Multi-Cycle Comparison',
                    font: { size: 16, weight: 'bold' }
                },
                legend: {
                    position: 'top'
                }
            },
            scales: {
                x: {
                    type: 'time',
                    time: { unit: 'day' },
                    title: { display: true, text: 'Date' }
                },
                y: {
                    title: { display: true, text: 'Value' }
                }
            }
        }
    });
}

/**
 * Create dashboard pie chart for project status distribution
 * @param {string} canvasId - Canvas element ID
 * @param {Object} statusCounts - Object with status counts
 */
function createStatusPieChart(canvasId, statusCounts) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    const labels = Object.keys(statusCounts);
    const data = Object.values(statusCounts);
    const colors = [
        'rgb(59, 130, 246)',    // Blue - Active
        'rgb(251, 191, 36)',    // Yellow - Planning
        'rgb(34, 197, 94)',     // Green - Completed
        'rgb(239, 68, 68)',     // Red - On Hold
        'rgb(107, 114, 128)'    // Gray - Abandoned
    ];

    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Project Status Distribution',
                    font: { size: 16, weight: 'bold' }
                },
                legend: {
                    position: 'right'
                }
            }
        }
    });
}

/**
 * Create trend chart showing success rates over time
 * @param {string} canvasId - Canvas element ID
 * @param {Array} monthlyData - Array of {month, success_rate} objects
 */
function createTrendChart(canvasId, monthlyData) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: monthlyData.map(d => d.month),
            datasets: [{
                label: 'Success Rate (%)',
                data: monthlyData.map(d => d.success_rate),
                borderColor: 'rgb(34, 197, 94)',
                backgroundColor: 'rgba(34, 197, 94, 0.1)',
                borderWidth: 3,
                tension: 0.4,
                fill: true,
                pointRadius: 5,
                pointHoverRadius: 7,
                pointBackgroundColor: 'rgb(34, 197, 94)',
                pointBorderColor: '#fff',
                pointBorderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Success Rate Trends',
                    font: { size: 16, weight: 'bold' }
                },
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    title: {
                        display: true,
                        text: 'Success Rate (%)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Month'
                    }
                }
            }
        }
    });
}

/**
 * Create bar chart for quality domain distribution
 * @param {string} canvasId - Canvas element ID
 * @param {Object} domainCounts - Object with domain counts
 */
function createDomainBarChart(canvasId, domainCounts) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return null;

    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: Object.keys(domainCounts),
            datasets: [{
                label: 'Number of Projects',
                data: Object.values(domainCounts),
                backgroundColor: [
                    'rgba(59, 130, 246, 0.8)',
                    'rgba(34, 197, 94, 0.8)',
                    'rgba(249, 115, 22, 0.8)',
                    'rgba(168, 85, 247, 0.8)',
                    'rgba(236, 72, 153, 0.8)',
                    'rgba(14, 165, 233, 0.8)'
                ],
                borderColor: [
                    'rgb(59, 130, 246)',
                    'rgb(34, 197, 94)',
                    'rgb(249, 115, 22)',
                    'rgb(168, 85, 247)',
                    'rgb(236, 72, 153)',
                    'rgb(14, 165, 233)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Projects by Quality Domain',
                    font: { size: 16, weight: 'bold' }
                },
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { stepSize: 1 },
                    title: {
                        display: true,
                        text: 'Number of Projects'
                    }
                }
            }
        }
    });
}

/**
 * Export chart to PNG image
 * @param {Chart} chartInstance - Chart.js instance
 * @param {string} filename - Filename for download
 */
function exportChartToPNG(chartInstance, filename = 'chart.png') {
    const url = chartInstance.toBase64Image();
    const link = document.createElement('a');
    link.download = filename;
    link.href = url;
    link.click();
}

/**
 * Add statistical annotations to chart (special causes, trends)
 * @param {Chart} chartInstance - Chart.js instance
 * @param {Array} annotations - Array of annotation objects
 */
function addStatisticalAnnotations(chartInstance, annotations) {
    if (!annotations || annotations.length === 0) return;

    const plugin = {
        id: 'statisticalAnnotations',
        afterDraw: (chart) => {
            const ctx = chart.ctx;
            const yAxis = chart.scales.y;
            const xAxis = chart.scales.x;

            annotations.forEach(annotation => {
                if (annotation.type === 'special_cause') {
                    // Mark special cause variation
                    const x = xAxis.getPixelForValue(annotation.index);
                    const y = yAxis.getPixelForValue(annotation.value);
                    
                    ctx.save();
                    ctx.fillStyle = 'rgba(239, 68, 68, 0.3)';
                    ctx.beginPath();
                    ctx.arc(x, y, 12, 0, 2 * Math.PI);
                    ctx.fill();
                    ctx.restore();
                } else if (annotation.type === 'trend') {
                    // Draw trend arrow
                    const startX = xAxis.getPixelForValue(annotation.start_index);
                    const endX = xAxis.getPixelForValue(annotation.end_index);
                    const y = yAxis.getPixelForValue(annotation.value);
                    
                    ctx.save();
                    ctx.strokeStyle = annotation.direction === 'up' ? 'rgb(34, 197, 94)' : 'rgb(239, 68, 68)';
                    ctx.lineWidth = 3;
                    ctx.beginPath();
                    ctx.moveTo(startX, y);
                    ctx.lineTo(endX, y);
                    ctx.stroke();
                    ctx.restore();
                }
            });
        }
    };

    chartInstance.options.plugins.push(plugin);
    chartInstance.update();
}

// Export functions for use in templates
window.PDSACharts = {
    createRunChart,
    createMultiCycleChart,
    createStatusPieChart,
    createTrendChart,
    createDomainBarChart,
    exportChartToPNG,
    addStatisticalAnnotations
};
