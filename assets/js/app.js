// ==================== Configuration ====================
// Prefer a runtime-injected `window.API_BASE_URL` (set by index.html or hosting platform)
const API_BASE_URL = (typeof window !== 'undefined' && window.API_BASE_URL)
    ? window.API_BASE_URL
    : 'http://localhost:8000';

// ==================== DOM Elements ====================
const navbar = document.getElementById('navbar');
const navToggle = document.getElementById('navToggle');
const navMenu = document.getElementById('navMenu');
const loadingOverlay = document.getElementById('loadingOverlay');
const toast = document.getElementById('toast');

// ==================== Navigation ====================
// Sticky navbar on scroll
window.addEventListener('scroll', () => {
    if (window.scrollY > 100) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
});

// Mobile menu toggle
navToggle.addEventListener('click', () => {
    navMenu.classList.toggle('active');
});

// Close mobile menu on link click
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', () => {
        navMenu.classList.remove('active');
    });
});

// Smooth scroll to section
function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.scrollIntoView({ behavior: 'smooth' });
    }
}

// ==================== Tab System ====================
const tabButtons = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');

tabButtons.forEach(button => {
    button.addEventListener('click', () => {
        const tabName = button.getAttribute('data-tab');
        
        // Remove active class from all tabs
        tabButtons.forEach(btn => btn.classList.remove('active'));
        tabContents.forEach(content => content.classList.remove('active'));
        
        // Add active class to clicked tab
        button.classList.add('active');
        document.getElementById(`${tabName}-tab`).classList.add('active');
    });
});

// ==================== Utility Functions ====================
function showLoading() {
    loadingOverlay.classList.add('show');
}

function hideLoading() {
    loadingOverlay.classList.remove('show');
}

function showToast(message, duration = 3000) {
    toast.textContent = message;
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, duration);
}

function formatCurrency(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency
    }).format(amount);
}

// ==================== API Functions ====================

// Chat Agent
let chatHistory = [];

