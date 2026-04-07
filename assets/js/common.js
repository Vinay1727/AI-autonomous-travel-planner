// Common JavaScript utilities for all pages
// Prefer runtime-injected API base (set in HTML by hosting or index/home pages)
const API_BASE_URL = (typeof window !== 'undefined' && window.API_BASE_URL)
    ? window.API_BASE_URL
    : 'https://ai-autonomous-travel-planner-4.onrender.com';

// Utility Functions
function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = '<div style="text-align: center; padding: 2rem;"><i class="fas fa-spinner fa-spin" style="font-size: 2rem; color: var(--gold);"></i></div>';
    }
}

function showError(elementId, message) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `<div style="text-align: center; padding: 2rem; color: var(--text-secondary);">
            <i class="fas fa-exclamation-circle" style="font-size: 2rem; color: var(--gold); margin-bottom: 1rem;"></i>
            <p>${message}</p>
        </div>`;
    }
}

function formatCurrency(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency
    }).format(amount);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// API Call Wrapper with Client-side Caching (localStorage)
async function apiCall(endpoint, data = {}, forceRefresh = false) {
    const cacheKey = `api_cache_${endpoint}_${JSON.stringify(data)}`;
    
    // Check if data exists in cache and not forcing refresh
    if (!forceRefresh) {
        const cachedData = localStorage.getItem(cacheKey);
        if (cachedData) {
            try {
                const { timestamp, response } = JSON.parse(cachedData);
                // Cache valid for 30 minutes (1800000ms)
                if (Date.now() - timestamp < 1800000) {
                    console.log(`Using cached data for ${endpoint}`);
                    return response;
                } else {
                    localStorage.removeItem(cacheKey);
                }
            } catch (e) {
                localStorage.removeItem(cacheKey);
            }
        }
    }

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const jsonResponse = await response.json();
        
        // Save to cache
        try {
            localStorage.setItem(cacheKey, JSON.stringify({
                timestamp: Date.now(),
                response: jsonResponse
            }));
        } catch (e) {
            // If localStorage is full, clear old cache entries
            console.warn('LocalStorage full, clearing old API cache');
            for (let i = 0; i < localStorage.length; i++) {
                const key = localStorage.key(i);
                if (key.startsWith('api_cache_')) {
                    localStorage.removeItem(key);
                }
            }
        }

        return jsonResponse;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

function clearApiCache() {
    for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key.startsWith('api_cache_')) {
            localStorage.removeItem(key);
            i--; // Adjust index as items are removed
        }
    }
}

// Toast Notification
function showToast(message, duration = 3000) {
    const toast = document.createElement('div');
    toast.style.cssText = `
        position: fixed;
        bottom: 2rem;
        right: 2rem;
        background: var(--bg-card);
        color: var(--text-primary);
        padding: 1rem 1.5rem;
        border: 1px solid var(--border-color);
        border-left: 3px solid var(--gold);
        z-index: 9999;
        animation: slideIn 0.3s ease-out;
    `;
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

// Navbar scroll effect (common for all pages)
window.addEventListener('scroll', () => {
    const navbar = document.getElementById('navbar');
    if (navbar) {
        if (window.scrollY > 100) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    }
});

// Mobile menu toggle (common for all pages)
document.addEventListener('DOMContentLoaded', () => {
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.getElementById('navMenu');

    if (navToggle && navMenu) {
        navToggle.addEventListener('click', () => {
            navMenu.classList.toggle('active');
        });

        // Close menu when clicking on a link
        navMenu.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', () => {
                navMenu.classList.remove('active');
            });
        });
    }
});

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
