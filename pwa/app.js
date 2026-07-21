// ============================================
// VQA Assistant – Rewritten App Logic
// ============================================

// Configuration
const CONFIG = {
    apiUrl: 'https://sakthi04-vqa-app.hf.space',
    speechRate: 0.9,
    autoCapture: false,
    qualityCheck: true,   // soft warning only – never blocks
    demoMode: false,
    timeoutMs: 15000      // 15 s API timeout
};

// Always ensure production URL (never localhost from old sessions)
const _savedUrl = localStorage.getItem('apiUrl');
if (!_savedUrl || _savedUrl.includes('localhost') || _savedUrl.includes('127.0.0.1')) {
    localStorage.setItem('apiUrl', CONFIG.apiUrl);
}

// ── DOM Elements ──────────────────────────────
const camera       = document.getElementById('camera');
const canvas       = document.getElementById('canvas');
const mainBtn      = document.getElementById('mainBtn');
const btnText      = document.getElementById('btnText');
const iconCamera   = document.getElementById('iconCamera');
const iconMic      = document.getElementById('iconMic');
const iconSpin     = document.getElementById('iconSpin');
const statusPill   = document.getElementById('statusPill');
const statusIcon   = document.getElementById('statusIcon');
const statusText   = document.getElementById('statusText');
const statusDiv    = document.getElementById('status');          // sr-only
const answerCard   = document.getElementById('answerCard');
const answerText   = document.getElementById('answerText');
const suggestionBox  = document.getElementById('suggestionBox');
const suggestionText = document.getElementById('suggestionText');
const dismissAnswer  = document.getElementById('dismissAnswer');
const qualityBadge   = document.getElementById('qualityBadge');
const hintText       = document.getElementById('hintText');
const settingsBtn    = document.getElementById('settingsBtn');
const settingsModal  = document.getElementById('settingsModal');
const closeSettings  = document.getElementById('closeSettings');
const apiUrlInput    = document.getElementById('apiUrl');
const speechRateInput = document.getElementById('speechRate');
const speechRateVal  = document.getElementById('speechRateVal');
const qualityCheck   = document.getElementById('qualityCheck');
const demoModeToggle = document.getElementById('demoMode');
const testApiBtn     = document.getElementById('testApi');
const apiStatusDot   = document.getElementById('apiStatus');

// ── State ─────────────────────────────────────
let stream         = null;
let isListening    = false;
let capturedImage  = null;

// ── Speech Recognition ────────────────────────
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = SpeechRecognition ? new SpeechRecognition() : null;

if (recognition) {
    recognition.continuous     = false;
    recognition.lang           = 'en-US';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
}

// ============================================
// Camera
// ============================================

async function startCamera() {
    try {
        stream = await navigator.mediaDevices.getUserMedia({
            video: {
                facingMode: { ideal: 'environment' },
                width:  { ideal: 1280 },
                height: { ideal: 720 }
            }
        });
        camera.srcObject = stream;
        updateStatus('Ready', 'idle');
        speak('Camera ready. Tap the button to capture a photo and ask your question.');
    } catch (error) {
        console.error('Camera error:', error);
        updateStatus('Camera access denied', 'error');
        speak('Camera access denied. Please enable camera permissions.');
    }
}

// ============================================
// Image Quality (soft warning only)
// ============================================

function analyzeImageQuality() {
    const ctx = canvas.getContext('2d');
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const pixels = imageData.data;
    const pixelCount = pixels.length / 4;

    let totalBrightness = 0;
    for (let i = 0; i < pixels.length; i += 4) {
        totalBrightness += 0.299 * pixels[i] + 0.587 * pixels[i + 1] + 0.114 * pixels[i + 2];
    }
    const avgBrightness = totalBrightness / pixelCount;

    let variance = 0;
    for (let i = 0; i < pixels.length; i += 4) {
        const b = 0.299 * pixels[i] + 0.587 * pixels[i + 1] + 0.114 * pixels[i + 2];
        variance += Math.pow(b - avgBrightness, 2);
    }
    const sharpness = variance / pixelCount;

    const tips = [];
    if (avgBrightness < 40)      tips.push('⚠️ Very dark – turn on a light');
    else if (avgBrightness < 80) tips.push('⚠️ Dim image – move to brighter area');
    if (avgBrightness > 220)     tips.push('⚠️ Too bright – avoid direct light');
    if (sharpness < 100)         tips.push('⚠️ Blurry – hold camera steady');

    return { avgBrightness, sharpness, tips };
}

