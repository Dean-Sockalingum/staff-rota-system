/**
 * Integrated TQM Dashboard Charts
 * Chart.js visualizations for Module 7
 * 
 * Charts:
 * 1. Incident Trend Line Chart (30-day rolling)
 * 2. Risk Distribution Doughnut Chart
 * 3. Training Completion Bar Chart
 * 4. PDSA Success Rate Line Chart
 * 5. QIA Closure Trend Line Chart
 */

// Chart color palette (Scottish care theme)
const CHART_COLORS = {
    primary: '#1a4d7a',
    success: '#28a745',
    warning: '#ffc107',
    danger: '#dc3545',
    info: '#17a2b8',
    secondary: '#6c757d',
    light: '#f8f9fa',
    dark: '#343a40'
};

// Common chart options
const commonOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: {
            display: true,
            position: 'top',
        }
    }
};

/**
 * Initialize all charts when DOM is ready
 */
document.addEventListener('DOMContentLoaded', function() {
    initializeIncidentTrendChart();
    initializeRiskDistributionChart();
    initializeTrainingCompletionChart();
    initializePDSASuccessChart();
    initializeQIAClosureTrendChart();
});

/**
 * 1. Incident Trend Chart (30-day rolling)
 * Shows incident volumes over the last 30 days
 */
function initializeIncidentTrendChart() {
    const ctx = document.getElementById('incidentTrendChart');
    if (!ctx) return;
    
    // Get data from page context
    const incidentData = JSON.parse(document.getElementById('incident-trend-data').textContent);
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: incidentData.labels,
            datasets: [{
                label: 'Total Incidents',
                data: incidentData.total,
                borderColor: CHART_COLORS.primary,
                backgroundColor: 'rgba(26, 77, 122, 0.1)',
                fill: true,
                tension: 0.4
            }, {
                label: 'High Severity',
                data: incidentData.high_severity,
                borderColor: CHART_COLORS.danger,
                backgroundColor: 'rgba(220, 53, 69, 0.1)',
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            ...commonOptions,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Incident Trends (Last 30 Days)',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                }
            }
        }
    });
}

/**
 * 2. Risk Distribution Doughnut Chart
 * Shows breakdown of risks by priority level
 */
function initializeRiskDistributionChart() {
    const ctx = document.getElementById('riskDistributionChart');
    if (!ctx) return;
    
    // Get data from page context
    const riskData = JSON.parse(document.getElementById('risk-distribution-data').textContent);
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Critical', 'High', 'Medium', 'Low'],
            datasets: [{
                data: [
                    riskData.critical,
                    riskData.high,
                    riskData.medium,
                    riskData.low
                ],
                backgroundColor: [
                    CHART_COLORS.danger,
                    CHART_COLORS.warning,
                    CHART_COLORS.info,
                    CHART_COLORS.success
                ],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            ...commonOptions,
            plugins: {
                title: {
                    display: true,
                    text: 'Risk Distribution by Priority',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                },
                legend: {
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * 3. Training Completion Bar Chart
 * Shows completion rates for mandatory training courses
 */
function initializeTrainingCompletionChart() {
    const ctx = document.getElementById('trainingCompletionChart');
    if (!ctx) return;
    
    // Get data from page context
    const trainingData = JSON.parse(document.getElementById('training-completion-data').textContent);
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: trainingData.courses,
            datasets: [{
                label: 'Completion Rate (%)',
                data: trainingData.completion_rates,
                backgroundColor: trainingData.completion_rates.map(rate => {
                    if (rate >= 90) return CHART_COLORS.success;
                    if (rate >= 75) return CHART_COLORS.info;
                    if (rate >= 50) return CHART_COLORS.warning;
                    return CHART_COLORS.danger;
                }),
                borderColor: trainingData.completion_rates.map(rate => {
                    if (rate >= 90) return CHART_COLORS.success;
                    if (rate >= 75) return CHART_COLORS.info;
                    if (rate >= 50) return CHART_COLORS.warning;
                    return CHART_COLORS.danger;
                }),
                borderWidth: 1
            }]
        },
        options: {
            ...commonOptions,
            indexAxis: 'y', // Horizontal bars
            scales: {
                x: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'Mandatory Training Completion Rates',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                },
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Completion: ${context.parsed.x}%`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * 4. PDSA Success Rate Over Time
 * Shows trends in PDSA project success rates
 */
function initializePDSASuccessChart() {
    const ctx = document.getElementById('pdsaSuccessChart');
    if (!ctx) return;
    
    // Get data from page context
    const pdsaData = JSON.parse(document.getElementById('pdsa-success-data').textContent);
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: pdsaData.months,
            datasets: [{
                label: 'Success Rate (%)',
                data: pdsaData.success_rates,
                borderColor: CHART_COLORS.success,
                backgroundColor: 'rgba(40, 167, 69, 0.1)',
                fill: true,
                tension: 0.4,
                pointRadius: 5,
                pointHoverRadius: 7
            }]
        },
        options: {
            ...commonOptions,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'PDSA Success Rate Trend (6 Months)',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Success Rate: ${context.parsed.y.toFixed(1)}%`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * 5. QIA Closure Trend Chart
 * Shows QIA closure rates over time
 */
function initializeQIAClosureTrendChart() {
    const ctx = document.getElementById('qiaClosureTrendChart');
    if (!ctx) return;
    
    // Get data from page context
    const qiaData = JSON.parse(document.getElementById('qia-closure-data').textContent);
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: qiaData.months,
            datasets: [{
                label: 'QIAs Created',
                data: qiaData.created,
                borderColor: CHART_COLORS.info,
                backgroundColor: 'rgba(23, 162, 184, 0.1)',
                fill: false,
                tension: 0.4
            }, {
                label: 'QIAs Closed',
                data: qiaData.closed,
                borderColor: CHART_COLORS.success,
                backgroundColor: 'rgba(40, 167, 69, 0.1)',
                fill: false,
                tension: 0.4
            }]
        },
        options: {
            ...commonOptions,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            },
            plugins: {
                title: {
                    display: true,
                    text: 'QIA Creation vs Closure Trend (6 Months)',
                    font: {
                        size: 16,
                        weight: 'bold'
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                }
            }
        }
    });
}

/**
 * Helper function to format dates for chart labels
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-GB', { day: 'numeric', month: 'short' });
}

/**
 * Helper function to generate last N days labels
 */
function generateDaysLabels(days) {
    const labels = [];
    const today = new Date();
    for (let i = days - 1; i >= 0; i--) {
        const date = new Date(today);
        date.setDate(date.getDate() - i);
        labels.push(formatDate(date));
    }
    return labels;
}

/**
 * Helper function to generate last N months labels
 */
function generateMonthsLabels(months) {
    const labels = [];
    const today = new Date();
    for (let i = months - 1; i >= 0; i--) {
        const date = new Date(today);
        date.setMonth(date.getMonth() - i);
        labels.push(date.toLocaleDateString('en-GB', { month: 'short', year: 'numeric' }));
    }
    return labels;
}
