/**
 * Universal AJAX Clear Search Function
 * This script provides AJAX-based search clearing functionality
 * that works across all HRMS portal pages without page reload
 */

// Universal clear search function
function clearSearchField(fieldName) {
    const url = new URL(window.location);
    url.searchParams.delete(fieldName);
    
    // Update the URL without reloading the page
    window.history.pushState({}, '', url.toString());
    
    // Clear the search input field
    const searchInput = document.querySelector(`input[name="${fieldName}"]`);
    if (searchInput) {
        searchInput.value = '';
    }
    
    // Hide the clear button
    const clearButton = document.querySelector(`button[onclick*="clearSearchField('${fieldName}')"]`);
    if (clearButton) {
        clearButton.style.display = 'none';
    }
    
    // Show loading state
    showLoadingState();
    
    // Reload the page content via AJAX
    loadPageContent(url.toString());
}

// Function to load page content via AJAX
function loadPageContent(url) {
    fetch(url, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'text/html'
        }
    })
    .then(response => response.text())
    .then(html => {
        // Parse the HTML and update the relevant parts
        updatePageContent(html);
        
        // Show success message
        showNotification('Search cleared successfully', 'success');
        
        // Hide loading state
        hideLoadingState();
    })
    .catch(error => {
        console.error('Error loading content:', error);
        hideLoadingState();
        // Fallback to page reload if AJAX fails
        window.location.reload();
    });
}

// Function to update page content
function updatePageContent(html) {
    const parser = new DOMParser();
    const doc = parser.parseFromString(html, 'text/html');
    
    // Update main content areas
    const contentSelectors = [
        'table.table',
        '.table-responsive',
        '.card-body',
        '.modern-card-body',
        '#listView',
        '#gridView'
    ];
    
    contentSelectors.forEach(selector => {
        const newElement = doc.querySelector(selector);
        const currentElement = document.querySelector(selector);
        if (newElement && currentElement) {
            currentElement.innerHTML = newElement.innerHTML;
        }
    });
    
    // Update pagination
    const newPagination = doc.querySelector('.pagination, .modern-pagination');
    if (newPagination) {
        const currentPagination = document.querySelector('.pagination, .modern-pagination');
        if (currentPagination) {
            currentPagination.innerHTML = newPagination.innerHTML;
        }
    }
    
    // Re-attach event listeners if needed
    if (typeof attachEventListeners === 'function') {
        attachEventListeners();
    }
}

// Function to show loading state
function showLoadingState() {
    const loadingOverlay = document.createElement('div');
    loadingOverlay.id = 'ajaxLoadingOverlay';
    loadingOverlay.className = 'position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center';
    loadingOverlay.style.cssText = 'background-color: rgba(255, 255, 255, 0.8); z-index: 9999;';
    loadingOverlay.innerHTML = `
        <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
        </div>
    `;
    document.body.appendChild(loadingOverlay);
}

// Function to hide loading state
function hideLoadingState() {
    const loadingOverlay = document.getElementById('ajaxLoadingOverlay');
    if (loadingOverlay) {
        loadingOverlay.remove();
    }
}

// Function to show notification
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.ajax-notification');
    existingNotifications.forEach(notification => notification.remove());
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed ajax-notification`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 10000; max-width: 400px; min-width: 300px;';
    notification.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="bi bi-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'} me-2"></i>
            <div class="flex-grow-1">${message}</div>
            <button type="button" class="btn-close ms-2" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-dismiss after 3 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.classList.remove('show');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 150);
        }
    }, 3000);
}

// Alternative simple clear function for basic pages
function clearSearch() {
    clearSearchField('search');
}

// Add keyboard support (ESC key to clear search)
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        // Find any active search input and clear it
        const activeSearchInput = document.querySelector('input[name="search"]:focus, input[name*="search"]:focus');
        if (activeSearchInput) {
            const fieldName = activeSearchInput.name;
            clearSearchField(fieldName);
        }
    }
});
