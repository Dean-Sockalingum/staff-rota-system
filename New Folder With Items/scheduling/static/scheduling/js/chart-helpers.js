/**
 * ChartHelpers - Utility library for creating Chart.js charts
 * Provides simple wrapper functions for common chart types used in the Staff Rota system
 */

const ChartHelpers = {
    /**
     * Create an area chart (line chart with filled area)
     * @param {string} canvasId - ID of the canvas element
     * @param {Object} data - Chart data object with labels and datasets
     * @param {Object} options - Chart options (optional)
     * @returns {Chart} Chart.js instance
     */
    createAreaChart: function(canvasId, data, options = {}) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error(`Canvas element with ID "${canvasId}" not found`);
            return null;
        }

        const ctx = canvas.getContext('2d');
        
        // Default options for area charts
        const defaultOptions = {
            type: 'line',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        };

        // Merge custom options with defaults
        const chartOptions = {
            type: 'line',
            data: data,
            options: { ...defaultOptions, ...options }
        };

        return new Chart(ctx, chartOptions);
    },

    /**
     * Create a bar chart
     * @param {string} canvasId - ID of the canvas element
     * @param {Object} data - Chart data object with labels and datasets
     * @param {Object} options - Chart options (optional)
     * @returns {Chart} Chart.js instance
     */
    createBarChart: function(canvasId, data, options = {}) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error(`Canvas element with ID "${canvasId}" not found`);
            return null;
        }

        const ctx = canvas.getContext('2d');
        
        // Default options for bar charts
        const defaultOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        };

        // Merge custom options with defaults
        const chartOptions = {
            type: 'bar',
            data: data,
            options: { ...defaultOptions, ...options }
        };

        return new Chart(ctx, chartOptions);
    },

    /**
     * Create a doughnut chart
     * @param {string} canvasId - ID of the canvas element
     * @param {Object} data - Chart data object with labels and datasets
     * @param {Object} options - Chart options (optional)
     * @returns {Chart} Chart.js instance
     */
    createDoughnutChart: function(canvasId, data, options = {}) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error(`Canvas element with ID "${canvasId}" not found`);
            return null;
        }

        const ctx = canvas.getContext('2d');
        
        // Default options for doughnut charts
        const defaultOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.label || '';
                            if (label) {
                                label += ': ';
                            }
                            const value = context.parsed;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            label += value + ' (' + percentage + '%)';
                            return label;
                        }
                    }
                }
            }
        };

        // Merge custom options with defaults
        const chartOptions = {
            type: 'doughnut',
            data: data,
            options: { ...defaultOptions, ...options }
        };

        return new Chart(ctx, chartOptions);
    },

    /**
     * Create a radar chart
     * @param {string} canvasId - ID of the canvas element
     * @param {Object} data - Chart data object with labels and datasets
     * @param {Object} options - Chart options (optional)
     * @returns {Chart} Chart.js instance
     */
    createRadarChart: function(canvasId, data, options = {}) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error(`Canvas element with ID "${canvasId}" not found`);
            return null;
        }

        const ctx = canvas.getContext('2d');
        
        // Default options for radar charts
        const defaultOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                r: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 20
                    }
                }
            }
        };

        // Merge custom options with defaults
        const chartOptions = {
            type: 'radar',
            data: data,
            options: { ...defaultOptions, ...options }
        };

        return new Chart(ctx, chartOptions);
    },

    /**
     * Create a pie chart
     * @param {string} canvasId - ID of the canvas element
     * @param {Object} data - Chart data object with labels and datasets
     * @param {Object} options - Chart options (optional)
     * @returns {Chart} Chart.js instance
     */
    createPieChart: function(canvasId, data, options = {}) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            console.error(`Canvas element with ID "${canvasId}" not found`);
            return null;
        }

        const ctx = canvas.getContext('2d');
        
        // Default options for pie charts
        const defaultOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            let label = context.label || '';
                            if (label) {
                                label += ': ';
                            }
                            const value = context.parsed;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            label += value + ' (' + percentage + '%)';
                            return label;
                        }
                    }
                }
            }
        };

        // Merge custom options with defaults
        const chartOptions = {
            type: 'pie',
            data: data,
            options: { ...defaultOptions, ...options }
        };

        return new Chart(ctx, chartOptions);
    },

    /**
     * Destroy a chart instance
     * @param {Chart} chart - Chart.js instance to destroy
     */
    destroyChart: function(chart) {
        if (chart && typeof chart.destroy === 'function') {
            chart.destroy();
        }
    }
};

// Make ChartHelpers available globally
if (typeof window !== 'undefined') {
    window.ChartHelpers = ChartHelpers;
}
