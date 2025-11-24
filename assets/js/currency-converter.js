// Currency Converter Widget Component
// Add this to any page to enable currency conversion

function createCurrencyConverter() {
    const converterHTML = `
        <div id="currencyConverter" class="currency-converter">
            <button id="currencyToggle" class="currency-toggle-btn">
                <i class="fas fa-exchange-alt"></i>
            </button>
            
            <div id="currencyPanel" class="currency-panel">
                <div class="currency-header">
                    <h3><i class="fas fa-coins"></i> Currency Converter</h3>
                    <button id="currencyClose" class="close-btn">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                
                <div class="currency-body">
                    <div class="form-group">
                        <label class="form-label">Amount</label>
                        <input type="number" id="currencyAmount" class="form-control" value="100" min="0" step="0.01">
                    </div>
                    
                    <div class="form-group">
                        <label class="form-label">From</label>
                        <select id="currencyFrom" class="form-control">
                            <option value="USD">USD - US Dollar</option>
                            <option value="EUR">EUR - Euro</option>
                            <option value="GBP">GBP - British Pound</option>
                            <option value="JPY">JPY - Japanese Yen</option>
                            <option value="INR">INR - Indian Rupee</option>
                            <option value="AUD">AUD - Australian Dollar</option>
                            <option value="CAD">CAD - Canadian Dollar</option>
                        </select>
                    </div>
                    
                    <button id="currencySwap" class="btn btn-secondary btn-block" style="margin: 0.5rem 0;">
                        <i class="fas fa-exchange-alt"></i> Swap
                    </button>
                    
                    <div class="form-group">
                        <label class="form-label">To</label>
                        <select id="currencyTo" class="form-control">
                            <option value="USD">USD - US Dollar</option>
                            <option value="EUR" selected>EUR - Euro</option>
                            <option value="GBP">GBP - British Pound</option>
                            <option value="JPY">JPY - Japanese Yen</option>
                            <option value="INR">INR - Indian Rupee</option>
                            <option value="AUD">AUD - Australian Dollar</option>
                            <option value="CAD">CAD - Canadian Dollar</option>
                        </select>
                    </div>
                    
                    <div id="currencyResult" class="currency-result">
                        <div class="result-display">
                            <span id="convertedAmount">--</span>
                        </div>
                        <div class="rate-display">
                            <small id="exchangeRate"></small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Add to body
    document.body.insertAdjacentHTML('beforeend', converterHTML);

    // Add styles
    const style = document.createElement('style');
    style.textContent = `
        .currency-converter {
            position: fixed;
            bottom: 90px;
            right: 2rem;
            z-index: 9998;
        }

        .currency-toggle-btn {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: var(--gold);
            color: var(--pure-black);
            border: none;
            font-size: 1.5rem;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            transition: var(--transition);
        }

        .currency-toggle-btn:hover {
            transform: scale(1.1);
            box-shadow: 0 6px 16px rgba(212, 175, 55, 0.4);
        }

        .currency-panel {
            position: absolute;
            bottom: 70px;
            right: 0;
            width: 320px;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
            display: none;
            animation: slideUp 0.3s ease-out;
        }

        .currency-panel.active {
            display: block;
        }

        .currency-header {
            padding: 1.5rem;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .currency-header h3 {
            margin: 0;
            color: var(--gold);
            font-size: 1.1rem;
        }

        .close-btn {
            background: none;
            border: none;
            color: var(--text-secondary);
            font-size: 1.2rem;
            cursor: pointer;
            padding: 0.25rem;
            transition: var(--transition);
        }

        .close-btn:hover {
            color: var(--text-primary);
        }

        .currency-body {
            padding: 1.5rem;
        }

        .currency-result {
            margin-top: 1.5rem;
            padding: 1.5rem;
            background: rgba(212, 175, 55, 0.1);
            border: 1px solid var(--gold);
            border-radius: 4px;
            text-align: center;
        }

        .result-display {
            font-size: 2rem;
            font-weight: 700;
            color: var(--gold);
            margin-bottom: 0.5rem;
        }

        .rate-display {
            color: var(--text-secondary);
            font-size: 0.85rem;
        }

        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
    `;
    document.head.appendChild(style);

    // Add event listeners
    const toggle = document.getElementById('currencyToggle');
    const panel = document.getElementById('currencyPanel');
    const closeBtn = document.getElementById('currencyClose');
    const swapBtn = document.getElementById('currencySwap');
    const amountInput = document.getElementById('currencyAmount');
    const fromSelect = document.getElementById('currencyFrom');
    const toSelect = document.getElementById('currencyTo');

    toggle.addEventListener('click', () => {
        panel.classList.toggle('active');
    });

    closeBtn.addEventListener('click', () => {
        panel.classList.remove('active');
    });

    swapBtn.addEventListener('click', () => {
        const temp = fromSelect.value;
        fromSelect.value = toSelect.value;
        toSelect.value = temp;
        convertCurrency();
    });

    // Convert on input change
    amountInput.addEventListener('input', convertCurrency);
    fromSelect.addEventListener('change', convertCurrency);
    toSelect.addEventListener('change', convertCurrency);

    async function convertCurrency() {
        const amount = parseFloat(amountInput.value) || 0;
        const from = fromSelect.value;
        const to = toSelect.value;

        if (amount === 0) {
            document.getElementById('convertedAmount').textContent = '--';
            document.getElementById('exchangeRate').textContent = '';
            return;
        }

        try {
            const response = await apiCall('/api/currency/convert', {
                amount: amount,
                from_currency: from,
                to_currency: to
            });

            if (response.success && response.data) {
                const converted = response.data;
                document.getElementById('convertedAmount').textContent =
                    `${converted.toFixed(2)} ${to}`;
                document.getElementById('exchangeRate').textContent =
                    `1 ${from} = ${(converted / amount).toFixed(4)} ${to}`;
            }
        } catch (error) {
            console.error('Currency conversion error:', error);
            document.getElementById('convertedAmount').textContent = 'Error';
            document.getElementById('exchangeRate').textContent = 'Failed to convert';
        }
    }

    // Initial conversion
    convertCurrency();
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', createCurrencyConverter);
} else {
    createCurrencyConverter();
}