async function sendChatMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Add user message to chat
    addChatMessage(message, 'user');
    input.value = '';
    
    // Add to history
    chatHistory.push({ role: 'user', content: message });
    
    try {
        showLoading();
        const response = await fetch(`${API_BASE_URL}/api/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message, history: chatHistory })
        });
        
        const data = await response.json();
        
        if (data.success) {
            addChatMessage(data.response, 'bot');
            chatHistory.push({ role: 'assistant', content: data.response });
        } else {
            showToast('Failed to get response from AI', 3000);
        }
    } catch (error) {
        console.error('Chat error:', error);
        showToast('Error connecting to chat service', 3000);
        addChatMessage('Sorry, I\'m having trouble connecting. Please try again.', 'bot');
    } finally {
        hideLoading();
    }
}

function addChatMessage(message, type) {
    const messagesContainer = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${type}`;
    
    messageDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas fa-${type === 'user' ? 'user' : 'robot'}"></i>
        </div>
        <div class="message-content">
            <p>${message}</p>
        </div>
    `;
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Allow Enter key to send message
document.getElementById('chatInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendChatMessage();
    }
});

// Flight Search
async function searchFlights(event) {
    event.preventDefault();
    
    const from_city = document.getElementById('flightFrom').value;
    const to_city = document.getElementById('flightTo').value;
    const date = document.getElementById('flightDate').value;
    const passengers = parseInt(document.getElementById('flightPassengers').value);
    
    try {
        showLoading();
        const response = await fetch(`${API_BASE_URL}/api/flights/search`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ from_city, to_city, date, passengers })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayFlightResults(data.flights, data.is_mock);
            
            // Also get booking links
            const linksResponse = await fetch(`${API_BASE_URL}/api/flights/links`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ from_city, to_city, date })
            });
            const linksData = await linksResponse.json();
            
            if (linksData.success) {
                displayBookingLinks(linksData.links);
            }
        } else {
            showToast('No flights found', 3000);
        }
    } catch (error) {
        console.error('Flight search error:', error);
        showToast('Error searching flights', 3000);
    } finally {
        hideLoading();
    }
}

function displayFlightResults(flights, isMock) {
    const resultsContainer = document.getElementById('flightResults');
    
    if (!flights || flights.length === 0) {
        resultsContainer.innerHTML = '<p style="text-align: center; opacity: 0.7;">No flights found</p>';
        return;
    }
    
    let html = '';
    
    if (isMock) {
        html += '<div style="background: rgba(255, 193, 7, 0.2); padding: 1rem; border-radius: 10px; margin-bottom: 1rem; text-align: center;">';
        html += '<i class="fas fa-info-circle"></i> Showing demo data (API unavailable)';
        html += '</div>';
    }
    
    flights.forEach(flight => {
        html += `
            <div class="result-card">
                <div class="result-header">
                    <div>
                        <div class="result-title">${flight.airline}</div>
                        <div class="result-detail">
                            <i class="fas fa-clock"></i>
                            <span>${flight.duration} min</span>
                        </div>
                    </div>
                    <div class="result-price">${formatCurrency(flight.price)}</div>
                </div>
                <div class="result-details">
                    <div class="result-detail">
                        <i class="fas fa-plane-departure"></i>
                        <span>${flight.departure}</span>
                    </div>
                    <div class="result-detail">
                        <i class="fas fa-plane-arrival"></i>
                        <span>${flight.arrival}</span>
                    </div>
                    <div class="result-detail">
                        <i class="fas fa-tag"></i>
                        <span>${flight.type}</span>
                    </div>
                </div>
            </div>
        `;
    });
    
    resultsContainer.innerHTML = html;
}

function displayBookingLinks(links) {
    const resultsContainer = document.getElementById('flightResults');
    
    let html = '<div style="margin-top: 1.5rem; padding: 1.5rem; background: rgba(255, 255, 255, 0.05); border-radius: 15px;">';
    html += '<h4 style="margin-bottom: 1rem;"><i class="fas fa-external-link-alt"></i> Book on:</h4>';
    html += '<div style="display: flex; gap: 1rem; flex-wrap: wrap;">';
    
    for (const [provider, url] of Object.entries(links)) {
        const providerName = provider.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
        html += `<a href="${url}" target="_blank" class="btn btn-secondary" style="text-decoration: none;">
            <i class="fas fa-plane"></i> ${providerName}
        </a>`;
    }
    
    html += '</div></div>';
    resultsContainer.innerHTML += html;
}

// Weather
async function getWeather(event) {
    event.preventDefault();
    
    const city = document.getElementById('weatherCity').value;
    
    try {
        showLoading();
        const response = await fetch(`${API_BASE_URL}/api/weather`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ city })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayWeatherResults(data.data);
        } else {
            showToast('City not found', 3000);
        }
    } catch (error) {
        console.error('Weather error:', error);
        showToast('Error fetching weather data', 3000);
    } finally {
        hideLoading();
    }
}

function displayWeatherResults(weather) {
    const resultsContainer = document.getElementById('weatherResults');
    
    let html = `
        <div class="result-card">
            <div class="result-header">
                <div>
                    <div class="result-title">${weather.location}</div>
                    <div style="font-size: 3rem; margin: 1rem 0;">${weather.current_condition}</div>
                </div>
                <div class="result-price">${weather.current_temp}°C</div>
            </div>
            <div class="result-details">
                <div class="result-detail">
                    <i class="fas fa-wind"></i>
                    <span>${weather.wind_speed} km/h</span>
                </div>
            </div>
        </div>
    `;
    
    if (weather.forecast && weather.forecast.length > 0) {
        html += '<h4 style="margin: 1.5rem 0 1rem;">5-Day Forecast</h4>';
        html += '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem;">';
        
        weather.forecast.forEach(day => {
            html += `
                <div class="result-card" style="text-align: center;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">${day.condition}</div>
                    <div style="font-size: 1.25rem; font-weight: 600;">${day.max}°C / ${day.min}°C</div>
                    <div style="opacity: 0.7; margin-top: 0.5rem;">Day ${day.day + 1}</div>
                </div>
            `;
        });
        
        html += '</div>';
    }
    
    resultsContainer.innerHTML = html;
}

// Hotels
async function searchHotels(event) {
    event.preventDefault();
    
    const city = document.getElementById('hotelCity').value;
    const checkin = document.getElementById('hotelCheckin').value;
    const checkout = document.getElementById('hotelCheckout').value;
    const guests = parseInt(document.getElementById('hotelGuests').value);
    
    try {
        showLoading();
        const response = await fetch(`${API_BASE_URL}/api/hotels/search`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ city, checkin, checkout, guests })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayHotelResults(data.hotels);
        } else {
            showToast('No hotels found', 3000);
        }
    } catch (error) {
        console.error('Hotel search error:', error);
        showToast('Error searching hotels', 3000);
    } finally {
        hideLoading();
    }
}

function displayHotelResults(hotels) {
    const resultsContainer = document.getElementById('hotelResults');
    
    if (!hotels || hotels.length === 0) {
        resultsContainer.innerHTML = '<p style="text-align: center; opacity: 0.7;">No hotels found. Try searching for popular cities like Paris, London, or Tokyo.</p>';
        return;
    }
    
    let html = '';
    
    hotels.forEach(hotel => {
        const name = hotel.name || 'Hotel';
        const address = hotel.address || 'Address not available';
        
        html += `
            <div class="result-card">
                <div class="result-header">
                    <div class="result-title">${name}</div>
                </div>
                <div class="result-details">
                    <div class="result-detail">
                        <i class="fas fa-map-marker-alt"></i>
                        <span>${address}</span>
                    </div>
                </div>
            </div>
        `;
    });
    
    resultsContainer.innerHTML = html;
}

// Budget Calculator
async function calculateBudget(event) {
    event.preventDefault();
    
    const destination = document.getElementById('budgetDest').value;
    const days = parseInt(document.getElementById('budgetDays').value);
    const budget_level = document.getElementById('budgetLevel').value;
    
    try {
        showLoading();
        const response = await fetch(`${API_BASE_URL}/api/budget/estimate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ destination, days, budget_level })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayBudgetResults(data.data);
        } else {
            showToast('Error calculating budget', 3000);
        }
    } catch (error) {
        console.error('Budget error:', error);
        showToast('Error calculating budget', 3000);
    } finally {
        hideLoading();
    }
}

