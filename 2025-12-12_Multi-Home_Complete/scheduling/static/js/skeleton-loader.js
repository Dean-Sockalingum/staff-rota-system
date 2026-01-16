/**
 * Skeleton Loading State Manager
 * ==============================
 * Utilities for showing/hiding skeleton loading states dynamically.
 * 
 * Usage:
 * 
 * // Show skeleton while loading
 * SkeletonLoader.show('#content-area', 'widget');
 * 
 * // Hide skeleton and show content
 * SkeletonLoader.hide('#content-area');
 * 
 * // Replace skeleton with actual content
 * SkeletonLoader.replace('#content-area', actualContentHTML);
 * 
 * // Show table skeleton with custom rows
 * SkeletonLoader.show('#table-container', 'table', { rows: 10 });
 */

const SkeletonLoader = {
    /**
     * Skeleton templates for different component types
     */
    templates: {
        widget: `
            <div class="skeleton-widget" aria-busy="true" role="status" aria-label="Loading widget">
                <div class="skeleton-widget-header">
                    <div class="skeleton skeleton-text skeleton-text-50"></div>
                    <div class="skeleton skeleton-badge"></div>
                </div>
                <div class="skeleton skeleton-widget-stat"></div>
                <div class="skeleton skeleton-text skeleton-text-75"></div>
                <div class="skeleton skeleton-text skeleton-text-90"></div>
                <div class="skeleton skeleton-text skeleton-text-50"></div>
            </div>
        `,
        
        card: `
            <div class="skeleton-card" aria-busy="true" role="status" aria-label="Loading content">
                <div class="skeleton-card-header">
                    <div class="skeleton skeleton-avatar"></div>
                    <div style="flex: 1;">
                        <div class="skeleton skeleton-text skeleton-text-50"></div>
                        <div class="skeleton skeleton-text skeleton-text-sm skeleton-text-75"></div>
                    </div>
                </div>
                <div class="skeleton-card-body">
                    <div class="skeleton skeleton-text skeleton-text-full"></div>
                    <div class="skeleton skeleton-text skeleton-text-90"></div>
                    <div class="skeleton skeleton-text skeleton-text-75"></div>
                </div>
            </div>
        `,
        
        table: (rows = 5) => {
            let rowsHTML = '';
            for (let i = 0; i < rows; i++) {
                rowsHTML += `
                    <tr class="skeleton-table-row">
                        <td><div class="skeleton skeleton-table-cell skeleton-text-75"></div></td>
                        <td><div class="skeleton skeleton-table-cell skeleton-text-90"></div></td>
                        <td><div class="skeleton skeleton-table-cell skeleton-text-50"></div></td>
                        <td><div class="skeleton skeleton-table-cell skeleton-text-25"></div></td>
                    </tr>
                `;
            }
            return `
                <div class="table-responsive" aria-busy="true" role="status" aria-label="Loading table">
                    <table class="skeleton-table table">
                        <thead class="skeleton-table-header">
                            <tr>
                                <th><div class="skeleton skeleton-text"></div></th>
                                <th><div class="skeleton skeleton-text"></div></th>
                                <th><div class="skeleton skeleton-text"></div></th>
                                <th><div class="skeleton skeleton-text"></div></th>
                            </tr>
                        </thead>
                        <tbody>${rowsHTML}</tbody>
                    </table>
                </div>
            `;
        },
        
        list: (items = 5) => {
            let itemsHTML = '';
            for (let i = 0; i < items; i++) {
                itemsHTML += `
                    <div class="skeleton-list-item">
                        <div class="skeleton skeleton-avatar-sm"></div>
                        <div class="skeleton-list-item-content">
                            <div class="skeleton skeleton-text skeleton-text-75"></div>
                            <div class="skeleton skeleton-text skeleton-text-sm skeleton-text-50"></div>
                        </div>
                        <div class="skeleton skeleton-badge"></div>
                    </div>
                `;
            }
            return `<div class="skeleton-list" aria-busy="true" role="status" aria-label="Loading list">${itemsHTML}</div>`;
        },
        
        'stat-card': `
            <div class="skeleton-stat-card" aria-busy="true" role="status" aria-label="Loading statistics">
                <div class="skeleton skeleton-text skeleton-text-sm skeleton-text-50"></div>
                <div class="skeleton skeleton-heading"></div>
                <div class="skeleton skeleton-text skeleton-text-75"></div>
            </div>
        `,
        
        'shift-card': `
            <div class="skeleton-shift-card" aria-busy="true" role="status" aria-label="Loading shift">
                <div class="skeleton-shift-header">
                    <div class="skeleton skeleton-text skeleton-text-50"></div>
                    <div class="skeleton skeleton-badge"></div>
                </div>
                <div class="skeleton-shift-body">
                    <div class="skeleton skeleton-text skeleton-text-75"></div>
                    <div class="skeleton skeleton-text skeleton-text-90"></div>
                    <div class="skeleton skeleton-text skeleton-text-50"></div>
                </div>
            </div>
        `,
        
        chart: `
            <div class="skeleton skeleton-chart" aria-busy="true" role="status" aria-label="Loading chart">
                <div class="skeleton skeleton-text skeleton-text-50" style="position: absolute; top: 16px; left: 16px;"></div>
            </div>
        `,
        
        text: `
            <div aria-busy="true" role="status" aria-label="Loading">
                <div class="skeleton skeleton-text skeleton-text-full"></div>
                <div class="skeleton skeleton-text skeleton-text-90"></div>
                <div class="skeleton skeleton-text skeleton-text-75"></div>
            </div>
        `
    },

    /**
     * Show skeleton loading state in a container
     * @param {string} selector - CSS selector for the container
     * @param {string} type - Type of skeleton (widget, card, table, list, etc.)
     * @param {object} options - Optional parameters (rows for table, items for list)
     */
    show(selector, type = 'text', options = {}) {
        const container = document.querySelector(selector);
        if (!container) {
            console.warn(`SkeletonLoader: Container not found: ${selector}`);
            return;
        }

        // Store original content
        if (!container.dataset.skeletonOriginal) {
            container.dataset.skeletonOriginal = container.innerHTML;
        }

        // Get template
        let template = this.templates[type];
        
        // Handle templates that are functions (table, list)
        if (typeof template === 'function') {
            const count = options.rows || options.items || 5;
            template = template(count);
        }

        // Insert skeleton
        container.innerHTML = template || this.templates.text;
        container.classList.add('skeleton-active');
    },

    /**
     * Hide skeleton and restore original content
     * @param {string} selector - CSS selector for the container
     */
    hide(selector) {
        const container = document.querySelector(selector);
        if (!container) {
            console.warn(`SkeletonLoader: Container not found: ${selector}`);
            return;
        }

        if (container.dataset.skeletonOriginal) {
            container.innerHTML = container.dataset.skeletonOriginal;
            delete container.dataset.skeletonOriginal;
        }
        
        container.classList.remove('skeleton-active');
    },

    /**
     * Replace skeleton with new content
     * @param {string} selector - CSS selector for the container
     * @param {string} content - New HTML content
     */
    replace(selector, content) {
        const container = document.querySelector(selector);
        if (!container) {
            console.warn(`SkeletonLoader: Container not found: ${selector}`);
            return;
        }

        // Fade out skeleton, fade in content
        container.style.opacity = '0';
        container.style.transition = 'opacity 0.3s ease';

        setTimeout(() => {
            container.innerHTML = content;
            delete container.dataset.skeletonOriginal;
            container.classList.remove('skeleton-active');
            container.style.opacity = '1';
        }, 300);
    },

    /**
     * Show skeleton for multiple containers
     * @param {Array} configs - Array of {selector, type, options}
     */
    showMultiple(configs) {
        configs.forEach(config => {
            this.show(config.selector, config.type, config.options);
        });
    },

    /**
     * Hide skeleton for multiple containers
     * @param {Array} selectors - Array of CSS selectors
     */
    hideMultiple(selectors) {
        selectors.forEach(selector => {
            this.hide(selector);
        });
    },

    /**
     * Wrap async function with skeleton loading state
     * @param {string} selector - CSS selector for the container
     * @param {string} type - Skeleton type
     * @param {Function} asyncFn - Async function to execute
     * @param {object} options - Skeleton options
     * @returns {Promise} - Result of asyncFn
     */
    async wrap(selector, type, asyncFn, options = {}) {
        this.show(selector, type, options);
        try {
            const result = await asyncFn();
            return result;
        } finally {
            this.hide(selector);
        }
    }
};

// Export for use in modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SkeletonLoader;
}

// Add to window for global access
if (typeof window !== 'undefined') {
    window.SkeletonLoader = SkeletonLoader;
}
