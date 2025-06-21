/**
 * EMTEEGEE - Magic: The Gathering Card Analysis Platform
 * Custom JavaScript for enhanced user experience
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all tooltips and popovers
    initializeBootstrapComponents();
    
    // Card-specific enhancements
    initializeCardEnhancements();
    
    // Search enhancements
    initializeSearchEnhancements();
});

/**
 * Initialize Bootstrap tooltips and popovers
 */
function initializeBootstrapComponents() {
    // Tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => 
        new bootstrap.Tooltip(tooltipTriggerEl, {
            delay: { show: 300, hide: 100 }
        })
    );
    
    // Popovers
    const popoverTriggerList = document.querySelectorAll('[data-bs-toggle="popover"]');
    const popoverList = [...popoverTriggerList].map(popoverTriggerEl => 
        new bootstrap.Popover(popoverTriggerEl, {
            trigger: 'hover focus',
            delay: { show: 300, hide: 100 }
        })
    );
}

/**
 * Card-specific enhancements
 */
function initializeCardEnhancements() {
    // Add mana symbol rendering
    renderManaSymbols();
    
    // Add card text parsing
    parseCardText();
    
    // Add copy UUID functionality
    addCopyUuidButtons();
}

/**
 * Render mana symbols in card text and costs
 */
function renderManaSymbols() {
    const manaPattern = /\{([WUBRG\d\/XYZ]+)\}/g;
    
    document.querySelectorAll('.mana-cost, .card-text-box').forEach(element => {
        element.innerHTML = element.innerHTML.replace(manaPattern, function(match, symbol) {
            return `<i class="ms ms-${symbol.toLowerCase()}" title="${symbol}"></i>`;
        });
    });
}

/**
 * Parse and enhance card text with rules text formatting
 */
function parseCardText() {
    document.querySelectorAll('.card-text-box').forEach(element => {
        let text = element.innerHTML;
        
        // Make reminder text italic
        text = text.replace(/\(([^)]+)\)/g, '<em class="text-muted">($1)</em>');
        
        // Bold ability names (words followed by —)
        text = text.replace(/([A-Z][a-z]+)\s*—/g, '<strong>$1</strong> —');
        
        element.innerHTML = text;
    });
}

/**
 * Add copy UUID functionality
 */
function addCopyUuidButtons() {
    document.querySelectorAll('.card-uuid').forEach(element => {
        const uuid = element.textContent.trim();
        
        const copyButton = document.createElement('button');
        copyButton.className = 'btn btn-sm btn-outline-secondary ms-2';
        copyButton.innerHTML = '<i class="bi bi-clipboard"></i>';
        copyButton.title = 'Copy UUID';
        copyButton.onclick = function() {
            navigator.clipboard.writeText(uuid).then(() => {
                copyButton.innerHTML = '<i class="bi bi-check"></i>';
                setTimeout(() => {
                    copyButton.innerHTML = '<i class="bi bi-clipboard"></i>';
                }, 2000);
            });
        };
        
        element.appendChild(copyButton);
    });
}

/**
 * Search enhancements
 */
function initializeSearchEnhancements() {
    // Add search suggestions (placeholder for future implementation)
    const searchInputs = document.querySelectorAll('input[type="search"]');
    searchInputs.forEach(input => {
        input.addEventListener('input', debounce(function() {
            // Future: implement search suggestions
        }, 300));
    });
}

/**
 * Utility: Debounce function for search
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Utility: Format large numbers with commas
 */
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

/**
 * Card search and filtering enhancements
 */
const CardSearch = {
    // Advanced search modal handling
    showAdvancedSearch: function() {
        const modal = new bootstrap.Modal(document.getElementById('advancedSearchModal'));
        modal.show();
    },
    
    // Clear all filters
    clearFilters: function() {
        document.querySelectorAll('.search-filter').forEach(input => {
            input.value = '';
            input.checked = false;
        });
    },
    
    // Export search results
    exportResults: function(format = 'json') {
        // Future implementation for exporting search results
        console.log(`Exporting results as ${format}`);
    }
};

// Global utilities for EMTEEGEE
window.EMTEEGEE = {
    CardSearch,
    formatNumber,
    initializeBootstrapComponents,
    renderManaSymbols
};
