/**
 * Chart.js Global Configuration
 * ==============================
 * Configures Chart.js with design system colors, responsive defaults,
 * and accessibility settings for dashboard visualizations.
 * 
 * This file is automatically loaded in base.html after Chart.js library.
 */

(function() {
    'use strict';

    // Design System Colors (from design-system.css)
    const colors = {
        primary: {
            50: '#E5F0FF',
            100: '#CCE0FF',
            200: '#99C2FF',
            300: '#66A3FF',
            400: '#3385FF',
            500: '#0066FF', // Primary brand color
            600: '#0052CC',
            700: '#003D99',
            800: '#002966',
            900: '#001433'
        },
        secondary: {
            50: '#E5F9F0',
            100: '#CCF3E0',
            200: '#99E7C2',
            300: '#66DBA3',
            400: '#33CF85',
            500: '#00C853', // Secondary brand color
            600: '#00A043',
            700: '#007832',
            800: '#005022',
            900: '#002811'
        },
        accent: {
            50: '#FFF3E5',
            100: '#FFE7CC',
            200: '#FFCF99',
            300: '#FFB766',
            400: '#FF9F33',
            500: '#FF6F00', // Accent brand color
            600: '#CC5900',
            700: '#994300',
            800: '#662C00',
            900: '#331600'
        },
        neutral: {
            50: '#F8F9FA',
            100: '#F1F3F5',
            200: '#E9ECEF',
            300: '#DEE2E6',
            400: '#CED4DA',
            500: '#ADB5BD',
            600: '#6C757D',
            700: '#495057',
            800: '#343A40',
            900: '#212529',
            white: '#FFFFFF',
            black: '#000000'
        },
        semantic: {
            success: '#10B981',
            warning: '#F59E0B',
            danger: '#EF4444',
            info: '#3B82F6'
        }
    };

    // Chart.js color palette (array for datasets)
    const chartColors = [
        colors.primary[500],
        colors.secondary[500],
        colors.accent[500],
        colors.semantic.info,
        colors.semantic.success,
        colors.semantic.warning,
        colors.semantic.danger,
        colors.primary[300],
        colors.secondary[300],
        colors.accent[300]
    ];

    // Helper to generate alpha variations
    function hexToRgba(hex, alpha = 1) {
        // Return as-is if not a string (could be a function or already rgba)
        if (typeof hex !== 'string') {
            return hex;
        }
        // Return as-is if already rgba/rgb
        if (hex.startsWith('rgba') || hex.startsWith('rgb')) {
            return hex;
        }
        // Convert hex to rgba
        const r = parseInt(hex.slice(1, 3), 16);
        const g = parseInt(hex.slice(3, 5), 16);
        const b = parseInt(hex.slice(5, 7), 16);
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }

    // Global Chart.js defaults
    Chart.defaults.font.family = 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
    Chart.defaults.font.size = 14;
    Chart.defaults.color = colors.neutral[700];
    Chart.defaults.borderColor = colors.neutral[200];
    Chart.defaults.responsive = true;
    Chart.defaults.maintainAspectRatio = false;

    // Plugin defaults for better UX
    Chart.defaults.plugins.legend.display = true;
    Chart.defaults.plugins.legend.position = 'bottom';
    Chart.defaults.plugins.legend.labels.padding = 16;
    Chart.defaults.plugins.legend.labels.usePointStyle = true;
    Chart.defaults.plugins.legend.labels.font = {
        family: 'Inter',
        size: 13,
        weight: 500
    };

    Chart.defaults.plugins.tooltip.enabled = true;
    Chart.defaults.plugins.tooltip.backgroundColor = hexToRgba(colors.neutral[900], 0.9);
    Chart.defaults.plugins.tooltip.titleColor = colors.neutral.white;
    Chart.defaults.plugins.tooltip.bodyColor = colors.neutral.white;
    Chart.defaults.plugins.tooltip.borderColor = colors.primary[500];
    Chart.defaults.plugins.tooltip.borderWidth = 1;
    Chart.defaults.plugins.tooltip.cornerRadius = 8;
    Chart.defaults.plugins.tooltip.padding = 12;
    Chart.defaults.plugins.tooltip.titleFont = {
        family: 'Inter',
        size: 14,
        weight: 600
    };
    Chart.defaults.plugins.tooltip.bodyFont = {
        family: 'Inter',
        size: 13,
        weight: 400
    };

    // Animation defaults
    Chart.defaults.animation.duration = 750;
    Chart.defaults.animation.easing = 'easeInOutQuart';

    /**
     * Chart Helper Functions
     * ======================
     */

    window.ChartHelpers = {
        colors: colors,
        chartColors: chartColors,

        /**
         * Get color from palette by index
         * @param {number} index - Color index
         * @param {number} alpha - Opacity (0-1)
         * @returns {string} RGBA color
         */
        getColor(index, alpha = 1) {
            const color = chartColors[index % chartColors.length];
            return hexToRgba(color, alpha);
        },

        /**
         * Get primary color with optional shade
         * @param {number} shade - Color shade (50-900)
         * @param {number} alpha - Opacity (0-1)
         * @returns {string} RGBA color
         */
        getPrimary(shade = 500, alpha = 1) {
            return hexToRgba(colors.primary[shade], alpha);
        },

        /**
         * Get secondary color with optional shade
         * @param {number} shade - Color shade (50-900)
         * @param {number} alpha - Opacity (0-1)
         * @returns {string} RGBA color
         */
        getSecondary(shade = 500, alpha = 1) {
            return hexToRgba(colors.secondary[shade], alpha);
        },

        /**
         * Get accent color with optional shade
         * @param {number} shade - Color shade (50-900)
         * @param {number} alpha - Opacity (0-1)
         * @returns {string} RGBA color
         */
        getAccent(shade = 500, alpha = 1) {
            return hexToRgba(colors.accent[shade], alpha);
        },

        /**
         * Get gradient for chart backgrounds
         * @param {object} ctx - Canvas context
         * @param {string} color - Hex color
         * @param {number} alpha - Opacity (0-1)
         * @returns {CanvasGradient} Gradient
         */
        getGradient(ctx, color, alpha = 0.2) {
            const gradient = ctx.createLinearGradient(0, 0, 0, ctx.canvas.height);
            gradient.addColorStop(0, hexToRgba(color, alpha));
            gradient.addColorStop(1, hexToRgba(color, 0));
            return gradient;
        },

        /**
         * Add alpha to any color
         * @param {string} color - Hex color
         * @param {number} alpha - Opacity (0-1)
         * @returns {string} RGBA color
         */
        addAlpha(color, alpha = 1) {
            return hexToRgba(color, alpha);
        },

        /**
         * Create line chart with design system styling
         * @param {string} canvasId - Canvas element ID
         * @param {object} data - Chart data
         * @param {object} options - Additional options
         * @returns {Chart} Chart instance
         */
        createLineChart(canvasId, data, options = {}) {
            const ctx = document.getElementById(canvasId).getContext('2d');
            
            // Apply gradient backgrounds to datasets
            const datasets = data.datasets.map((dataset, index) => {
                const color = dataset.borderColor || chartColors[index % chartColors.length];
                return {
                    ...dataset,
                    borderColor: color,
                    backgroundColor: this.getGradient(ctx, color, 0.2),
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true,
                    pointBackgroundColor: colors.neutral.white,
                    pointBorderColor: color,
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                    pointHoverBorderWidth: 3
                };
            });

            return new Chart(ctx, {
                type: 'line',
                data: { ...data, datasets },
                options: {
                    ...options,
                    scales: {
                        x: {
                            grid: {
                                display: false
                            },
                            ticks: {
                                font: {
                                    family: 'Inter',
                                    size: 12
                                }
                            }
                        },
                        y: {
                            beginAtZero: true,
                            grid: {
                                color: colors.neutral[200],
                                drawBorder: false
                            },
                            ticks: {
                                font: {
                                    family: 'Inter',
                                    size: 12
                                }
                            }
                        }
                    }
                }
            });
        },

        /**
         * Create bar chart with design system styling
         * @param {string} canvasId - Canvas element ID
         * @param {object} data - Chart data
         * @param {object} options - Additional options
         * @returns {Chart} Chart instance
         */
        createBarChart(canvasId, data, options = {}) {
            const ctx = document.getElementById(canvasId).getContext('2d');
            
            const datasets = data.datasets.map((dataset, index) => {
                const color = dataset.backgroundColor || chartColors[index % chartColors.length];
                return {
                    ...dataset,
                    // Don't override if backgroundColor is a function
                    backgroundColor: typeof dataset.backgroundColor === 'function' 
                        ? dataset.backgroundColor 
                        : hexToRgba(color, 0.8),
                    // Don't override if borderColor is a function
                    borderColor: typeof dataset.borderColor === 'function'
                        ? dataset.borderColor
                        : (dataset.borderColor || color),
                    borderWidth: dataset.borderWidth || 2,
                    borderRadius: 8,
                    borderSkipped: false
                };
            });

            return new Chart(ctx, {
                type: 'bar',
                data: { ...data, datasets },
                options: {
                    ...options,
                    scales: {
                        x: {
                            grid: {
                                display: false
                            },
                            ticks: {
                                font: {
                                    family: 'Inter',
                                    size: 12
                                }
                            }
                        },
                        y: {
                            beginAtZero: true,
                            grid: {
                                color: colors.neutral[200],
                                drawBorder: false
                            },
                            ticks: {
                                font: {
                                    family: 'Inter',
                                    size: 12
                                }
                            }
                        }
                    }
                }
            });
        },

        /**
         * Create doughnut chart with design system styling
         * @param {string} canvasId - Canvas element ID
         * @param {object} data - Chart data
         * @param {object} options - Additional options
         * @returns {Chart} Chart instance
         */
        createDoughnutChart(canvasId, data, options = {}) {
            const ctx = document.getElementById(canvasId).getContext('2d');
            
            const datasets = data.datasets.map((dataset, index) => {
                const bgColors = dataset.data.map((_, i) => 
                    hexToRgba(chartColors[i % chartColors.length], 0.8)
                );
                const borderColors = dataset.data.map((_, i) => 
                    chartColors[i % chartColors.length]
                );

                return {
                    ...dataset,
                    backgroundColor: bgColors,
                    borderColor: borderColors,
                    borderWidth: 2,
                    hoverBorderWidth: 3,
                    hoverOffset: 8
                };
            });

            return new Chart(ctx, {
                type: 'doughnut',
                data: { ...data, datasets },
                options: {
                    ...options,
                    cutout: '70%',
                    plugins: {
                        legend: {
                            position: 'right'
                        }
                    }
                }
            });
        },

        /**
         * Create area chart (line chart with filled area)
         * @param {string} canvasId - Canvas element ID
         * @param {object} data - Chart data
         * @param {object} options - Additional options
         * @returns {Chart} Chart instance
         */
        createAreaChart(canvasId, data, options = {}) {
            const ctx = document.getElementById(canvasId).getContext('2d');
            
            const datasets = data.datasets.map((dataset, index) => {
                const color = dataset.borderColor || chartColors[index % chartColors.length];
                return {
                    ...dataset,
                    borderColor: color,
                    backgroundColor: dataset.backgroundColor || this.getGradient(ctx, color, 0.3),
                    borderWidth: dataset.borderWidth || 2,
                    tension: dataset.tension || 0.4,
                    fill: dataset.fill !== undefined ? dataset.fill : true,
                    pointBackgroundColor: colors.neutral.white,
                    pointBorderColor: color,
                    pointBorderWidth: 2,
                    pointRadius: 3,
                    pointHoverRadius: 5,
                    pointHoverBorderWidth: 3
                };
            });

            return new Chart(ctx, {
                type: 'line',
                data: { ...data, datasets },
                options: {
                    ...options,
                    scales: {
                        ...options.scales,
                        x: {
                            ...(options.scales?.x || {}),
                            grid: {
                                display: false,
                                ...(options.scales?.x?.grid || {})
                            }
                        },
                        y: {
                            ...(options.scales?.y || {}),
                            beginAtZero: true,
                            grid: {
                                color: colors.neutral[200],
                                drawBorder: false,
                                ...(options.scales?.y?.grid || {})
                            }
                        }
                    }
                }
            });
        },

        /**
         * Create radar chart with design system styling
         * @param {string} canvasId - Canvas element ID
         * @param {object} data - Chart data
         * @param {object} options - Additional options
         * @returns {Chart} Chart instance
         */
        createRadarChart(canvasId, data, options = {}) {
            const ctx = document.getElementById(canvasId).getContext('2d');
            
            const datasets = data.datasets.map((dataset, index) => {
                const color = dataset.borderColor || chartColors[index % chartColors.length];
                return {
                    ...dataset,
                    borderColor: color,
                    backgroundColor: dataset.backgroundColor || hexToRgba(color, 0.2),
                    borderWidth: 2,
                    pointBackgroundColor: color,
                    pointBorderColor: colors.neutral.white,
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                    pointHoverBorderWidth: 3
                };
            });

            return new Chart(ctx, {
                type: 'radar',
                data: { ...data, datasets },
                options: {
                    ...options,
                    scales: {
                        r: {
                            ...(options.scales?.r || {}),
                            grid: {
                                color: colors.neutral[200],
                                ...(options.scales?.r?.grid || {})
                            },
                            angleLines: {
                                color: colors.neutral[200],
                                ...(options.scales?.r?.angleLines || {})
                            },
                            pointLabels: {
                                font: {
                                    family: 'Inter',
                                    size: 12,
                                    weight: 500
                                },
                                ...(options.scales?.r?.pointLabels || {})
                            },
                            ticks: {
                                font: {
                                    family: 'Inter',
                                    size: 11
                                },
                                ...(options.scales?.r?.ticks || {})
                            }
                        }
                    }
                }
            });
        },

        /**
         * Destroy chart instance safely
         * @param {Chart} chart - Chart instance
         */
        destroyChart(chart) {
            if (chart && typeof chart.destroy === 'function') {
                chart.destroy();
            }
        }
    };

    // Make hexToRgba available globally
    window.hexToRgba = hexToRgba;

    console.log('✅ Chart.js configured with design system colors');
})();
