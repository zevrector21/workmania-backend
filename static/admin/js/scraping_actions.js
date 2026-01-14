function startScraping(platformId, event) {
    // Show loading indicator
    const link = event.target;
    const originalText = link.textContent;
    link.textContent = 'Starting...';
    link.style.pointerEvents = 'none';

    // Make AJAX call to start scraping
    fetch(`/api/v1/platforms/${platformId}/scraping_start/`, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCookie('csrftoken')
        },
        credentials: 'same-origin'  // Include cookies for authentication
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error('Failed to start scraping');
        }
    })
    .then(data => {
        console.log('Scraping started successfully:', data);
        // Refresh the page after successful start
        window.location.reload();
    })
    .catch(error => {
        console.error('Error starting scraping:', error);
        // Restore original text and functionality
        link.textContent = originalText;
        link.style.pointerEvents = 'auto';
        window.location.reload();
    });
}

function stopScraping(platformId, event) {
    // Show loading indicator
    const link = event.target;
    const originalText = link.textContent;
    link.textContent = 'Stopping...';
    link.style.pointerEvents = 'none';
    
    // Make AJAX call to stop scraping
    fetch(`/api/v1/platforms/${platformId}/scraping_stop/`, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCookie('csrftoken')
        },
        credentials: 'same-origin'  // Include cookies for authentication
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error('Failed to stop scraping');
        }
    })
    .then(data => {
        console.log('Scraping stopped successfully:', data);
        // Refresh the page after successful stop
        window.location.reload();
    })
    .catch(error => {
        console.error('Error stopping scraping:', error);
        // Restore original text and functionality
        link.textContent = originalText;
        link.style.pointerEvents = 'auto';
        window.location.reload();
    });
}

// Helper function to get CSRF token from cookies
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