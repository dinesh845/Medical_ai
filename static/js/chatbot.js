// ===========================
// AI Health Chatbot
// ===========================

let chatHistory = [];
let isWaitingForResponse = false;

// Initialize chatbot
document.addEventListener('DOMContentLoaded', function() {
    initializeChatbot();
});

function initializeChatbot() {
    const chatbotToggle = document.getElementById('chatbotToggle');
    const chatbotContainer = document.getElementById('chatbotContainer');
    const chatbotClose = document.getElementById('chatbotClose');
    const chatbotSend = document.getElementById('chatbotSend');
    const chatbotInput = document.getElementById('chatbotInput');

    // Toggle chatbot visibility
    if (chatbotToggle) {
        chatbotToggle.addEventListener('click', function() {
            chatbotContainer.classList.toggle('active');
            if (chatbotContainer.classList.contains('active')) {
                chatbotInput.focus();
            }
        });
    }

    // Close chatbot
    if (chatbotClose) {
        chatbotClose.addEventListener('click', function() {
            chatbotContainer.classList.remove('active');
        });
    }

    // Send message on button click
    if (chatbotSend) {
        chatbotSend.addEventListener('click', sendMessage);
    }

    // Send message on Enter key
    if (chatbotInput) {
        chatbotInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }
}

async function sendMessage() {
    const input = document.getElementById('chatbotInput');
    const message = input.value.trim();

    if (!message || isWaitingForResponse) return;

    // Add user message to chat
    addMessageToChat('user', message);
    
    // Clear input
    input.value = '';

    // Add to chat history
    chatHistory.push({ role: 'user', content: message });

    // Show typing indicator
    showTypingIndicator();

    isWaitingForResponse = true;

    try {
        // Send to API
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                history: chatHistory
            })
        });

        const data = await response.json();

        // Remove typing indicator
        removeTypingIndicator();

        if (data.success) {
            // Add bot response
            addMessageToChat('bot', data.response);
            
            // Add to chat history
            chatHistory.push({ role: 'bot', content: data.response });

            // Update suggestions if provided
            if (data.suggestions && data.suggestions.length > 0) {
                updateSuggestions(data.suggestions);
            }
        } else {
            addMessageToChat('bot', 'I apologize, but I encountered an error. Please try again.');
        }
    } catch (error) {
        removeTypingIndicator();
        addMessageToChat('bot', 'I\'m having trouble connecting. Please check your connection and try again.');
        console.error('Chat error:', error);
    }

    isWaitingForResponse = false;
}

function addMessageToChat(sender, message) {
    const messagesContainer = document.getElementById('chatbotMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${sender}-message`;

    const currentTime = new Date().toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit' 
    });

    if (sender === 'bot') {
        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content">
                <p>${formatMessage(message)}</p>
                <span class="message-time">${currentTime}</span>
            </div>
        `;
    } else {
        messageDiv.innerHTML = `
            <div class="message-content">
                <p>${escapeHtml(message)}</p>
                <span class="message-time">${currentTime}</span>
            </div>
            <div class="message-avatar">
                <i class="fas fa-user"></i>
            </div>
        `;
    }

    messagesContainer.appendChild(messageDiv);
    
    // Smooth scroll to bottom
    messagesContainer.scrollTo({
        top: messagesContainer.scrollHeight,
        behavior: 'smooth'
    });

    // Add animation
    setTimeout(() => {
        messageDiv.style.opacity = '1';
        messageDiv.style.transform = 'translateY(0)';
    }, 10);
}

function formatMessage(message) {
    // Convert markdown-style formatting to HTML
    message = escapeHtml(message);
    
    // Bold text **text**
    message = message.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Line breaks
    message = message.replace(/\n/g, '<br>');
    
    // Lists
    message = message.replace(/^- (.*?)$/gm, '<li>$1</li>');
    message = message.replace(/^(\d+)\. (.*?)$/gm, '<li>$2</li>');
    
    return message;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showTypingIndicator() {
    const messagesContainer = document.getElementById('chatbotMessages');
    const typingDiv = document.createElement('div');
    typingDiv.className = 'chat-message bot-message typing-indicator';
    typingDiv.id = 'typingIndicator';
    
    typingDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas fa-robot"></i>
        </div>
        <div class="message-content">
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;
    
    messagesContainer.appendChild(typingDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function removeTypingIndicator() {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

function updateSuggestions(suggestions) {
    const suggestionsContainer = document.getElementById('chatbotSuggestions');
    suggestionsContainer.innerHTML = '';
    
    suggestions.forEach(suggestion => {
        const chip = document.createElement('button');
        chip.className = 'suggestion-chip';
        chip.textContent = suggestion;
        chip.onclick = () => sendSuggestion(suggestion);
        suggestionsContainer.appendChild(chip);
    });
}

function sendSuggestion(text) {
    const input = document.getElementById('chatbotInput');
    input.value = text;
    sendMessage();
}

// Quick action buttons
function startEmergencyChat() {
    const chatbotContainer = document.getElementById('chatbotContainer');
    chatbotContainer.classList.add('active');
    
    setTimeout(() => {
        sendSuggestion('I need urgent help');
    }, 500);
}

function clearChat() {
    const messagesContainer = document.getElementById('chatbotMessages');
    chatHistory = [];
    messagesContainer.innerHTML = `
        <div class="chat-message bot-message">
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="message-content">
                <p>Hello! 👋 I'm your AI Medical Assistant. I can help you understand symptoms and provide health guidance. What can I help you with today?</p>
                <span class="message-time">Just now</span>
            </div>
        </div>
    `;
    
    updateSuggestions([
        'I have a fever',
        'I\'m feeling unwell',
        'General health questions'
    ]);
}

// Export chat history
function exportChatHistory() {
    const chatText = chatHistory.map(msg => {
        return `[${msg.role.toUpperCase()}]: ${msg.content}`;
    }).join('\n\n');
    
    const blob = new Blob([chatText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `medical-chat-${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}