function displayBudgetResults(budget) {
    const resultsContainer = document.getElementById('budgetResults');
    
    let html = `
        <div class="result-card">
            <div class="result-header">
                <div class="result-title">Estimated Total Budget</div>
                <div class="result-price">${formatCurrency(budget.total_estimated)}</div>
            </div>
            <h4 style="margin: 1.5rem 0 1rem;">Budget Breakdown</h4>
            <div class="result-details">
                <div class="result-detail">
                    <i class="fas fa-bed"></i>
                    <span>Accommodation: ${formatCurrency(budget.breakdown.accommodation)}</span>
                </div>
                <div class="result-detail">
                    <i class="fas fa-utensils"></i>
                    <span>Food: ${formatCurrency(budget.breakdown.food)}</span>
                </div>
                <div class="result-detail">
                    <i class="fas fa-ticket-alt"></i>
                    <span>Activities: ${formatCurrency(budget.breakdown.activities)}</span>
                </div>
                <div class="result-detail">
                    <i class="fas fa-bus"></i>
                    <span>Transport: ${formatCurrency(budget.breakdown.transport)}</span>
                </div>
            </div>
        </div>
    `;
    
    resultsContainer.innerHTML = html;
}

// Currency Converter
async function convertCurrency(event) {
    event.preventDefault();
    
    const amount = parseFloat(document.getElementById('currencyAmount').value);
    const from_currency = document.getElementById('currencyFrom').value;
    const to_currency = document.getElementById('currencyTo').value;
    
    try {
        showLoading();
        const response = await fetch(`${API_BASE_URL}/api/currency/convert`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ amount, from_currency, to_currency })
        });
        
        const data = await response.json();
        
        if (data.success && data.data !== null) {
            displayCurrencyResults(amount, from_currency, data.data, to_currency);
        } else {
            showToast('Currency conversion failed', 3000);
        }
    } catch (error) {
        console.error('Currency error:', error);
        showToast('Error converting currency', 3000);
    } finally {
        hideLoading();
    }
}

function displayCurrencyResults(amount, fromCurrency, convertedAmount, toCurrency) {
    const resultsContainer = document.getElementById('currencyResults');
    
    let html = `
        <div class="result-card">
            <div class="result-header">
                <div class="result-title">${formatCurrency(amount, fromCurrency)}</div>
                <div style="font-size: 2rem; opacity: 0.5;"><i class="fas fa-arrow-right"></i></div>
                <div class="result-price">${formatCurrency(convertedAmount, toCurrency)}</div>
            </div>
            <div style="text-align: center; margin-top: 1rem; opacity: 0.8;">
                1 ${fromCurrency} = ${(convertedAmount / amount).toFixed(4)} ${toCurrency}
            </div>
        </div>
    `;
    
    resultsContainer.innerHTML = html;
}

// Explore Destination
async function exploreDestination(destination) {
    // Switch to weather tab and populate
    document.querySelector('[data-tab="weather"]').click();
    document.getElementById('weatherCity').value = destination;
    
    // Auto-search weather
    const weatherForm = document.getElementById('weatherForm');
    weatherForm.dispatchEvent(new Event('submit'));
    
    // Scroll to search section
    scrollToSection('search');
    
    showToast(`Exploring ${destination}...`, 2000);
}

// ==================== Initialize ====================
// Set default dates
const tomorrow = new Date();
tomorrow.setDate(tomorrow.getDate() + 1);
document.getElementById('flightDate').value = tomorrow.toISOString().split('T')[0];

const nextWeek = new Date();
nextWeek.setDate(nextWeek.getDate() + 7);
document.getElementById('hotelCheckin').value = tomorrow.toISOString().split('T')[0];
document.getElementById('hotelCheckout').value = nextWeek.toISOString().split('T')[0];

// Welcome message
setTimeout(() => {
    showToast('Welcome to Premium AI Travel AI! 🌍✨', 3000);
}, 1000);

console.log('Premium AI Travel AI initialized successfully! 🚀');
