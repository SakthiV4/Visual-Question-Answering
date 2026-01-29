// VQA PWA - JavaScript Application Logic

const API_URL = 'http://localhost:8000';

// DOM Elements
const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const placeholder = document.getElementById('placeholder');
const startCameraBtn = document.getElementById('startCamera');
const capturePhotoBtn = document.getElementById('capturePhoto');
const questionInput = document.getElementById('questionInput');
const voiceBtn = document.getElementById('voiceBtn');
const submitBtn = document.getElementById('submitBtn');
const loading = document.getElementById('loading');
const error = document.getElementById('error');
const answerSection = document.getElementById('answerSection');
const answerText = document.getElementById('answerText');
const processingTime = document.getElementById('processingTime');
const confidence = document.getElementById('confidence');

let stream = null;
let capturedImage = null;
let recognition = null;

// Initialize Speech Recognition
if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        questionInput.value = transcript;
        voiceBtn.classList.remove('listening');
        voiceBtn.textContent = '🎤 Ask with Voice';
    };

    recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        voiceBtn.classList.remove('listening');
        voiceBtn.textContent = '🎤 Ask with Voice';
        showError('Voice recognition failed. Please try again.');
    };

    recognition.onend = () => {
        voiceBtn.classList.remove('listening');
        voiceBtn.textContent = '🎤 Ask with Voice';
    };
}

// Start Camera
startCameraBtn.addEventListener('click', async () => {
    try {
        stream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: 'environment' }
        });
        video.srcObject = stream;
        video.style.display = 'block';
        placeholder.style.display = 'none';
        capturePhotoBtn.disabled = false;
        startCameraBtn.textContent = 'Camera Active';
        startCameraBtn.disabled = true;
    } catch (err) {
        showError('Camera access denied. Please allow camera permissions.');
        console.error('Camera error:', err);
    }
});

// Capture Photo
capturePhotoBtn.addEventListener('click', () => {
    const context = canvas.getContext('2d');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0);

    // Show canvas, hide video
    canvas.style.display = 'block';
    video.style.display = 'none';

    // Store captured image as base64
    capturedImage = canvas.toDataURL('image/jpeg', 0.8);

    // Update button
    capturePhotoBtn.textContent = 'Retake Photo';
    capturePhotoBtn.onclick = retakePhoto;
});

// Retake Photo
function retakePhoto() {
    canvas.style.display = 'none';
    video.style.display = 'block';
    capturedImage = null;
    capturePhotoBtn.textContent = 'Capture Photo';
    capturePhotoBtn.onclick = null;
    capturePhotoBtn.addEventListener('click', arguments.callee);
}

// Voice Input
voiceBtn.addEventListener('click', () => {
    if (!recognition) {
        showError('Voice recognition not supported in this browser.');
        return;
    }

    if (voiceBtn.classList.contains('listening')) {
        recognition.stop();
    } else {
        voiceBtn.classList.add('listening');
        voiceBtn.textContent = '🔴 Listening...';
        recognition.start();
    }
});

// Submit Question
submitBtn.addEventListener('click', async () => {
    const question = questionInput.value.trim();

    if (!question) {
        showError('Please enter a question.');
        return;
    }

    if (!capturedImage) {
        showError('Please capture a photo first.');
        return;
    }

    // Show loading
    loading.classList.add('show');
    answerSection.classList.remove('show');
    error.classList.remove('show');

    try {
        const response = await fetch(`${API_URL}/vqa/base64`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                image: capturedImage,
                question: question
            })
        });

        if (!response.ok) {
            throw new Error('Server error');
        }

        const data = await response.json();

        // Hide loading
        loading.classList.remove('show');

        // Show answer
        answerText.textContent = data.answer;
        processingTime.textContent = `⏱️ ${data.processing_time_ms}ms`;
        confidence.textContent = `✓ ${(data.confidence * 100).toFixed(0)}% confident`;
        answerSection.classList.add('show');

        // Speak answer
        speakAnswer(data.answer);

    } catch (err) {
        loading.classList.remove('show');
        showError('Failed to get answer. Make sure the backend server is running.');
        console.error('API error:', err);
    }
});

// Text-to-Speech
function speakAnswer(text) {
    if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 0.9;
        utterance.pitch = 1;
        utterance.volume = 1;
        speechSynthesis.speak(utterance);
    }
}

// Show Error
function showError(message) {
    error.textContent = message;
    error.classList.add('show');
    setTimeout(() => {
        error.classList.remove('show');
    }, 5000);
}

// Service Worker Registration (PWA)
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('sw.js')
        .then(reg => console.log('Service Worker registered'))
        .catch(err => console.error('Service Worker registration failed:', err));
}
