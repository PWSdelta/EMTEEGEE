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
    
    // Initialize card preview modal
    if (typeof window.cardPreviewModal === 'undefined') {
        window.cardPreviewModal = new CardPreviewModal();
    }
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
    initializeLazyLoading,
    showCardPreview,
    hideCardPreview
};

// Card preview modal functionality
let previewModal = null;

function showCardPreview(cardElement) {
    const cardName = cardElement.querySelector('.card-name')?.textContent || 'Unknown Card';
    const cardImage = cardElement.querySelector('.card-image img')?.src || '';
    const cardType = cardElement.dataset.cardType || '';
    const cardMana = cardElement.dataset.cardMana || '';
    const cardUuid = cardElement.dataset.cardUuid || '';
    
    if (!previewModal) {
        createPreviewModal();
    }
    
    // Update modal content
    document.getElementById('preview-card-name').textContent = cardName;
    document.getElementById('preview-card-type').textContent = cardType;
    document.getElementById('preview-card-mana').textContent = cardMana;
    
    const previewImage = document.getElementById('preview-card-image');
    if (cardImage) {
        previewImage.src = cardImage;
        previewImage.style.display = 'block';
    } else {
        previewImage.style.display = 'none';
    }
    
    // Update view button
    const viewButton = document.getElementById('preview-view-button');
    if (cardUuid) {
        viewButton.href = `/card/${cardUuid}/`;
        viewButton.style.display = 'inline-block';
    } else {
        viewButton.style.display = 'none';
    }
    
    // Show modal
    previewModal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
    
    // Add fade-in animation
    setTimeout(() => {
        previewModal.classList.add('show');
    }, 10);
}

function hideCardPreview() {
    if (previewModal) {
        previewModal.classList.remove('show');
        
        setTimeout(() => {
            previewModal.style.display = 'none';
            document.body.style.overflow = '';
        }, 300);
    }
}

