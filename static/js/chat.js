/**
 * Chat UI logic — shared between campus and MindMate chatbots.
 * BOT_TYPE and API_URL are set in the HTML page before this script loads.
 * Includes end-conversation review flow.
 */

const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const typingIndicator = document.getElementById('typingIndicator');
const suggestionsContainer = document.getElementById('suggestionsContainer');

let messageCount = 0; // Track messages for end-conversation prompt

// ─── Helpers ──────────────────────────────────────────────

function formatTime(date) {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// ─── Add Messages ─────────────────────────────────────────

function addUserMessage(text) {
    const div = document.createElement('div');
    div.className = 'message user';
    div.innerHTML = `
        <div class="message-avatar">&#128100;</div>
        <div>
            <div class="message-bubble">${escapeHtml(text)}</div>
            <div class="message-time">${formatTime(new Date())}</div>
        </div>
    `;
    chatMessages.insertBefore(div, typingIndicator);
    scrollToBottom();
}

function addBotMessage(text) {
    const isMindmate = typeof BOT_TYPE !== 'undefined' && BOT_TYPE === 'mindmate';
    const div = document.createElement('div');
    div.className = `message bot${isMindmate ? ' mindmate' : ''}`;
    div.innerHTML = `
        <div class="message-avatar">${isMindmate ? '&#128155;' : '&#129302;'}</div>
        <div>
            <div class="message-bubble">${text}</div>
            <div class="message-time">${formatTime(new Date())}</div>
        </div>
    `;
    chatMessages.insertBefore(div, typingIndicator);
    scrollToBottom();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ─── Typing Animation ─────────────────────────────────────

function showTyping() {
    typingIndicator.classList.add('active');
    scrollToBottom();
}

function hideTyping() {
    typingIndicator.classList.remove('active');
}

// ─── Send Message ─────────────────────────────────────────

async function sendMessage() {
    const text = chatInput.value.trim();
    if (!text) return;

    // Hide suggestions after first message
    if (suggestionsContainer) {
        suggestionsContainer.style.display = 'none';
    }

    addUserMessage(text);
    chatInput.value = '';
    chatInput.focus();
    messageCount++;

    showTyping();

    try {
        const body = { message: text };

        // Add language from dropdown
        const langSelect = document.getElementById('langSelect');
        if (langSelect) {
            body.language = langSelect.value;
        } else if (typeof SESSION_LANG !== 'undefined') {
            body.language = SESSION_LANG;
        }

        const res = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        });

        const data = await res.json();

        // Realistic typing delay
        const delay = 500 + Math.random() * 1000;
        await new Promise(r => setTimeout(r, delay));

        hideTyping();

        if (data.response) {
            addBotMessage(data.response);

            // After every 5 messages, ask if user wants to continue
            if (messageCount > 0 && messageCount % 5 === 0) {
                setTimeout(() => showEndConversationPrompt(), 1500);
            }
        } else if (data.error) {
            addBotMessage('Sorry, something went wrong. Please try again.');
        }
    } catch (err) {
        hideTyping();
        addBotMessage('Connection error. Please check your network and try again.');
        console.error(err);
    }
}

// Send on Enter key
chatInput.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// ─── End Conversation + Review Flow ───────────────────────

function showEndConversationPrompt() {
    const isMindmate = typeof BOT_TYPE !== 'undefined' && BOT_TYPE === 'mindmate';
    const div = document.createElement('div');
    div.className = `message bot${isMindmate ? ' mindmate' : ''}`;
    div.id = 'endConvoPrompt';
    div.innerHTML = `
        <div class="message-avatar">${isMindmate ? '&#128155;' : '&#129302;'}</div>
        <div>
            <div class="message-bubble" style="text-align:center;">
                Would you like to end this conversation?
                <div style="display:flex; gap:10px; justify-content:center; margin-top:12px;">
                    <button onclick="endConversation()" style="
                        padding:8px 24px; border:none; border-radius:20px;
                        background:linear-gradient(135deg, #6C63FF, #5A52D5);
                        color:white; font-weight:600; cursor:pointer; font-size:13px;
                    ">Yes, end chat</button>
                    <button onclick="continueConversation()" style="
                        padding:8px 24px; border:2px solid #E2E8F0; border-radius:20px;
                        background:white; color:#2D3748; font-weight:600; cursor:pointer; font-size:13px;
                    ">No, continue</button>
                </div>
            </div>
            <div class="message-time">${formatTime(new Date())}</div>
        </div>
    `;
    chatMessages.insertBefore(div, typingIndicator);
    scrollToBottom();
}

