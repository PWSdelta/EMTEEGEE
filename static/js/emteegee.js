// Enhanced JavaScript for EMTEEGEE - Magic: The Gathering Analysis Platform

document.addEventListener('DOMContentLoaded', function() {
    
    // Initialize tooltips for mana symbols
    initializeManaSymbolTooltips();
    
    // Initialize card hover effects
    initializeCardHoverEffects();
    
    // Initialize search functionality
    initializeSearchFeatures();
    
    // Initialize navigation enhancements
    initializeNavigation();
    
    // Initialize stats counters animation
    initializeStatsAnimation();
    
    // Initialize loading states
    initializeLoadingStates();
});

// Mana symbol tooltips
function initializeManaSymbolTooltips() {
    const manaSymbols = document.querySelectorAll('.mana-symbol, .mana-symbol-text');
    manaSymbols.forEach(symbol => {
        symbol.addEventListener('mouseenter', function() {
            const tooltip = document.createElement('div');
            tooltip.className = 'mana-tooltip';
            tooltip.textContent = this.getAttribute('title') || this.getAttribute('alt');
            document.body.appendChild(tooltip);
            
            const rect = this.getBoundingClientRect();
            tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
            tooltip.style.top = rect.top - tooltip.offsetHeight - 5 + 'px';
        });
        
        symbol.addEventListener('mouseleave', function() {
            const tooltip = document.querySelector('.mana-tooltip');
            if (tooltip) {
                tooltip.remove();
            }
        });
    });
}

// Card hover effects
function initializeCardHoverEffects() {
    const cards = document.querySelectorAll('.card-item, .featured-card, .gallery-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px) scale(1.02)';
            this.style.boxShadow = '0 10px 25px rgba(0,0,0,0.3)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
            this.style.boxShadow = '0 4px 8px rgba(0,0,0,0.1)';
        });
    });
}

// Search functionality enhancements
function initializeSearchFeatures() {
    const searchInputs = document.querySelectorAll('input[type="search"], .search-input');
    searchInputs.forEach(input => {
        let searchTimeout;
        
        input.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();
            
            if (query.length >= 2) {
                searchTimeout = setTimeout(() => {
                    performSearch(query);
                }, 300);
            }
        });
        
        // Add search suggestions
        input.addEventListener('focus', function() {
            showSearchSuggestions(this);
        });
    });
}

// Navigation enhancements
function initializeNavigation() {
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Active nav highlighting
    highlightActiveNavigation();
}

// Stats animation
function initializeStatsAnimation() {
    const statsNumbers = document.querySelectorAll('.stat-number, .hero-stat-number');
    
    const animateNumber = (element) => {
        const target = parseInt(element.textContent.replace(/,/g, ''));
        const duration = 2000;
        const step = target / (duration / 16);
        let current = 0;
        
        const timer = setInterval(() => {
            current += step;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            element.textContent = Math.floor(current).toLocaleString();
        }, 16);
    };
    
    // Use Intersection Observer to trigger animation when visible
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateNumber(entry.target);
                observer.unobserve(entry.target);
            }
        });
    });
    
    statsNumbers.forEach(stat => observer.observe(stat));
}

// Loading states
function initializeLoadingStates() {
    // Add loading states to buttons
    document.querySelectorAll('.btn-primary, .btn-outline-primary').forEach(button => {
        button.addEventListener('click', function() {
            if (this.type === 'submit' || this.href) {
                this.classList.add('loading');
                this.disabled = true;
                
                const originalText = this.textContent;
                this.textContent = 'Loading...';
                
                // Reset after 5 seconds if no page change
                setTimeout(() => {
                    this.classList.remove('loading');
                    this.disabled = false;
                    this.textContent = originalText;
                }, 5000);
            }
        });
    });
}

// Search functionality
function performSearch(query) {
    // This would typically make an AJAX request to search endpoint
    console.log('Searching for:', query);
    
    // Show loading indicator
    const searchIndicator = document.querySelector('.search-loading');
    if (searchIndicator) {
        searchIndicator.style.display = 'block';
    }
    
    // Simulate search (replace with actual API call)
    setTimeout(() => {
        if (searchIndicator) {
            searchIndicator.style.display = 'none';
        }
        // Handle search results
    }, 500);
}

// Search suggestions
function showSearchSuggestions(input) {
    const suggestions = [
        'Lightning Bolt',
        'Black Lotus',
        'Serra Angel',
        'Counterspell',
        'Birds of Paradise',
        'Wrath of God',
        'Ancestral Recall',
        'Sol Ring'
    ];
    
    const suggestionsContainer = document.createElement('div');
    suggestionsContainer.className = 'search-suggestions';
    
    suggestions.forEach(suggestion => {
        const item = document.createElement('div');
        item.className = 'suggestion-item';
        item.textContent = suggestion;
        item.addEventListener('click', () => {
            input.value = suggestion;
            suggestionsContainer.remove();
            performSearch(suggestion);
        });
        suggestionsContainer.appendChild(item);
    });
    
    // Position and show suggestions
    const rect = input.getBoundingClientRect();
    suggestionsContainer.style.position = 'absolute';
    suggestionsContainer.style.top = rect.bottom + 'px';
    suggestionsContainer.style.left = rect.left + 'px';
    suggestionsContainer.style.width = rect.width + 'px';
    
    document.body.appendChild(suggestionsContainer);
    
    // Remove suggestions when clicking outside
    document.addEventListener('click', function(e) {
        if (!suggestionsContainer.contains(e.target) && e.target !== input) {
            suggestionsContainer.remove();
        }
    });
}

// Navigation highlighting
function highlightActiveNavigation() {
    const currentPath = window.location.pathname;
    document.querySelectorAll('.nav-link').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
}

// Utility functions
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

// Card image lazy loading
function initializeLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
}

// Initialize lazy loading
document.addEventListener('DOMContentLoaded', initializeLazyLoading);

// Theme toggle functionality (if needed)
function initializeThemeToggle() {
    const themeToggle = document.querySelector('.theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            document.body.classList.toggle('dark-theme');
            localStorage.setItem('theme', document.body.classList.contains('dark-theme') ? 'dark' : 'light');
        });
        
        // Load saved theme
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'dark') {
            document.body.classList.add('dark-theme');
        }
    }
}

// Error handling for images
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('img').forEach(img => {
        img.addEventListener('error', function() {
            this.src = '/static/images/card-placeholder.png';
            this.alt = 'Card image not available';
        });
    });
});

// Export functions for use in other scripts
window.EMTEEGEEUtils = {
    performSearch,
    showSearchSuggestions,
    debounce,
    initializeLazyLoading
};
