// AI Chatbot Component
// Add this to any page to enable AI travel assistant chat

function createChatbot() {
    const chatbotHTML = `
        <div id="chatbot" class="chatbot">
            <button id="chatToggle" class="chat-toggle-btn">
                <i class="fas fa-comments"></i>
            </button>
            
            <div id="chatPanel" class="chat-panel">
                <div class="chat-header">
                    <h3><i class="fas fa-robot"></i> AI Travel Assistant</h3>
                    <button id="chatClose" class="close-btn">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                
                <div id="chatMessages" class="chat-messages">
                    <div class="chat-message bot-message">
                        <div class="message-content">
                            <strong>AI Assistant</strong>
                            <p>Hello! I'm your AI travel assistant. Ask me anything about travel planning, destinations, or tips!</p>
                        </div>
                    </div>
                </div>
                
                <div class="chat-input-container">
                    <input type="text" id="chatInput" class="chat-input" placeholder="Ask me anything about travel...">
                    <button id="chatSend" class="chat-send-btn">
                        <i class="fas fa-paper-plane"></i>
                    </button>
                </div>
            </div>
        </div>
    `;

    // Add to body
    document.body.insertAdjacentHTML('beforeend', chatbotHTML);

    // Add styles
    const style = document.createElement('style');
    style.textContent = `
        .chatbot {
            position: fixed;
            bottom: 2rem;
            right: 2rem;
            z-index: 9999;
        }

        .chat-toggle-btn {
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

        .chat-toggle-btn:hover {
            transform: scale(1.1);
            box-shadow: 0 6px 16px rgba(212, 175, 55, 0.4);
        }

        .chat-panel {
            position: absolute;
            bottom: 70px;
            right: 0;
            width: 380px;
            height: 500px;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
            display: none;
            flex-direction: column;
            animation: slideUp 0.3s ease-out;
        }

        .chat-panel.active {
            display: flex;
        }

        .chat-header {
            padding: 1.5rem;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: var(--medium-dark);
        }

        .chat-header h3 {
            margin: 0;
            color: var(--gold);
            font-size: 1.1rem;
        }

        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }

        .chat-message {
            display: flex;
            flex-direction: column;
            max-width: 85%;
        }

        .bot-message {
            align-self: flex-start;
        }

        .user-message {
            align-self: flex-end;
        }

        .message-content {
            padding: 1rem;
            border-radius: 8px;
            line-height: 1.6;
        }

        .bot-message .message-content {
            background: var(--medium-dark);
            border: 1px solid var(--border-color);
        }

        .user-message .message-content {
            background: rgba(212, 175, 55, 0.2);
            border: 1px solid var(--gold);
        }

        .message-content strong {
            color: var(--gold);
            display: block;
            margin-bottom: 0.5rem;
            font-size: 0.85rem;
        }

        .message-content p {
            margin: 0;
            color: var(--text-secondary);
        }

        .chat-input-container {
            padding: 1rem;
            border-top: 1px solid var(--border-color);
            display: flex;
            gap: 0.75rem;
        }

        .chat-input {
            flex: 1;
            padding: 0.75rem;
            background: var(--medium-dark);
            border: 1px solid var(--border-color);
            color: var(--text-primary);
            border-radius: 4px;
            font-family: inherit;
        }

        .chat-input:focus {
            outline: none;
            border-color: var(--gold);
        }

        .chat-send-btn {
            padding: 0.75rem 1.25rem;
            background: var(--gold);
            color: var(--pure-black);
            border: none;
            border-radius: 4px;
            cursor: pointer;
            transition: var(--transition);
        }

        .chat-send-btn:hover {
            opacity: 0.9;
        }

        .chat-send-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .typing-indicator {
            display: flex;
            gap: 0.25rem;
            padding: 1rem;
        }

        .typing-dot {
            width: 8px;
            height: 8px;
            background: var(--gold);
            border-radius: 50%;
            animation: typing 1.4s infinite;
        }

        .typing-dot:nth-child(2) {
            animation-delay: 0.2s;
        }

        .typing-dot:nth-child(3) {
            animation-delay: 0.4s;
        }

        @keyframes typing {
            0%, 60%, 100% {
                opacity: 0.3;
                transform: translateY(0);
            }
            30% {
                opacity: 1;
                transform: translateY(-10px);
            }
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

    // Chat history
    let chatHistory = [];

    // Add event listeners
    const toggle = document.getElementById('chatToggle');
    const panel = document.getElementById('chatPanel');
    const closeBtn = document.getElementById('chatClose');
    const input = document.getElementById('chatInput');
    const sendBtn = document.getElementById('chatSend');
    const messagesContainer = document.getElementById('chatMessages');

    toggle.addEventListener('click', () => {
        panel.classList.toggle('active');
        if (panel.classList.contains('active')) {
            input.focus();
        }
    });

    closeBtn.addEventListener('click', () => {
        panel.classList.remove('active');
    });

    sendBtn.addEventListener('click', sendMessage);
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    async function sendMessage() {
        const message = input.value.trim();
        if (!message) return;

        // Add user message to UI
        addMessage(message, 'user');
        input.value = '';
        sendBtn.disabled = true;

        // Add to history
        chatHistory.push({ role: 'user', content: message });

        // Show typing indicator
        const typingIndicator = document.createElement('div');
        typingIndicator.className = 'typing-indicator';
        typingIndicator.innerHTML = `
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        `;
        messagesContainer.appendChild(typingIndicator);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        try {
            const response = await apiCall('/api/chat', {
                message: message,
                history: chatHistory
            });

            // Remove typing indicator
            typingIndicator.remove();

            if (response.success && response.response) {
                addMessage(response.response, 'bot');
                chatHistory.push({ role: 'assistant', content: response.response });
            } else {
                addMessage('Sorry, I encountered an error. Please try again.', 'bot');
            }
        } catch (error) {
            typingIndicator.remove();
            console.error('Chat error:', error);
            addMessage('Sorry, I\'m having trouble connecting. Please try again later.', 'bot');
        }

        sendBtn.disabled = false;
        input.focus();
    }

    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${sender}-message`;

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        const senderLabel = sender === 'user' ? 'You' : 'AI Assistant';
        contentDiv.innerHTML = `
            <strong>${senderLabel}</strong>
            <p>${text}</p>
        `;

        messageDiv.appendChild(contentDiv);
        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', createChatbot);
} else {
    createChatbot();
}
