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
    },

    /**
     * Color palette configuration
     * Using Tailwind CSS color shades
     */
    colors: {
        primary: {
            50: '#f0f9ff',
            100: '#e0f2fe',
            200: '#bae6fd',
            300: '#7dd3fc',
            400: '#38bdf8',
            500: '#0ea5e9',
            600: '#0284c7',
            700: '#0369a1',
            800: '#075985',
            900: '#0c4a6e'
        },
        secondary: {
            50: '#fdf2f8',
            100: '#fce7f3',
            200: '#fbcfe8',
            300: '#f9a8d4',
            400: '#f472b6',
            500: '#ec4899',
            600: '#db2777',
            700: '#be185d',
            800: '#9d174d',
            900: '#831843'
        },
        accent: {
            50: '#faf5ff',
            100: '#f3e8ff',
            200: '#e9d5ff',
            300: '#d8b4fe',
            400: '#c084fc',
            500: '#a855f7',
            600: '#9333ea',
            700: '#7e22ce',
            800: '#6b21a8',
            900: '#581c87'
        },
        success: {
            500: '#10b981'
        },
        warning: {
            500: '#f59e0b'
        },
        danger: {
            500: '#ef4444'
        },
        info: {
            500: '#3b82f6'
        }
    },

    /**
     * Add alpha transparency to a hex color
     * @param {string} color - Hex color code (e.g., '#0ea5e9')
     * @param {number} alpha - Alpha value between 0 and 1
     * @returns {string} RGBA color string
     */
    addAlpha: function(color, alpha) {
        // Remove # if present
        color = color.replace('#', '');
        
        // Convert to RGB
        const r = parseInt(color.substring(0, 2), 16);
        const g = parseInt(color.substring(2, 4), 16);
        const b = parseInt(color.substring(4, 6), 16);
        
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }
};

// Make ChartHelpers available globally
if (typeof window !== 'undefined') {
    window.ChartHelpers = ChartHelpers;
}
