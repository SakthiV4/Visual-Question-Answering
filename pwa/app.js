// ============================================
// VQA Accessibility App - Main JavaScript
// ============================================

// Configuration
const CONFIG = {
    // Use demo mode if backend not deployed
    // Change this to your backend URL when deployed (e.g., Render, AWS, etc.)
    apiUrl: 'https://sakthi04-vqa-app.hf.space', // Backend API URL
    speechRate: 0.9,
    autoCapture: false
};

// DOM Elements
const camera = document.getElementById('camera');
const canvas = document.getElementById('canvas');
const mainBtn = document.getElementById('mainBtn');
const btnText = document.getElementById('btnText');
const statusDiv = document.getElementById('status');
const settingsBtn = document.getElementById('settingsBtn');
const settingsModal = document.getElementById('settingsModal');
const closeSettings = document.getElementById('closeSettings');
const apiUrlInput = document.getElementById('apiUrl');
const speechRateInput = document.getElementById('speechRate');

// State
let stream = null;
let isListening = false;
let capturedImage = null;

// Speech Recognition Setup
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = SpeechRecognition ? new SpeechRecognition() : null;

if (recognition) {
    recognition.continuous = false;
    recognition.lang = 'en-US';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
}

// ============================================
// Camera Functions
// ============================================

async function startCamera() {
    try {
        stream = await navigator.mediaDevices.getUserMedia({
            video: {
                facingMode: 'environment',
                width: { ideal: 1280 },
                height: { ideal: 720 }
            }
        });
        camera.srcObject = stream;
        updateStatus('Camera ready. Tap button to capture and ask.', 'success');
        speak('Camera ready. Tap the button to capture a photo and ask your question.');
    } catch (error) {
        console.error('Camera error:', error);
        updateStatus('Camera access denied. Please enable camera.', 'error');
        speak('Camera access denied. Please enable camera permissions.');
    }
}

function capturePhoto() {
    const context = canvas.getContext('2d');
    canvas.width = camera.videoWidth;
    canvas.height = camera.videoHeight;
    context.drawImage(camera, 0, 0);

    // Convert to blob
    canvas.toBlob((blob) => {
        capturedImage = blob;
        vibrate(100);
        startListening();
    }, 'image/jpeg', 0.9);
}

// ============================================
// Voice Functions
// ============================================

function speak(text, onEnd = null) {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = CONFIG.speechRate;
    utterance.pitch = 1;
    utterance.volume = 1;

    if (onEnd) {
        utterance.onend = onEnd;
    }

    speechSynthesis.cancel(); // Cancel any ongoing speech
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
    btnText.textContent = 'Listening...';
    updateStatus('Listening for your question...', '');
    speak('What would you like to know?');

    vibrate(50);
    recognition.start();
}

function stopListening() {
    if (recognition && isListening) {
        recognition.stop();
        isListening = false;
        mainBtn.classList.remove('listening');
        btnText.textContent = 'Tap to Start';
    }
}

// ============================================
// API Functions
// ============================================

async function sendToAPI(imageBlob, question) {
    mainBtn.classList.add('processing');
    btnText.textContent = 'Processing...';
    updateStatus('Analyzing image...', '');
    speak('Analyzing...');

    try {
        // Demo mode for testing without backend
        if (CONFIG.apiUrl === 'DEMO_MODE') {
            // Simulate API delay
            await new Promise(resolve => setTimeout(resolve, 1500));

            // Generate demo response based on question
            let answer = 'This is a demo response. ';
            if (question.toLowerCase().includes('color')) {
                answer += 'I can see various colors in the image.';
            } else if (question.toLowerCase().includes('what')) {
                answer += 'I can see an object in the image.';
            } else {
                answer += 'To get real answers, please deploy the backend API.';
            }

            updateStatus(`Answer: ${answer}`, 'success');
            speak(answer);
            vibrate([100, 50, 100]);
            mainBtn.classList.remove('processing');
            btnText.textContent = 'Tap to Start';
            return;
        }

        // Real API call
        const formData = new FormData();
        formData.append('image', imageBlob, 'photo.jpg');
        formData.append('question', question);

        const response = await fetch(`${CONFIG.apiUrl}/api/vqa`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        const data = await response.json();

        if (data.success) {
            updateStatus(`Answer: ${data.answer}`, 'success');
            speak(data.answer);
            vibrate([100, 50, 100]);
        } else {
            throw new Error('No answer received');
        }

    } catch (error) {
        console.error('API error:', error);
        updateStatus('Error: Could not get answer. Check connection.', 'error');
        speak('Sorry, I could not process your request. Please try again.');
        vibrate([200, 100, 200]);
    } finally {
        mainBtn.classList.remove('processing');
        btnText.textContent = 'Tap to Start';
    }
}

// ============================================
// Speech Recognition Handlers
// ============================================

if (recognition) {
    recognition.onresult = (event) => {
        const question = event.results[0][0].transcript;
        console.log('Question:', question);

        stopListening();
        updateStatus(`You asked: "${question}"`, '');

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
            updateStatus('No speech detected. Please try again.', 'error');
            speak('I did not hear anything. Please try again.');
        } else {
            updateStatus('Speech recognition error', 'error');
            speak('Sorry, there was an error. Please try again.');
        }
    };

    recognition.onend = () => {
        if (isListening) {
            stopListening();
        }
    };
}

