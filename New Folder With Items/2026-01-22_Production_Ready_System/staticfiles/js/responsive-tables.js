/**
 * Responsive Tables JavaScript
 * Enhances tables with sorting, filtering, and mobile-friendly features
 * Version: 1.0
 */

(function() {
    'use strict';
    
    /**
     * Initialize all responsive tables on page load
     */
    function initResponsiveTables() {
        // Auto-convert tables with .table class to card layout on mobile
        const tables = document.querySelectorAll('.table');
        tables.forEach(table => {
            if (!table.classList.contains('table-no-mobile')) {
                makeTableResponsive(table);
            }
        });
        
        // Initialize sortable headers
        initSortableHeaders();
        
        // Initialize table search
        initTableSearch();
        
        // Add scroll indicators
        addScrollIndicators();
    }
    
    /**
     * Make a table responsive by adding data-label attributes
     */
    function makeTableResponsive(table) {
        const headers = table.querySelectorAll('thead th');
        const rows = table.querySelectorAll('tbody tr');
        
        // Add card-mobile class for automatic card layout
        if (!table.classList.contains('table-scroll-mobile')) {
            table.classList.add('table-card-mobile', 'table-mobile-optimized');
        }
        
        // Add data-label attributes to each cell for mobile view
        rows.forEach(row => {
            const cells = row.querySelectorAll('td');
            cells.forEach((cell, index) => {
                if (headers[index]) {
                    const headerText = headers[index].textContent.trim();
                    cell.setAttribute('data-label', headerText);
                }
            });
        });
    }
    
    /**
     * Initialize sortable table headers
     */
    function initSortableHeaders() {
        const sortableHeaders = document.querySelectorAll('.sortable-header');
        
        sortableHeaders.forEach(header => {
            header.addEventListener('click', function() {
                const table = this.closest('table');
                const tbody = table.querySelector('tbody');
                const columnIndex = Array.from(this.parentElement.children).indexOf(this);
                const isAscending = this.classList.contains('sorted-asc');
                
                // Remove sorted class from all headers
                table.querySelectorAll('.sortable-header').forEach(h => {
                    h.classList.remove('sorted-asc', 'sorted-desc');
                });
                
                // Sort rows
                const rows = Array.from(tbody.querySelectorAll('tr'));
                rows.sort((a, b) => {
                    const aValue = a.cells[columnIndex].textContent.trim();
                    const bValue = b.cells[columnIndex].textContent.trim();
                    
                    // Try numeric comparison first
                    const aNum = parseFloat(aValue);
                    const bNum = parseFloat(bValue);
                    
                    if (!isNaN(aNum) && !isNaN(bNum)) {
                        return isAscending ? bNum - aNum : aNum - bNum;
                    }
                    
                    // Fallback to string comparison
                    return isAscending 
                        ? bValue.localeCompare(aValue)
                        : aValue.localeCompare(bValue);
                });
                
                // Update sorted class
                this.classList.add(isAscending ? 'sorted-desc' : 'sorted-asc');
                
                // Re-append sorted rows
                rows.forEach(row => tbody.appendChild(row));
                
                // Announce to screen readers
                const direction = isAscending ? 'descending' : 'ascending';
                announceToScreenReader(`Table sorted by ${this.textContent.trim()} in ${direction} order`);
            });
            
            // Add keyboard support
            header.setAttribute('role', 'button');
            header.setAttribute('tabindex', '0');
            header.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.click();
                }
            });
        });
    }
    
    /**
     * Initialize table search/filter functionality
     */
    function initTableSearch() {
        const searchInputs = document.querySelectorAll('[data-table-search]');
        
        searchInputs.forEach(input => {
            const tableId = input.getAttribute('data-table-search');
            const table = document.getElementById(tableId);
            
            if (!table) return;
            
            input.addEventListener('input', debounce(function() {
                const searchTerm = this.value.toLowerCase();
                const rows = table.querySelectorAll('tbody tr');
                let visibleCount = 0;
                
                rows.forEach(row => {
                    const text = row.textContent.toLowerCase();
                    const matches = text.includes(searchTerm);
                    
                    row.style.display = matches ? '' : 'none';
                    if (matches) visibleCount++;
                });
                
                // Show/hide empty state
                updateEmptyState(table, visibleCount);
                
                // Announce results to screen readers
                announceToScreenReader(`${visibleCount} results found`);
            }, 300));
        });
    }
    
    /**
     * Add scroll indicators to scrollable tables
     */
    function addScrollIndicators() {
        const scrollContainers = document.querySelectorAll('.table-responsive-mobile');
        
        scrollContainers.forEach(container => {
            const table = container.querySelector('table');
            if (!table) return;
            
            // Update shadows based on scroll position
            function updateScrollShadows() {
                const scrollLeft = container.scrollLeft;
                const scrollWidth = container.scrollWidth;
                const clientWidth = container.clientWidth;
                
                const before = container.querySelector('::before');
                const after = container.querySelector('::after');
                
                // Show left shadow if scrolled right
                container.style.setProperty('--left-shadow-opacity', scrollLeft > 0 ? '1' : '0');
                
                // Show right shadow if not fully scrolled
                const atEnd = scrollLeft + clientWidth >= scrollWidth - 1;
                container.style.setProperty('--right-shadow-opacity', atEnd ? '0' : '1');
            }
            
            container.addEventListener('scroll', updateScrollShadows);
            updateScrollShadows(); // Initial check
            
            // Re-check on window resize
            window.addEventListener('resize', debounce(updateScrollShadows, 200));
        });
    }
    
    /**
     * Update empty state visibility
     */
    function updateEmptyState(table, visibleCount) {
        let emptyState = table.querySelector('.table-empty-state');
        
        if (visibleCount === 0) {
            if (!emptyState) {
                emptyState = document.createElement('div');
                emptyState.className = 'table-empty-state';
                emptyState.innerHTML = `
                    <i class="fas fa-search"></i>
                    <h3>No results found</h3>
                    <p>Try adjusting your search terms</p>
                `;
                table.parentElement.appendChild(emptyState);
            }
            emptyState.style.display = 'block';
        } else if (emptyState) {
            emptyState.style.display = 'none';
        }
    }
    
    /**
     * Announce message to screen readers
     */
    function announceToScreenReader(message) {
        const announcement = document.createElement('div');
        announcement.setAttribute('role', 'status');
        announcement.setAttribute('aria-live', 'polite');
        announcement.className = 'sr-only';
        announcement.textContent = message;
        
        document.body.appendChild(announcement);
        
        // Remove after announcement
        setTimeout(() => announcement.remove(), 1000);
    }
    
    /**
     * Debounce helper function
     */
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func.apply(this, args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    /**
     * Export table to CSV
     */
    window.exportTableToCSV = function(tableId, filename = 'table-export.csv') {
        const table = document.getElementById(tableId);
        if (!table) return;
        
        const rows = table.querySelectorAll('tr');
        const csv = [];
        
        rows.forEach(row => {
            const cells = row.querySelectorAll('th, td');
            const rowData = Array.from(cells).map(cell => {
                let text = cell.textContent.trim();
                // Escape quotes and wrap in quotes if contains comma
                text = text.replace(/"/g, '""');
                return text.includes(',') ? `"${text}"` : text;
            });
            csv.push(rowData.join(','));
        });
        
        // Create download link
        const csvContent = csv.join('\n');
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        link.click();
        window.URL.revokeObjectURL(url);
        
        announceToScreenReader('Table exported to CSV');
    };
    
    /**
     * Toggle table view (card vs table on mobile)
     */
    window.toggleTableView = function(tableId) {
        const table = document.getElementById(tableId);
        if (!table) return;
        
        if (table.classList.contains('table-card-mobile')) {
            table.classList.remove('table-card-mobile');
            table.classList.add('table-scroll-mobile');
            announceToScreenReader('Switched to table view');
        } else {
            table.classList.remove('table-scroll-mobile');
            table.classList.add('table-card-mobile');
            announceToScreenReader('Switched to card view');
        }
    };
    
    /**
     * Initialize on DOM ready
     */
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initResponsiveTables);
    } else {
        initResponsiveTables();
    }
    
    // Re-initialize on AJAX content load (if using HTMX or similar)
    document.addEventListener('htmx:afterSwap', initResponsiveTables);
    
})();