function capturePhoto() {
    const ctx = canvas.getContext('2d');
    canvas.width  = camera.videoWidth;
    canvas.height = camera.videoHeight;
    ctx.drawImage(camera, 0, 0);

    if (CONFIG.qualityCheck) {
        const quality = analyzeImageQuality();
        if (quality.tips.length > 0) {
            // Soft warning: show badge but STILL proceed
            showQualityBadge(quality.tips[0]);
        } else {
            hideQualityBadge();
        }
    }

    // Always proceed to question capture
    canvas.toBlob((blob) => {
        capturedImage = blob;
        vibrate(100);
        startListening();
    }, 'image/jpeg', 0.92);
}

function showQualityBadge(msg) {
    qualityBadge.textContent = msg;
    qualityBadge.classList.remove('hidden');
    setTimeout(hideQualityBadge, 4000);
}
function hideQualityBadge() {
    qualityBadge.classList.add('hidden');
}

// ============================================
// Voice / Speech
// ============================================

function speak(text, onEnd = null) {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate   = CONFIG.speechRate;
    utterance.pitch  = 1;
    utterance.volume = 1;
    if (onEnd) utterance.onend = onEnd;
    speechSynthesis.cancel();
    speechSynthesis.speak(utterance);
}

function startListening() {
    if (!recognition) {
        updateStatus('Speech recognition not supported', 'error');
        speak('Speech recognition is not supported in this browser.');
        return;
    }
    isListening = true;
    mainBtn.classList.add('listening');
    setButtonState('listening');
    updateStatus('Listening…', 'listening');
    hintText.textContent = 'Speak your question now…';
    speak('What would you like to know?');
    vibrate(50);
    recognition.start();
}

function stopListening() {
    if (recognition && isListening) {
        recognition.stop();
        isListening = false;
        mainBtn.classList.remove('listening');
        setButtonState('idle');
        hintText.textContent = 'Tap to capture a photo, then ask your question';
    }
}

// ── Button icon states ─────────────────────
function setButtonState(state) {
    // hide all icons
    iconCamera.classList.add('hidden');
    iconMic.classList.add('hidden');
    iconSpin.classList.add('hidden');

    if (state === 'idle') {
        iconCamera.classList.remove('hidden');
        btnText.textContent = 'Capture';
        mainBtn.classList.remove('listening', 'processing');
    } else if (state === 'listening') {
        iconMic.classList.remove('hidden');
        btnText.textContent = 'Listening…';
    } else if (state === 'processing') {
        iconSpin.classList.remove('hidden');
        btnText.textContent = 'Analyzing…';
        mainBtn.classList.add('processing');
    }
}

// ============================================
// API
// ============================================