// ============================================
// UI Helper Functions
// ============================================

function updateStatus(message, type = '') {
    statusDiv.textContent = message;
    statusDiv.className = `status-message ${type}`;
}

function vibrate(pattern) {
    if ('vibrate' in navigator) {
        navigator.vibrate(pattern);
    }
}

// ============================================
// Event Listeners
// ============================================

mainBtn.addEventListener('click', () => {
    if (!isListening) {
        capturePhoto();
    }
});

settingsBtn.addEventListener('click', () => {
    settingsModal.hidden = false;
    speak('Settings opened');
});

closeSettings.addEventListener('click', () => {
    CONFIG.apiUrl = apiUrlInput.value;
    CONFIG.speechRate = parseFloat(speechRateInput.value);
    settingsModal.hidden = true;
    speak('Settings saved');
});

// ============================================
// Service Worker Registration
// ============================================

if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('sw.js')
        .then(reg => console.log('Service Worker registered:', reg))
        .catch(err => console.error('Service Worker registration failed:', err));
}

// ============================================
// Voice Commands
// ============================================

let isVoiceCommandMode = false;
let voiceCommandRecognition = null;

// Setup continuous voice command recognition
if (SpeechRecognition) {
    voiceCommandRecognition = new SpeechRecognition();
    voiceCommandRecognition.continuous = true;
    voiceCommandRecognition.interimResults = false;
    voiceCommandRecognition.lang = 'en-US';

    voiceCommandRecognition.onresult = (event) => {
        const lastResult = event.results[event.results.length - 1];
        const command = lastResult[0].transcript.toLowerCase().trim();

        console.log('Voice command:', command);

        // Check for "take photo" or "capture" command
        if (command.includes('take photo') || command.includes('capture') || command.includes('take picture')) {
            speak('Taking photo now');
            vibrate(100);
            capturePhoto();
        }
        // Check for "help" command
        else if (command.includes('help')) {
            speak('Say take photo to capture an image. After capturing, I will ask you a question. You can also tap the large button to capture.');
        }
        // Check for "settings" command
        else if (command.includes('settings') || command.includes('setting')) {
            settingsModal.hidden = false;
            speak('Settings opened');
        }
    };

    voiceCommandRecognition.onerror = (event) => {
        if (event.error !== 'no-speech') {
            console.error('Voice command error:', event.error);
        }
    };
}

function startVoiceCommands() {
    if (voiceCommandRecognition && !isVoiceCommandMode) {
        try {
            voiceCommandRecognition.start();
            isVoiceCommandMode = true;
            console.log('Voice commands enabled');
        } catch (e) {
            console.log('Voice commands already running');
        }
    }
}

function stopVoiceCommands() {
    if (voiceCommandRecognition && isVoiceCommandMode) {
        voiceCommandRecognition.stop();
        isVoiceCommandMode = false;
        console.log('Voice commands disabled');
    }
}

// ============================================
// Initialize App
// ============================================

window.addEventListener('load', () => {
    startCamera();

    // Load saved settings
    const savedApiUrl = localStorage.getItem('apiUrl');
    const savedSpeechRate = localStorage.getItem('speechRate');

    if (savedApiUrl) {
        // Migration: If saved URL is localhost, switch to production
        if (savedApiUrl.includes('localhost') || savedApiUrl.includes('127.0.0.1')) {
            localStorage.removeItem('apiUrl');
            CONFIG.apiUrl = 'https://sakthi04-vqa-app.hf.space';
            apiUrlInput.value = CONFIG.apiUrl;
        } else {
            CONFIG.apiUrl = savedApiUrl;
            apiUrlInput.value = savedApiUrl;
        }
    }

    if (savedSpeechRate) {
        CONFIG.speechRate = parseFloat(savedSpeechRate);
        speechRateInput.value = savedSpeechRate;
    }

    // Welcome message with instructions
    setTimeout(() => {
        speak('Welcome to VQA Assistant. This app is designed for voice-first operation. You can tap the large button to capture a photo, or say "take photo" at any time. After capturing, I will ask you a question about the image.', () => {
            // Start voice commands after welcome message
            setTimeout(() => {
                startVoiceCommands();
                speak('Voice commands are now active. Say "take photo" to begin, or tap the button.');
            }, 1000);
        });
    }, 1500);
});

// Save settings on change
apiUrlInput.addEventListener('change', () => {
    localStorage.setItem('apiUrl', apiUrlInput.value);
});

speechRateInput.addEventListener('change', () => {
    localStorage.setItem('speechRate', speechRateInput.value);
});
