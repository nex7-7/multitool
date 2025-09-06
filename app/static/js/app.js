/**
 * Main application JavaScript
 * Handles navigation, modal management, and core UI interactions
 */

// Global app state
const App = {
    currentTab: 'image',
    currentTool: null,
    isProcessing: false
};

// DOM elements
const DOM = {
    navButtons: document.querySelectorAll('.nav-btn'),
    tabContents: document.querySelectorAll('.tab-content'),
    toolCards: document.querySelectorAll('.tool-card'),
    modal: document.getElementById('tool-modal'),
    modalTitle: document.getElementById('modal-title'),
    modalBody: document.getElementById('modal-body'),
    loadingOverlay: document.getElementById('loading-overlay')
};

/**
 * Initialize the application
 */
function initApp() {
    setupEventListeners();
    setupTabNavigation();
    setupToolCards();
}

/**
 * Setup event listeners for navigation and UI interactions
 */
function setupEventListeners() {
    // Tab navigation
    DOM.navButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.dataset.tab;
            switchTab(tabId);
        });
    });

    // Tool cards
    DOM.toolCards.forEach(card => {
        card.addEventListener('click', () => {
            if (card.classList.contains('coming-soon')) {
                showAlert('This tool is coming soon!', 'warning');
                return;
            }
            
            const tool = card.dataset.tool;
            const category = App.currentTab;
            openToolModal(tool, category);
        });
    });

    // Modal close events
    document.addEventListener('click', (e) => {
        if (e.target === DOM.modal) {
            closeModal();
        }
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && DOM.modal.classList.contains('active')) {
            closeModal();
        }
    });
}

/**
 * Setup tab navigation
 */
function setupTabNavigation() {
    // Set initial active tab
    switchTab('image');
}

/**
 * Setup tool cards interactions
 */
function setupToolCards() {
    // Add hover effects and accessibility
    DOM.toolCards.forEach(card => {
        card.setAttribute('tabindex', '0');
        
        card.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                card.click();
            }
        });
    });
}

/**
 * Switch between tabs
 * @param {string} tabId - The tab to switch to
 */
function switchTab(tabId) {
    App.currentTab = tabId;

    // Update navigation buttons
    DOM.navButtons.forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tabId);
    });

    // Update tab content
    DOM.tabContents.forEach(content => {
        content.classList.toggle('active', content.id === `${tabId}-tab`);
    });
}

/**
 * Open tool modal
 * @param {string} tool - Tool identifier
 * @param {string} category - Tool category (image, video, pdf)
 */
function openToolModal(tool, category) {
    App.currentTool = tool;
    
    // Set modal title
    const toolNames = {
        resize: 'Resize Image',
        crop: 'Crop Image',
        rotate: 'Rotate Image',
        enhance: 'Enhance Image',
        'remove-bg': 'Remove Background',
    convert: 'Convert Format',
    // PDF tools
    split: 'Split PDF',
    merge: 'Merge PDFs',
    rearrange: 'Rearrange Pages',
    'extract-text': 'Extract Text',
    'convert-to-pdf': 'Convert to PDF'
    };
    
    DOM.modalTitle.textContent = toolNames[tool] || 'Tool';
    
    // Load tool-specific content
    loadToolContent(tool, category);
    
    // Show modal
    DOM.modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

/**
 * Close modal
 */
function closeModal() {
    DOM.modal.classList.remove('active');
    document.body.style.overflow = '';
    App.currentTool = null;
}

/**
 * Load tool-specific content into modal
 * @param {string} tool - Tool identifier
 * @param {string} category - Tool category
 */
function loadToolContent(tool, category) {
    if (category === 'image') {
        loadImageToolContent(tool);
    } else if (category === 'pdf') {
        if (typeof loadPdfToolContent === 'function') {
            loadPdfToolContent(tool);
        } else {
            DOM.modalBody.innerHTML = '<p>PDF tool UI not loaded.</p>';
        }
    } else {
        DOM.modalBody.innerHTML = '<p>This tool is not yet implemented.</p>';
    }
}

/**
 * Show loading overlay
 * @param {string} message - Loading message
 */
function showLoading(message = 'Processing...') {
    App.isProcessing = true;
    DOM.loadingOverlay.querySelector('p').textContent = message;
    DOM.loadingOverlay.classList.add('active');
}

/**
 * Hide loading overlay
 */
function hideLoading() {
    App.isProcessing = false;
    DOM.loadingOverlay.classList.remove('active');
}

/**
 * Show alert message
 * @param {string} message - Alert message
 * @param {string} type - Alert type (success, error, warning)
 * @param {number} duration - Auto-hide duration in ms
 */
function showAlert(message, type = 'success', duration = 5000) {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'exclamation-triangle'}"></i>
        ${message}
    `;

    // Find a good place to insert the alert
    const container = document.querySelector('.modal-body') || document.querySelector('.main .container');
    container.insertBefore(alert, container.firstChild);

    // Auto-hide after duration
    if (duration > 0) {
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, duration);
    }

    return alert;
}

/**
 * Format file size for display
 * @param {number} bytes - File size in bytes
 * @returns {string} Formatted file size
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Validate file type
 * @param {File} file - File object
 * @param {Array} allowedTypes - Array of allowed MIME types or extensions
 * @returns {boolean} Whether file is valid
 */
function validateFileType(file, allowedTypes) {
    const fileExtension = file.name.toLowerCase().split('.').pop();
    const mimeType = file.type.toLowerCase();
    
    return allowedTypes.some(type => {
        return type.includes('/') ? mimeType.includes(type) : fileExtension === type;
    });
}

/**
 * Create file input element
 * @param {Object} options - File input options
 * @returns {HTMLElement} File input element
 */
function createFileInput(options = {}) {
    const input = document.createElement('input');
    input.type = 'file';
    input.style.display = 'none';
    
    if (options.accept) {
        input.accept = options.accept;
    }
    
    if (options.multiple) {
        input.multiple = true;
    }
    
    return input;
}

/**
 * Download file from URL
 * @param {string} url - File URL
 * @param {string} filename - Suggested filename
 */
function downloadFile(url, filename) {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

/**
 * Make API request
 * @param {string} url - API endpoint
 * @param {Object} options - Request options
 * @returns {Promise} Fetch promise
 */
async function apiRequest(url, options = {}) {
    try {
        const response = await fetch(url, {
            ...options,
            headers: {
                ...options.headers
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', initApp);

// Expose global functions
window.closeModal = closeModal;
window.showAlert = showAlert;
window.showLoading = showLoading;
window.hideLoading = hideLoading;
window.formatFileSize = formatFileSize;
window.validateFileType = validateFileType;
window.downloadFile = downloadFile;
window.apiRequest = apiRequest;
