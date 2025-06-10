// Main JavaScript file for DSA Questions Manager

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips if Bootstrap tooltips are used
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-resize textareas
    autoResizeTextareas();
    
    // Setup form validation
    setupFormValidation();
    
    // Setup search functionality
    setupSearchEnhancements();
});

// Auto-resize textareas based on content
function autoResizeTextareas() {
    const textareas = document.querySelectorAll('textarea');
    
    textareas.forEach(textarea => {
        // Initial resize
        resizeTextarea(textarea);
        
        // Add event listener for input
        textarea.addEventListener('input', function() {
            resizeTextarea(this);
        });
    });
}

function resizeTextarea(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = Math.max(textarea.scrollHeight, 100) + 'px';
}

// Enhanced form validation
function setupFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
                
                // Focus on first invalid field
                const firstInvalidField = form.querySelector(':invalid');
                if (firstInvalidField) {
                    firstInvalidField.focus();
                }
            }
            
            form.classList.add('was-validated');
        });
        
        // Real-time validation for better UX
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                if (this.checkValidity()) {
                    this.classList.remove('is-invalid');
                    this.classList.add('is-valid');
                } else {
                    this.classList.remove('is-valid');
                    this.classList.add('is-invalid');
                }
            });
        });
    });
}

// Enhanced search functionality
function setupSearchEnhancements() {
    const searchForm = document.querySelector('form[action*="index"]');
    if (!searchForm) return;
    
    const searchInput = searchForm.querySelector('input[name="search"]');
    const difficultySelect = searchForm.querySelector('select[name="difficulty"]');
    const topicSelect = searchForm.querySelector('select[name="topic"]');
    
    // Auto-submit form when filters change (with debouncing for search)
    let searchTimeout;
    
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                if (this.value.length >= 2 || this.value.length === 0) {
                    searchForm.submit();
                }
            }, 500); // 500ms debounce
        });
    }
    
    if (difficultySelect) {
        difficultySelect.addEventListener('change', function() {
            searchForm.submit();
        });
    }
    
    if (topicSelect) {
        topicSelect.addEventListener('change', function() {
            searchForm.submit();
        });
    }
}

// Utility function to show loading state on buttons
function showLoadingState(button, loadingText = 'Loading...') {
    const originalText = button.innerHTML;
    button.innerHTML = `<span class="spinner-border spinner-border-sm me-2" role="status"></span>${loadingText}`;
    button.disabled = true;
    
    // Return function to restore original state
    return function() {
        button.innerHTML = originalText;
        button.disabled = false;
    };
}

// Utility function to show toast notifications
function showToast(message, type = 'info') {
    // Create toast element
    const toastHtml = `
        <div class="toast align-items-center text-white bg-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'info'} border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;
    
    // Create toast container if it doesn't exist
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    // Add toast to container
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    
    // Initialize and show toast
    const toastElement = toastContainer.lastElementChild;
    const toast = new bootstrap.Toast(toastElement);
    toast.show();
    
    // Remove toast element after it's hidden
    toastElement.addEventListener('hidden.bs.toast', function() {
        this.remove();
    });
}

// Confirmation dialog utility
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Copy to clipboard utility
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(function() {
            showToast('Copied to clipboard!', 'success');
        }).catch(function() {
            fallbackCopyToClipboard(text);
        });
    } else {
        fallbackCopyToClipboard(text);
    }
}

function fallbackCopyToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        document.execCommand('copy');
        showToast('Copied to clipboard!', 'success');
    } catch (err) {
        showToast('Failed to copy to clipboard', 'error');
    }
    
    document.body.removeChild(textArea);
}

// Format time complexity display
function formatTimeComplexity(complexity) {
    // Add some common formatting for time complexity strings
    return complexity
        .replace(/\bO\(/g, 'O(')
        .replace(/\blog\s*n/gi, 'log n')
        .replace(/\bn\s*\^\s*2/gi, 'n²')
        .replace(/\bn\s*\*\s*m/gi, 'n×m');
}

// Keyboard shortcuts
document.addEventListener('keydown', function(event) {
    // Ctrl/Cmd + / to focus search
    if ((event.ctrlKey || event.metaKey) && event.key === '/') {
        event.preventDefault();
        const searchInput = document.querySelector('input[name="search"]');
        if (searchInput) {
            searchInput.focus();
        }
    }
    
    // Escape to clear search
    if (event.key === 'Escape') {
        const searchInput = document.querySelector('input[name="search"]');
        if (searchInput && document.activeElement === searchInput) {
            searchInput.value = '';
            searchInput.form.submit();
        }
    }
});

// Analytics and user experience tracking
function trackUserAction(action, details = {}) {
    // This would integrate with analytics services
    console.log('User action:', action, details);
}

// Export functions for use in other scripts
window.DSAManager = {
    showLoadingState,
    showToast,
    confirmAction,
    copyToClipboard,
    formatTimeComplexity,
    trackUserAction
};