async function sendToAPI(imageBlob, question) {
    setButtonState('processing');
    updateStatus('Analyzing image…', 'processing');
    hideAnswerCard();

    try {
        // ── Demo mode ──────────────────────────
        if (CONFIG.demoMode) {
            await new Promise(r => setTimeout(r, 1800));
            let answer = 'Demo mode is active. ';
            const q = question.toLowerCase();
            if (q.includes('color') || q.includes('colour')) answer += 'I can see a mix of colors in this image.';
            else if (q.includes('what') || q.includes('see'))  answer += 'I can see a person in an indoor environment.';
            else if (q.includes('read') || q.includes('text')) answer += 'I can see some text in the image.';
            else answer += 'I can observe the scene in this image. Please deploy the backend for real answers.';

            showAnswer(answer, null);
            speak(answer);
            vibrate([100, 50, 100]);
            setButtonState('idle');
            updateStatus('Done', 'success');
            return;
        }

        // ── Real API call with timeout ─────────
        const formData = new FormData();
        formData.append('image', imageBlob, 'photo.jpg');
        formData.append('question', question);

        const controller = new AbortController();
        const timer = setTimeout(() => controller.abort(), CONFIG.timeoutMs);

        let response;
        try {
            response = await fetch(`${CONFIG.apiUrl}/api/vqa`, {
                method: 'POST',
                body: formData,
                signal: controller.signal
            });
            clearTimeout(timer);
        } catch (netError) {
            clearTimeout(timer);

            if (netError.name === 'AbortError') {
                throw new Error('Request timed out after 15 seconds. The server may be waking up – please try again.');
            }

            // Auto-switch to production if localhost fails
            if (CONFIG.apiUrl.includes('localhost') || CONFIG.apiUrl.includes('127.0.0.1')) {
                updateStatus('Switching to cloud server…', 'warning');
                speak('Local connection failed. Switching to cloud.');
                CONFIG.apiUrl = 'https://sakthi04-vqa-app.hf.space';
                apiUrlInput.value = CONFIG.apiUrl;
                localStorage.setItem('apiUrl', CONFIG.apiUrl);

                const ctrl2 = new AbortController();
                const timer2 = setTimeout(() => ctrl2.abort(), CONFIG.timeoutMs);
                response = await fetch(`${CONFIG.apiUrl}/api/vqa`, {
                    method: 'POST',
                    body: formData,
                    signal: ctrl2.signal
                });
                clearTimeout(timer2);
            } else {
                throw netError;
            }
        }

        if (!response.ok) {
            const errBody = await response.text().catch(() => '');
            throw new Error(`Server error ${response.status}${errBody ? ': ' + errBody.slice(0, 80) : ''}`);
        }

        const data = await response.json();

        if (data.success) {
            const recommendation = data.recommendation || null;
            showAnswer(data.answer, recommendation);
            speak(data.answer + (recommendation ? `. ${recommendation}` : ''));
            vibrate([100, 50, 100]);
            updateStatus('Done', 'success');
        } else {
            throw new Error(data.error || 'No answer received from server.');
        }

    } catch (error) {
        console.error('API error:', error);
        const msg = error.message || 'Unknown error';
        updateStatus(`Error: ${msg}`, 'error');
        showAnswer(`❌ ${msg}`, null);
        speak('Sorry, I could not process your request. ' + msg);
        vibrate([200, 100, 200]);
    } finally {
        setButtonState('idle');
    }
}

// ============================================
// Answer Card
// ============================================

function showAnswer(text, suggestion) {
    answerText.textContent = text;
    if (suggestion) {
        suggestionText.textContent = suggestion;
        suggestionBox.classList.remove('hidden');
    } else {
        suggestionBox.classList.add('hidden');
    }
    answerCard.classList.remove('hidden');
}

function hideAnswerCard() {
    answerCard.classList.add('hidden');
}

dismissAnswer.addEventListener('click', hideAnswerCard);

// ============================================
// Status
// ============================================

const PILL_CONFIG = {
    idle:       { icon: '●', label: 'Ready' },
    success:    { icon: '✓', label: 'Done' },
    error:      { icon: '✕', label: 'Error' },
    warning:    { icon: '⚠', label: 'Warning' },
    processing: { icon: '◌', label: 'Processing' },
    listening:  { icon: '♪', label: 'Listening' }
};

function updateStatus(message, type = 'idle') {
    const cfg = PILL_CONFIG[type] || PILL_CONFIG.idle;
    statusPill.className = `status-pill ${type}`;
    statusIcon.textContent = cfg.icon;
    statusText.textContent = message || cfg.label;
    // sr-only for screen readers
    statusDiv.textContent = message;
}

function vibrate(pattern) {
    if ('vibrate' in navigator) navigator.vibrate(pattern);
}

// ============================================
// Speech Recognition Handlers
// ============================================

if (recognition) {
    recognition.onresult = (event) => {
        const question = event.results[0][0].transcript;
        console.log('Question:', question);
        stopListening();
        updateStatus(`"${question}"`, 'processing');
        hintText.textContent = `You asked: "${question}"`;
        if (capturedImage) {
            sendToAPI(capturedImage, question);
        } else {
            updateStatus('No image captured', 'error');
            speak('Please capture an image first.');
        }
    };

    recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        stopListening();
        if (event.error === 'no-speech') {
            updateStatus('No speech detected – try again', 'warning');
            speak('I did not hear anything. Please try again.');
        } else {
            updateStatus(`Speech error: ${event.error}`, 'error');
            speak('Sorry, there was an error. Please try again.');
        }
    };

    recognition.onend = () => {
        if (isListening) stopListening();
    };
}

// ============================================
// Event Listeners
// ============================================

mainBtn.addEventListener('click', () => {
    if (!isListening) capturePhoto();
});

settingsBtn.addEventListener('click', () => {
    settingsModal.hidden = false;
    speak('Settings opened');
});

