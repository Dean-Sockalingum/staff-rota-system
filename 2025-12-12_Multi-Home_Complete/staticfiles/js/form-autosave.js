/**
 * Form Auto-Save Library - Task 57
 * Automatically saves form data to localStorage to prevent data loss
 * 
 * Usage:
 *   <form id="my-form" data-autosave="true" data-autosave-key="leave-request">
 *       ...
 *   </form>
 * 
 * Or programmatically:
 *   FormAutoSave.init('my-form', {
 *       storageKey: 'leave-request',
 *       saveInterval: 5000,  // Save every 5 seconds
 *       onSave: (data) => console.log('Saved:', data),
 *       onRestore: (data) => console.log('Restored:', data)
 *   });
 */

const FormAutoSave = (function() {
    'use strict';

    // Configuration defaults
    const defaults = {
        storagePrefix: 'staff_rota_form_',
        saveInterval: 3000,  // 3 seconds
        indicatorId: 'autosave-indicator',
        excludeFields: ['csrfmiddlewaretoken', 'submit'],
        debug: false
    };

    // Active forms being tracked
    const activeForms = new Map();

    /**
     * Initialize auto-save for a form
     * @param {string|HTMLFormElement} formSelector - Form ID or element
     * @param {Object} options - Configuration options
     */
    function init(formSelector, options = {}) {
        const form = typeof formSelector === 'string' 
            ? document.getElementById(formSelector)
            : formSelector;

        if (!form) {
            console.error('FormAutoSave: Form not found:', formSelector);
            return null;
        }

        const config = {
            ...defaults,
            ...options,
            storageKey: options.storageKey || form.dataset.autosaveKey || form.id
        };

        if (!config.storageKey) {
            console.error('FormAutoSave: No storage key provided for form');
            return null;
        }

        // Check if already initialized
        if (activeForms.has(form.id)) {
            console.warn('FormAutoSave: Form already initialized:', form.id);
            return activeForms.get(form.id);
        }

        const instance = createInstance(form, config);
        activeForms.set(form.id, instance);

        if (config.debug) {
            console.log('FormAutoSave: Initialized', form.id, config);
        }

        return instance;
    }

    /**
     * Create an auto-save instance for a form
     */
    function createInstance(form, config) {
        let saveTimer = null;
        let isDirty = false;

        const storageKey = config.storagePrefix + config.storageKey;

        // Create instance object
        const instance = {
            form,
            config,
            storageKey,

            /**
             * Save form data to localStorage
             */
            save() {
                const formData = getFormData(form, config.excludeFields);
                
                try {
                    localStorage.setItem(storageKey, JSON.stringify({
                        data: formData,
                        timestamp: new Date().toISOString(),
                        url: window.location.pathname
                    }));

                    isDirty = false;
                    updateIndicator('saved');

                    if (config.onSave) {
                        config.onSave(formData);
                    }

                    if (config.debug) {
                        console.log('FormAutoSave: Saved', storageKey, formData);
                    }
                } catch (error) {
                    console.error('FormAutoSave: Save error', error);
                    updateIndicator('error');
                }
            },

            /**
             * Restore form data from localStorage
             */
            restore() {
                try {
                    const saved = localStorage.getItem(storageKey);
                    if (!saved) {
                        if (config.debug) {
                            console.log('FormAutoSave: No saved data found');
                        }
                        return false;
                    }

                    const { data, timestamp, url } = JSON.parse(saved);

                    // Only restore if on same URL
                    if (url && url !== window.location.pathname) {
                        if (config.debug) {
                            console.log('FormAutoSave: URL mismatch, not restoring');
                        }
                        return false;
                    }

                    setFormData(form, data);
                    showRestoreNotification(timestamp);

                    if (config.onRestore) {
                        config.onRestore(data);
                    }

                    if (config.debug) {
                        console.log('FormAutoSave: Restored', storageKey, data);
                    }

                    return true;
                } catch (error) {
                    console.error('FormAutoSave: Restore error', error);
                    return false;
                }
            },

            /**
             * Clear saved data
             */
            clear() {
                try {
                    localStorage.removeItem(storageKey);
                    isDirty = false;
                    updateIndicator('cleared');

                    if (config.debug) {
                        console.log('FormAutoSave: Cleared', storageKey);
                    }
                } catch (error) {
                    console.error('FormAutoSave: Clear error', error);
                }
            },

            /**
             * Destroy auto-save instance
             */
            destroy() {
                if (saveTimer) {
                    clearInterval(saveTimer);
                }
                form.removeEventListener('input', handleInput);
                form.removeEventListener('change', handleChange);
                form.removeEventListener('submit', handleSubmit);
                activeForms.delete(form.id);

                if (config.debug) {
                    console.log('FormAutoSave: Destroyed', form.id);
                }
            }
        };

        // Event handlers
        function handleInput() {
            isDirty = true;
            updateIndicator('unsaved');
        }

        function handleChange() {
            if (isDirty) {
                instance.save();
            }
        }

        function handleSubmit() {
            // Clear saved data on successful submit
            instance.clear();
        }

        // Set up event listeners
        form.addEventListener('input', handleInput);
        form.addEventListener('change', handleChange);
        form.addEventListener('submit', handleSubmit);

        // Set up periodic save
        if (config.saveInterval > 0) {
            saveTimer = setInterval(() => {
                if (isDirty) {
                    instance.save();
                }
            }, config.saveInterval);
        }

        // Try to restore saved data
        instance.restore();

        // Add visual indicator
        addIndicator(form, config.indicatorId);

        return instance;
    }

    /**
     * Get form data as object
     */
    function getFormData(form, excludeFields = []) {
        const formData = new FormData(form);
        const data = {};

        for (const [key, value] of formData.entries()) {
            if (!excludeFields.includes(key)) {
                // Handle multiple values (checkboxes, multi-select)
                if (data[key]) {
                    if (Array.isArray(data[key])) {
                        data[key].push(value);
                    } else {
                        data[key] = [data[key], value];
                    }
                } else {
                    data[key] = value;
                }
            }
        }

        return data;
    }

    /**
     * Set form data from object
     */
    function setFormData(form, data) {
        for (const [key, value] of Object.entries(data)) {
            const field = form.elements[key];
            if (!field) continue;

            if (field.type === 'checkbox' || field.type === 'radio') {
                if (Array.isArray(value)) {
                    // Handle checkbox groups
                    const fields = form.querySelectorAll(`[name="${key}"]`);
                    fields.forEach(f => {
                        f.checked = value.includes(f.value);
                    });
                } else {
                    field.checked = value === field.value || value === 'on';
                }
            } else if (field.tagName === 'SELECT' && field.multiple) {
                // Handle multi-select
                const values = Array.isArray(value) ? value : [value];
                Array.from(field.options).forEach(option => {
                    option.selected = values.includes(option.value);
                });
            } else {
                // Handle text, textarea, select, etc.
                field.value = value;
            }
        }
    }

    /**
     * Add auto-save indicator to form
     */
    function addIndicator(form, indicatorId) {
        // Check if indicator already exists
        if (form.querySelector(`#${indicatorId}`)) {
            return;
        }

        const indicator = document.createElement('div');
        indicator.id = indicatorId;
        indicator.className = 'autosave-indicator';
        indicator.innerHTML = `
            <span class="autosave-icon"></span>
            <span class="autosave-text">Draft auto-save enabled</span>
        `;

        // Insert indicator at top of form
        form.insertBefore(indicator, form.firstChild);
    }

    /**
     * Update indicator status
     */
    function updateIndicator(status) {
        const indicators = document.querySelectorAll('.autosave-indicator');
        indicators.forEach(indicator => {
            const icon = indicator.querySelector('.autosave-icon');
            const text = indicator.querySelector('.autosave-text');

            indicator.className = 'autosave-indicator autosave-' + status;

            switch (status) {
                case 'saved':
                    icon.textContent = '✓';
                    text.textContent = `Draft saved at ${new Date().toLocaleTimeString()}`;
                    break;
                case 'unsaved':
                    icon.textContent = '○';
                    text.textContent = 'Unsaved changes...';
                    break;
                case 'error':
                    icon.textContent = '✗';
                    text.textContent = 'Error saving draft';
                    break;
                case 'cleared':
                    icon.textContent = '✓';
                    text.textContent = 'Draft cleared';
                    break;
            }
        });
    }

    /**
     * Show notification that data was restored
     */
    function showRestoreNotification(timestamp) {
        const date = new Date(timestamp);
        const timeAgo = getTimeAgo(date);

        const notification = document.createElement('div');
        notification.className = 'alert alert-info alert-dismissible fade show autosave-restore-alert';
        notification.innerHTML = `
            <strong>Draft Restored:</strong> Your previous input from ${timeAgo} has been restored.
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        // Insert at top of page
        const container = document.querySelector('.container, .container-fluid');
        if (container) {
            container.insertBefore(notification, container.firstChild);
        }

        // Auto-dismiss after 10 seconds
        setTimeout(() => {
            notification.remove();
        }, 10000);
    }

    /**
     * Get human-readable time ago
     */
    function getTimeAgo(date) {
        const seconds = Math.floor((new Date() - date) / 1000);

        if (seconds < 60) return 'just now';
        if (seconds < 3600) return Math.floor(seconds / 60) + ' minutes ago';
        if (seconds < 86400) return Math.floor(seconds / 3600) + ' hours ago';
        return Math.floor(seconds / 86400) + ' days ago';
    }

    /**
     * Auto-initialize all forms with data-autosave attribute
     */
    function autoInit() {
        document.querySelectorAll('form[data-autosave="true"]').forEach(form => {
            const options = {
                storageKey: form.dataset.autosaveKey || form.id,
                saveInterval: parseInt(form.dataset.autosaveInterval) || defaults.saveInterval
            };

            init(form, options);
        });
    }

    // Auto-initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', autoInit);
    } else {
        autoInit();
    }

    // Public API
    return {
        init,
        get: (formId) => activeForms.get(formId),
        destroy: (formId) => {
            const instance = activeForms.get(formId);
            if (instance) {
                instance.destroy();
            }
        },
        clearAll: () => {
            activeForms.forEach(instance => instance.clear());
        }
    };
})();

// Make available globally
window.FormAutoSave = FormAutoSave;