function continueConversation() {
    const prompt = document.getElementById('endConvoPrompt');
    if (prompt) prompt.remove();
    const isMindmate = typeof BOT_TYPE !== 'undefined' && BOT_TYPE === 'mindmate';
    addBotMessage(isMindmate
        ? "Great, I'm glad you want to keep talking! I'm here for you. What else is on your mind? 💛"
        : "Sure! I'm here to help. What else would you like to know? 😊"
    );
}

function endConversation() {
    const prompt = document.getElementById('endConvoPrompt');
    if (prompt) prompt.remove();
    showReviewModal();
}

function showReviewModal() {
    // Create review overlay
    const overlay = document.createElement('div');
    overlay.id = 'reviewOverlay';
    overlay.style.cssText = `
        position:fixed; inset:0; background:rgba(0,0,0,0.5);
        display:flex; align-items:center; justify-content:center; z-index:9999;
    `;

    const isMindmate = typeof BOT_TYPE !== 'undefined' && BOT_TYPE === 'mindmate';
    const botName = isMindmate ? 'MindMate AI' : 'CampusConnect AI';

    overlay.innerHTML = `
        <div style="
            background:white; border-radius:20px; padding:28px 22px; width:420px; max-width:92vw;
            box-shadow:0 20px 60px rgba(0,0,0,0.2); text-align:center; animation:slideUp 0.3s ease;
            max-height:90vh; overflow-y:auto;
        ">
            <div style="font-size:40px; margin-bottom:12px;">${isMindmate ? '&#128155;' : '&#129302;'}</div>
            <h3 style="font-size:20px; font-weight:700; margin-bottom:8px;">How was your experience?</h3>
            <p style="font-size:14px; color:#718096; margin-bottom:20px;">Rate your chat with ${botName}</p>

            <!-- Star Rating -->
            <div id="starRating" style="display:flex; justify-content:center; gap:8px; margin-bottom:20px;">
                ${[1,2,3,4,5].map(n => `
                    <span class="review-star" data-value="${n}" onclick="setRating(${n})" style="
                        font-size:36px; cursor:pointer; color:#E2E8F0; transition:all 0.2s;
                    ">&#9733;</span>
                `).join('')}
            </div>

            <!-- Feedback -->
            <textarea id="reviewFeedback" placeholder="Tell us more about your experience (optional)..." style="
                width:100%; padding:14px; border:2px solid #E2E8F0; border-radius:12px;
                font-size:14px; min-height:80px; resize:vertical; font-family:inherit;
                margin-bottom:16px;
            "></textarea>

            <!-- Buttons -->
            <div style="display:flex; gap:12px; justify-content:center;">
                <button onclick="submitReview()" id="submitReviewBtn" disabled style="
                    padding:12px 32px; border:none; border-radius:12px;
                    background:linear-gradient(135deg, #6C63FF, #5A52D5);
                    color:white; font-weight:700; cursor:pointer; font-size:15px;
                    opacity:0.5; transition:all 0.3s;
                ">Submit Review</button>
                <button onclick="skipReview()" style="
                    padding:12px 24px; border:2px solid #E2E8F0; border-radius:12px;
                    background:white; color:#718096; font-weight:600; cursor:pointer; font-size:14px;
                ">Skip</button>
            </div>
        </div>
    `;

    document.body.appendChild(overlay);
}

let selectedRating = 0;

function setRating(value) {
    selectedRating = value;
    document.querySelectorAll('.review-star').forEach(star => {
        const v = parseInt(star.dataset.value);
        star.style.color = v <= value ? '#F6E05E' : '#E2E8F0';
        star.style.transform = v <= value ? 'scale(1.2)' : 'scale(1)';
    });
    const btn = document.getElementById('submitReviewBtn');
    btn.disabled = false;
    btn.style.opacity = '1';
}