closeSettings.addEventListener('click', () => {
    CONFIG.apiUrl     = apiUrlInput.value;
    CONFIG.speechRate = parseFloat(speechRateInput.value);
    CONFIG.qualityCheck = qualityCheck.checked;
    CONFIG.demoMode   = demoModeToggle.checked;
    localStorage.setItem('apiUrl', CONFIG.apiUrl);
    localStorage.setItem('speechRate', CONFIG.speechRate);
    settingsModal.hidden = true;
    speak('Settings saved');
});

// Close modal on backdrop click
settingsModal.querySelector('.modal-backdrop').addEventListener('click', () => {
    settingsModal.hidden = true;
});

// Speech rate display
speechRateInput.addEventListener('input', () => {
    speechRateVal.textContent = `${speechRateInput.value}×`;
});

// Test API connection
testApiBtn.addEventListener('click', async () => {
    apiStatusDot.className = 'api-status-dot checking';
    testApiBtn.textContent = 'Testing…';
    try {
        const res = await fetch(`${apiUrlInput.value}/api/health`, { method: 'GET', signal: AbortSignal.timeout(8000) });
        if (res.ok) {
            apiStatusDot.className = 'api-status-dot ok';
            testApiBtn.textContent = '✓ Connected';
        } else {
            apiStatusDot.className = 'api-status-dot fail';
            testApiBtn.textContent = `✕ HTTP ${res.status}`;
        }
    } catch {
        apiStatusDot.className = 'api-status-dot fail';
        testApiBtn.textContent = '✕ Unreachable';
    }
    setTimeout(() => { testApiBtn.textContent = 'Test Connection'; }, 3000);
});

// ============================================
// Service Worker
// ============================================

if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('sw.js')
        .then(reg => console.log('SW registered:', reg))
        .catch(err => console.error('SW failed:', err));
}

// ============================================
// Voice Commands
// ============================================

let isVoiceCommandMode = false;
let voiceCommandRecognition = null;

if (SpeechRecognition) {
    voiceCommandRecognition = new SpeechRecognition();
    voiceCommandRecognition.continuous      = true;
    voiceCommandRecognition.interimResults  = false;
    voiceCommandRecognition.lang            = 'en-US';

    voiceCommandRecognition.onresult = (event) => {
        const cmd = event.results[event.results.length - 1][0].transcript.toLowerCase().trim();
        console.log('Voice command:', cmd);

        if (cmd.includes('take photo') || cmd.includes('capture') || cmd.includes('take picture')) {
            speak('Taking photo now');
            vibrate(100);
            capturePhoto();
        } else if (cmd.includes('help')) {
            speak('Say "take photo" to capture. After capturing, speak your question. You can also tap the large button.');
        } else if (cmd.includes('settings')) {
            settingsModal.hidden = false;
            speak('Settings opened');
        }
    };

    voiceCommandRecognition.onerror = (event) => {
        if (event.error !== 'no-speech') console.error('Voice cmd error:', event.error);
    };
}

function startVoiceCommands() {
    if (voiceCommandRecognition && !isVoiceCommandMode) {
        try {
            voiceCommandRecognition.start();
            isVoiceCommandMode = true;
        } catch (e) { /* already running */ }
    }
}

// ============================================
// Initialize
// ============================================

window.addEventListener('load', () => {
    startCamera();

    // Restore saved settings
    const savedRate = localStorage.getItem('speechRate');
    if (savedRate) {
        CONFIG.speechRate = parseFloat(savedRate);
        speechRateInput.value = savedRate;
        speechRateVal.textContent = `${savedRate}×`;
    }

    CONFIG.apiUrl       = 'https://sakthi04-vqa-app.hf.space';
    apiUrlInput.value   = CONFIG.apiUrl;
    qualityCheck.checked  = CONFIG.qualityCheck;
    demoModeToggle.checked = CONFIG.demoMode;

    setTimeout(() => {
        speak('Welcome to VQA Assistant. Tap the button to capture a photo and ask your question.', () => {
            setTimeout(() => {
                startVoiceCommands();
            }, 500);
        });
    }, 1500);
});

apiUrlInput.addEventListener('change', () => localStorage.setItem('apiUrl', apiUrlInput.value));
speechRateInput.addEventListener('change', () => localStorage.setItem('speechRate', speechRateInput.value));