function createPreviewModal() {
    const modalHTML = `
        <div class="card-preview-modal" id="card-preview-modal">
            <div class="preview-backdrop" onclick="hideCardPreview()"></div>
            <div class="preview-content">
                <button class="preview-close" onclick="hideCardPreview()">&times;</button>
                <div class="preview-body">
                    <div class="preview-image-section">
                        <img id="preview-card-image" alt="Card preview" />
                    </div>
                    <div class="preview-info-section">
                        <h2 id="preview-card-name">Card Name</h2>
                        <p id="preview-card-type">Card Type</p>
                        <p id="preview-card-mana">Mana Cost</p>
                        <div class="preview-actions">
                            <a id="preview-view-button" class="btn-preview-primary">View Full Analysis</a>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    previewModal = document.getElementById('card-preview-modal');
    
    // Add CSS for the modal
    const modalCSS = `
        <style>
        .card-preview-modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        
        .card-preview-modal.show {
            opacity: 1;
        }
        
        .preview-backdrop {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
        }
        
        .preview-content {
            background: white;
            border-radius: 16px;
            max-width: 800px;
            max-height: 90vh;
            margin: 2rem;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
            position: relative;
            overflow: hidden;
            transform: translateY(50px);
            transition: transform 0.3s ease;
        }
        
        .card-preview-modal.show .preview-content {
            transform: translateY(0);
        }
        
        .preview-close {
            position: absolute;
            top: 1rem;
            right: 1rem;
            background: rgba(0, 0, 0, 0.5);
            color: white;
            border: none;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            font-size: 1.5rem;
            cursor: pointer;
            z-index: 10;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background 0.2s ease;
        }
        
        .preview-close:hover {
            background: rgba(0, 0, 0, 0.7);
        }
        
        .preview-body {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            padding: 2rem;
        }
        
        .preview-image-section img {
            width: 100%;
            height: auto;
            border-radius: 12px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        }
        
        .preview-info-section h2 {
            font-size: 1.8rem;
            font-weight: 700;
            color: #333;
            margin-bottom: 1rem;
        }
        
        .preview-info-section p {
            color: #666;
            margin-bottom: 0.5rem;
            font-size: 1.1rem;
        }
        
        .preview-actions {
            margin-top: 2rem;
        }
        
        .btn-preview-primary {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            text-decoration: none;
            display: inline-block;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .btn-preview-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
            color: white;
            text-decoration: none;
        }
        
        @media (max-width: 768px) {
            .preview-body {
                grid-template-columns: 1fr;
                gap: 1rem;
                padding: 1rem;
            }
            
            .preview-content {
                margin: 1rem;
            }
        }
        </style>
    `;
    
    document.head.insertAdjacentHTML('beforeend', modalCSS);
    
    // Handle escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && previewModal && previewModal.style.display === 'flex') {
            hideCardPreview();
        }
    });
}

// Card Preview Modal System
class CardPreviewModal {
    constructor() {
        this.modal = null;
        this.currentCard = null;
        this.previewCache = new Map();
        this.loadingTimeout = null;
        this.init();
    }
    
    init() {
        this.createModal();
        this.bindEvents();
    }
    
    createModal() {
        // Create modal HTML
        const modalHTML = `
            <div id="card-preview-modal" class="card-preview-modal" style="display: none;">
                <div class="card-preview-content">
                    <div class="card-preview-header">
                        <h3 class="card-preview-title">Card Preview</h3>
                        <button class="card-preview-close" aria-label="Close preview">×</button>
                    </div>
                    <div class="card-preview-body">
                        <div class="card-preview-loading">
                            <div class="loading-spinner"></div>
                            <p>Loading card preview...</p>
                        </div>
                        <div class="card-preview-error" style="display: none;">
                            <p>Error loading card preview</p>
                        </div>
                        <div class="card-preview-data" style="display: none;">
                            <div class="card-preview-grid">
                                <div class="card-preview-image-section">
                                    <img class="card-preview-image" alt="Card image">
                                </div>
                                <div class="card-preview-info-section">
                                    <h4 class="card-preview-name"></h4>
                                    <p class="card-preview-type"></p>
                                    <div class="card-preview-stats">
                                        <div class="card-preview-stat">
                                            <label>Mana Cost:</label>
                                            <span class="card-preview-mana-cost"></span>
                                        </div>
                                        <div class="card-preview-stat">
                                            <label>Analysis:</label>
                                            <span class="card-preview-analysis-status"></span>
                                        </div>
                                    </div>
                                    <div class="card-preview-actions">
                                        <a class="btn btn-primary card-preview-view-btn" href="#">View Full Analysis</a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="card-preview-backdrop"></div>
            </div>
        `;
        
        // Add to page
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        this.modal = document.getElementById('card-preview-modal');
        
        // Add CSS
        this.addModalStyles();
    }
    
    addModalStyles() {
        const styles = `
            .card-preview-modal {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: 1050;
                display: flex;
                align-items: center;
                justify-content: center;
                opacity: 0;
                visibility: hidden;
                transition: opacity 0.3s ease, visibility 0.3s ease;
            }
            
            .card-preview-modal.show {
                opacity: 1;
                visibility: visible;
            }
            
            .card-preview-backdrop {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
                backdrop-filter: blur(2px);
            }
            
            .card-preview-content {
                position: relative;
                background: white;
                border-radius: 12px;
                max-width: 600px;
                width: 90%;
                max-height: 80vh;
                overflow: hidden;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                transform: scale(0.9);
                transition: transform 0.3s ease;
            }
            
            .card-preview-modal.show .card-preview-content {
                transform: scale(1);
            }
            
            .card-preview-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 1rem;
                display: flex;
                justify-content: between;
                align-items: center;
            }
            
            .card-preview-title {
                margin: 0;
                font-size: 1.2rem;
                font-weight: 600;
            }
            
            .card-preview-close {
                background: none;
                border: none;
                color: white;
                font-size: 1.5rem;
                cursor: pointer;
                padding: 0;
                margin-left: auto;
                width: 30px;
                height: 30px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 50%;
                transition: background-color 0.2s ease;
            }
            
            .card-preview-close:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
            
            .card-preview-body {
                padding: 1.5rem;
                max-height: 60vh;
                overflow-y: auto;
            }
            
            .card-preview-loading {
                text-align: center;
                padding: 2rem;
            }
            
            .card-preview-error {
                text-align: center;
                padding: 2rem;
                color: #dc3545;
            }
            
            .card-preview-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 1.5rem;
                align-items: start;
            }
            
            .card-preview-image {
                width: 100%;
                height: auto;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            }
            
            .card-preview-name {
                color: #667eea;
                margin-bottom: 0.5rem;
                font-size: 1.3rem;
            }
            
            .card-preview-type {
                color: #666;
                margin-bottom: 1rem;
                font-style: italic;
            }
            
            .card-preview-stats {
                margin-bottom: 1.5rem;
            }
            
            .card-preview-stat {
                display: flex;
                justify-content: between;
                margin-bottom: 0.5rem;
            }
            
            .card-preview-stat label {
                font-weight: 600;
                color: #333;
            }
            
            .card-preview-analysis-status {
                background: #28a745;
                color: white;
                padding: 0.2rem 0.5rem;
                border-radius: 4px;
                font-size: 0.8rem;
            }
            
            .card-preview-actions {
                text-align: center;
            }
            
            .card-preview-view-btn {
                background: linear-gradient(135deg, #667eea, #764ba2);
                border: none;
                padding: 0.75rem 1.5rem;
                border-radius: 6px;
                color: white;
                text-decoration: none;
                display: inline-block;
                transition: transform 0.2s ease;
            }
            
            .card-preview-view-btn:hover {
                transform: translateY(-2px);
                color: white;
                text-decoration: none;
            }
            
            @media (max-width: 768px) {
                .card-preview-grid {
                    grid-template-columns: 1fr;
                }
                
                .card-preview-content {
                    width: 95%;
                    max-height: 90vh;
                }
            }
        `;
        
        // Add styles to head
        const styleSheet = document.createElement('style');
        styleSheet.textContent = styles;
        document.head.appendChild(styleSheet);
    }
    
    bindEvents() {
        // Close modal events
        const closeBtn = this.modal.querySelector('.card-preview-close');
        const backdrop = this.modal.querySelector('.card-preview-backdrop');
        
        closeBtn.addEventListener('click', () => this.hide());
        backdrop.addEventListener('click', () => this.hide());
        
        // Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.modal.classList.contains('show')) {
                this.hide();
            }
        });
        
        // Bind to card links
        this.bindCardLinks();
    }
    
    bindCardLinks() {
        // Find all card links and add preview on hover
        document.addEventListener('mouseover', (e) => {
            const cardLink = e.target.closest('a[href*="/card/"]');
            if (cardLink && !cardLink.hasAttribute('data-preview-bound')) {
                cardLink.setAttribute('data-preview-bound', 'true');
                this.addPreviewToLink(cardLink);
            }
        });
    }
    
    addPreviewToLink(link) {
        let hoverTimeout;
        
        link.addEventListener('mouseenter', () => {
            hoverTimeout = setTimeout(() => {
                const cardUuid = this.extractCardUuid(link.href);
                if (cardUuid) {
                    this.showPreview(cardUuid);
                }
            }, 500); // Show preview after 500ms hover
        });
        
        link.addEventListener('mouseleave', () => {
            clearTimeout(hoverTimeout);
        });
        
        // Also add click handler for mobile
        link.addEventListener('click', (e) => {
            if (window.innerWidth <= 768) {
                e.preventDefault();
                const cardUuid = this.extractCardUuid(link.href);
                if (cardUuid) {
                    this.showPreview(cardUuid);
                }
            }
        });
    }
    
    extractCardUuid(href) {
        const match = href.match(/\/card\/([^\/]+)\//);
        return match ? match[1] : null;
    }
    
    async showPreview(cardUuid) {
        if (this.currentCard === cardUuid && this.modal.classList.contains('show')) {
            return; // Already showing this card
        }
        
        this.currentCard = cardUuid;
        this.show();
        
        // Show loading state
        this.showLoading();
        
        // Check cache first
        if (this.previewCache.has(cardUuid)) {
            this.showCardData(this.previewCache.get(cardUuid));
            return;
        }
        
        try {
            // Fetch card data
            const response = await fetch(`/api/card-preview/${cardUuid}/`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const cardData = await response.json();
            
            // Cache the data
            this.previewCache.set(cardUuid, cardData);
            
            // Show the card data
            this.showCardData(cardData);
            
        } catch (error) {
            console.error('Error loading card preview:', error);
            this.showError();
        }
    }
    
    show() {
        this.modal.style.display = 'flex';
        // Force reflow
        this.modal.offsetHeight;
        this.modal.classList.add('show');
        document.body.style.overflow = 'hidden';
    }
    
    hide() {
        this.modal.classList.remove('show');
        document.body.style.overflow = '';
        setTimeout(() => {
            this.modal.style.display = 'none';
        }, 300);
    }
    
    showLoading() {
        this.modal.querySelector('.card-preview-loading').style.display = 'block';
        this.modal.querySelector('.card-preview-error').style.display = 'none';
        this.modal.querySelector('.card-preview-data').style.display = 'none';
    }
    
    showError() {
        this.modal.querySelector('.card-preview-loading').style.display = 'none';
        this.modal.querySelector('.card-preview-error').style.display = 'block';
        this.modal.querySelector('.card-preview-data').style.display = 'none';
    }
    
    showCardData(cardData) {
        this.modal.querySelector('.card-preview-loading').style.display = 'none';
        this.modal.querySelector('.card-preview-error').style.display = 'none';
        this.modal.querySelector('.card-preview-data').style.display = 'block';
        
        // Populate data
        this.modal.querySelector('.card-preview-name').textContent = cardData.name || 'Unknown Card';
        this.modal.querySelector('.card-preview-type').textContent = cardData.type || '';
        this.modal.querySelector('.card-preview-mana-cost').textContent = cardData.manaCost || 'N/A';
        
        // Set image
        const img = this.modal.querySelector('.card-preview-image');
        if (cardData.imageUris && cardData.imageUris.normal) {
            img.src = cardData.imageUris.normal;
            img.alt = cardData.name || 'Card image';
        } else {
            img.src = '/static/images/card-placeholder.png';
            img.alt = 'Card image not available';
        }
        
        // Analysis status
        const analysisStatus = this.modal.querySelector('.card-preview-analysis-status');
        const componentCount = cardData.componentCount || 0;
        if (componentCount >= 20) {
            analysisStatus.textContent = 'Fully Analyzed';
            analysisStatus.className = 'card-preview-analysis-status bg-success';
        } else if (componentCount > 0) {
            analysisStatus.textContent = `${componentCount}/20 Components`;
            analysisStatus.className = 'card-preview-analysis-status bg-warning';
        } else {
            analysisStatus.textContent = 'Not Analyzed';
            analysisStatus.className = 'card-preview-analysis-status bg-secondary';
        }
        
        // View button
        const viewBtn = this.modal.querySelector('.card-preview-view-btn');
        viewBtn.href = `/card/${cardData.uuid}/`;
    }
}

// Initialize card preview modal when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize card preview modal
    if (typeof window.cardPreviewModal === 'undefined') {
        window.cardPreviewModal = new CardPreviewModal();
    }
});