async function submitReview() {
    const feedback = document.getElementById('reviewFeedback').value.trim();

    try {
        await fetch('/api/review', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                rating: selectedRating,
                feedback: feedback,
                bot_type: typeof BOT_TYPE !== 'undefined' ? BOT_TYPE : 'campus'
            })
        });
    } catch (err) {
        console.error('Review submit error:', err);
    }

    closeReviewAndRedirect('Thank you for your feedback! 💛');
}

function skipReview() {
    closeReviewAndRedirect(null);
}

function closeReviewAndRedirect(message) {
    const overlay = document.getElementById('reviewOverlay');
    if (overlay) overlay.remove();

    if (message) {
        addBotMessage(message);
    }

    // Redirect to dashboard after short delay
    setTimeout(() => {
        window.location.href = '/dashboard';
    }, 1500);
}

// ─── End Chat Button (accessible anytime) ─────────────────

// Add an "End Chat" button to the header if not already present
(function addEndChatButton() {
    const headerRight = document.querySelector('.chat-header-right');
    if (headerRight) {
        const endBtn = document.createElement('button');
        endBtn.textContent = 'End Chat';
        endBtn.style.cssText = `
            padding:6px 12px; border:2px solid #E27070; border-radius:8px;
            background:transparent; color:#E27070; font-weight:600; font-size:12px;
            cursor:pointer; transition:all 0.3s; white-space:nowrap;
        `;
        endBtn.onmouseenter = () => { endBtn.style.background = '#F56565'; endBtn.style.color = 'white'; };
        endBtn.onmouseleave = () => { endBtn.style.background = 'transparent'; endBtn.style.color = '#F56565'; };
        endBtn.onclick = () => showReviewModal();
        headerRight.insertBefore(endBtn, headerRight.firstChild);
    }
})();

// ─── Quick / Suggestion Messages ──────────────────────────

function sendQuickMessage(btn) {
    chatInput.value = btn.textContent.trim();
    sendMessage();
}

// ─── Load Suggested Questions (Campus Bot) ────────────────

async function loadSuggestions() {
    if (typeof BOT_TYPE === 'undefined' || BOT_TYPE !== 'campus') return;

    try {
        const langSelect = document.getElementById('langSelect');
        const lang = langSelect ? langSelect.value : 'en';
        const actualLang = lang === 'auto' ? 'en' : lang;

        const res = await fetch(`/api/suggestions?language=${actualLang}`);
        const data = await res.json();

        if (suggestionsContainer && data.suggestions) {
            suggestionsContainer.innerHTML = data.suggestions.map(q =>
                `<button class="suggestion-btn" onclick="sendQuickMessage(this)">${q}</button>`
            ).join('');
        }
    } catch (err) {
        console.error('Failed to load suggestions:', err);
    }
}

// Reload suggestions when language changes
const langSelect = document.getElementById('langSelect');
if (langSelect) {
    langSelect.addEventListener('change', loadSuggestions);
}

// ─── Voice Input (Web Speech API) ─────────────────────────

let recognition = null;
let isRecording = false;

function toggleVoice() {
    const voiceBtn = document.getElementById('voiceBtn');

    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        alert('Voice input is not supported in your browser. Please use Chrome or Edge.');
        return;
    }

    if (isRecording) {
        recognition.stop();
        voiceBtn.classList.remove('recording');
        isRecording = false;
        return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.lang = getRecognitionLang();
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = function () {
        isRecording = true;
        voiceBtn.classList.add('recording');
    };

    recognition.onresult = function (event) {
        const transcript = event.results[0][0].transcript;
        chatInput.value = transcript;
        voiceBtn.classList.remove('recording');
        isRecording = false;
    };

    recognition.onerror = function () {
        voiceBtn.classList.remove('recording');
        isRecording = false;
    };

    recognition.onend = function () {
        voiceBtn.classList.remove('recording');
        isRecording = false;
    };

    recognition.start();
}

function getRecognitionLang() {
    const langSelect = document.getElementById('langSelect');
    if (!langSelect) return 'en-IN';

    const map = {
        'en': 'en-IN',
        'hi': 'hi-IN',
        'mr': 'mr-IN',
        'auto': 'en-IN'
    };
    return map[langSelect.value] || 'en-IN';
}
