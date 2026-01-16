/**
 * Interactive Tour System
 * Provides guided tours with spotlight effects and tooltips
 */

class InteractiveTour {
    constructor(steps, options = {}) {
        this.steps = steps;
        this.currentStep = 0;
        this.options = {
            onComplete: options.onComplete || (() => {}),
            onSkip: options.onSkip || (() => {}),
            highlightPadding: options.highlightPadding || 10,
            ...options
        };
        
        this.overlay = null;
        this.spotlight = null;
        this.tooltip = null;
        
        this.init();
    }
    
    init() {
        // Create overlay
        this.overlay = document.createElement('div');
        this.overlay.className = 'tour-overlay';
        document.body.appendChild(this.overlay);
        
        // Create spotlight
        this.spotlight = document.createElement('div');
        this.spotlight.className = 'tour-spotlight';
        document.body.appendChild(this.spotlight);
        
        // Create tooltip
        this.tooltip = document.createElement('div');
        this.tooltip.className = 'tour-tooltip';
        document.body.appendChild(this.tooltip);
    }
    
    start() {
        this.overlay.classList.add('active');
        this.showStep(0);
    }
    
    showStep(stepIndex) {
        if (stepIndex >= this.steps.length) {
            this.complete();
            return;
        }
        
        this.currentStep = stepIndex;
        const step = this.steps[stepIndex];
        
        // Highlight element
        if (step.element) {
            const element = document.querySelector(step.element);
            if (element) {
                this.highlightElement(element);
                
                // Scroll element into view
                element.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        } else {
            // Center tooltip if no element
            this.spotlight.style.display = 'none';
        }
        
        // Show tooltip
        this.showTooltip(step);
    }
    
    highlightElement(element) {
        const rect = element.getBoundingClientRect();
        const padding = this.options.highlightPadding;
        
        this.spotlight.style.display = 'block';
        this.spotlight.style.top = `${rect.top - padding + window.scrollY}px`;
        this.spotlight.style.left = `${rect.left - padding}px`;
        this.spotlight.style.width = `${rect.width + (padding * 2)}px`;
        this.spotlight.style.height = `${rect.height + (padding * 2)}px`;
    }
    
    showTooltip(step) {
        // Build tooltip content
        this.tooltip.innerHTML = `
            <h3>${step.title}</h3>
            <p>${step.description}</p>
            ${step.action ? `
                <div class="tour-action">
                    <a href="${step.actionUrl}" class="btn btn-sm btn-primary">
                        ${step.action}
                    </a>
                </div>
            ` : ''}
            <div class="tour-controls">
                <span class="tour-step-indicator">
                    Step ${this.currentStep + 1} of ${this.steps.length}
                </span>
                <div>
                    ${this.currentStep > 0 ? '<button class="btn btn-sm btn-outline-secondary tour-btn-prev">Back</button>' : ''}
                    <button class="btn btn-sm btn-outline-secondary tour-btn-skip">Skip</button>
                    <button class="btn btn-sm btn-primary tour-btn-next">
                        ${this.currentStep < this.steps.length - 1 ? 'Next' : 'Finish'}
                    </button>
                </div>
            </div>
        `;
        
        // Position tooltip
        this.positionTooltip(step.position || 'bottom');
        
        // Attach event listeners
        const prevBtn = this.tooltip.querySelector('.tour-btn-prev');
        const nextBtn = this.tooltip.querySelector('.tour-btn-next');
        const skipBtn = this.tooltip.querySelector('.tour-btn-skip');
        
        if (prevBtn) {
            prevBtn.addEventListener('click', () => this.prev());
        }
        
        nextBtn.addEventListener('click', () => this.next());
        skipBtn.addEventListener('click', () => this.skip());
    }
    
    positionTooltip(position) {
        this.tooltip.className = `tour-tooltip position-${position}`;
        
        if (this.spotlight.style.display === 'none') {
            // Center on screen
            this.tooltip.style.top = '50%';
            this.tooltip.style.left = '50%';
            this.tooltip.style.transform = 'translate(-50%, -50%)';
        } else {
            // Position relative to spotlight
            const spotlightRect = this.spotlight.getBoundingClientRect();
            
            switch (position) {
                case 'bottom':
                    this.tooltip.style.top = `${spotlightRect.bottom + 20}px`;
                    this.tooltip.style.left = `${spotlightRect.left + (spotlightRect.width / 2)}px`;
                    this.tooltip.style.transform = 'translateX(-50%)';
                    break;
                case 'top':
                    this.tooltip.style.bottom = `${window.innerHeight - spotlightRect.top + 20}px`;
                    this.tooltip.style.left = `${spotlightRect.left + (spotlightRect.width / 2)}px`;
                    this.tooltip.style.transform = 'translateX(-50%)';
                    break;
                case 'left':
                    this.tooltip.style.top = `${spotlightRect.top}px`;
                    this.tooltip.style.right = `${window.innerWidth - spotlightRect.left + 20}px`;
                    break;
                case 'right':
                    this.tooltip.style.top = `${spotlightRect.top}px`;
                    this.tooltip.style.left = `${spotlightRect.right + 20}px`;
                    break;
                default:
                    this.tooltip.style.top = `${spotlightRect.bottom + 20}px`;
                    this.tooltip.style.left = `${spotlightRect.left}px`;
            }
        }
    }
    
    next() {
        this.showStep(this.currentStep + 1);
    }
    
    prev() {
        if (this.currentStep > 0) {
            this.showStep(this.currentStep - 1);
        }
    }
    
    skip() {
        if (confirm('Are you sure you want to skip the tour? You can restart it anytime from your settings.')) {
            this.cleanup();
            this.options.onSkip();
        }
    }
    
    complete() {
        this.cleanup();
        this.options.onComplete();
    }
    
    cleanup() {
        this.overlay.remove();
        this.spotlight.remove();
        this.tooltip.remove();
    }
}

// Helper function to create tour from data attributes
function initTourFromData() {
    const tourData = document.getElementById('tour-data');
    if (!tourData) return;
    
    try {
        const steps = JSON.parse(tourData.textContent);
        const tour = new InteractiveTour(steps, {
            onComplete: () => {
                // Mark step as complete
                fetch(window.location.href, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: 'action=complete'
                }).then(() => {
                    // Redirect to next step
                    const nextUrl = tourData.dataset.nextUrl;
                    if (nextUrl) {
                        window.location.href = nextUrl;
                    }
                });
            },
            onSkip: () => {
                if (confirm('Skip the entire onboarding tour?')) {
                    fetch('/onboarding/skip/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded',
                            'X-CSRFToken': getCookie('csrftoken')
                        }
                    }).then(response => response.json())
                      .then(data => {
                          if (data.success) {
                              window.location.href = data.redirect_url;
                          }
                      });
                }
            }
        });
        
        // Auto-start tour
        setTimeout(() => tour.start(), 500);
    } catch (e) {
        console.error('Failed to initialize tour:', e);
    }
}

// Get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Initialize on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTourFromData);
} else {
    initTourFromData();
}

// Export for use in other scripts
window.InteractiveTour = InteractiveTour;
