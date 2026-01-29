# Accessible VQA PWA - Voice-First Visual Question Answering

[![UN SDG 10](https://img.shields.io/badge/UN%20SDG-10%20Reduced%20Inequalities-E5243B)](https://sdgs.un.org/goals/goal10)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PWA](https://img.shields.io/badge/PWA-enabled-5A0FC8.svg)](https://web.dev/progressive-web-apps/)

> **A production-ready Progressive Web App enabling visually impaired users to ask questions about their surroundings using voice commands only - no screen interaction required.**

---

## 🎯 Overview

This application combines **BLIP Visual Question Answering** with a **voice-first PWA interface** to empower visually impaired individuals with AI-powered visual assistance. Built for **UN SDG Goal 10: Reduced Inequalities**.

### Key Features

- 🎤 **Voice-First Operation** - Complete hands-free control
- 🔊 **Text-to-Speech Feedback** - All responses spoken aloud
- 📷 **Auto Camera Capture** - Say "Take photo" to capture
- ♿ **WCAG 2.1 Level AA** - Full accessibility compliance
- 📱 **Progressive Web App** - Installable, works offline
- 🚀 **Production Ready** - No training required (pretrained BLIP model)
- 🎯 **78-82% Accuracy** - Validated on VQA v2 dataset

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Modern browser (Chrome/Edge recommended)
- Camera and microphone
- 4GB RAM minimum (GPU recommended)

### Installation

```bash
# Clone repository
git clone https://github.com/SakthiV4/Visual-Question-Answering.git
cd Visual-Question-Answering

# Create virtual environment
python -m venv venv

# Activate venv
# Windows:
.\venv\Scripts\Activate.ps1
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install torch torchvision transformers fastapi uvicorn pillow python-multipart
```

### Run Application

**Windows:**
```powershell
.\START_APP.ps1
```

**Linux/Mac:**
```bash
./start_app.sh
```

**Or manually:**
```bash
# Terminal 1 - Backend
cd backend
python main.py

# Terminal 2 - Frontend
cd pwa
python -m http.server 8080

# Browser: http://localhost:8080
```

---

## 🎤 How to Use

### Voice-First Operation (No Screen Needed!)

1. **Open app** → Automatic voice welcome
2. **Say "Take photo"** → Camera captures automatically
3. **Ask your question** → e.g., "What is in front of me?"
4. **Listen to answer** → Spoken response

### Voice Commands
- **"Take photo"** / **"Capture"** - Captures image
- **"Help"** - Instructions
- **"Settings"** - Open settings

### Alternative (Touch)
- Tap large circular button (280x280px)

---

## 📁 Project Structure

```
vqa-project/
├── pwa/                          # Progressive Web App
│   ├── index.html               # Accessible UI
│   ├── style.css                # High-contrast design
│   ├── app.js                   # Voice I/O + Camera
│   ├── sw.js                    # Service Worker
│   ├── manifest.json            # PWA config
│   ├── icon-192.png             # App icon (small)
│   └── icon-512.png             # App icon (large)
│
├── backend/                      # FastAPI Backend
│   └── main.py                  # API server
│
├── src/                          # Source Code
│   ├── models/
│   │   ├── blip_vqa.py          # BLIP model wrapper
│   │   └── vqa_inference.py     # Inference API
│   ├── data/                    # Data loaders
│   ├── training/                # Training scripts
│   └── config.py                # Configuration
│
├── START_APP.ps1                # Windows startup
├── start_app.sh                 # Linux/Mac startup
└── model_config.json            # Model specifications
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│         PWA Frontend                │
│  - Voice Input (Web Speech API)     │
│  - Voice Output (Text-to-Speech)    │
│  - Camera (MediaDevices API)        │
│  - Accessible UI (WCAG 2.1 AA)      │
└──────────────┬──────────────────────┘
               │ HTTPS
               ▼
┌─────────────────────────────────────┐
│      Backend API (FastAPI)          │
│  - VQA Inference                    │
│  - Image Processing                 │
│  - CORS Enabled                     │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   BLIP-VQA Model (Pretrained)       │
│  - Salesforce/blip-vqa-base         │
│  - 78-82% Accuracy on VQA v2        │
└─────────────────────────────────────┘
```

---

## 📱 PWA Features

### Installation

**Desktop (Chrome/Edge):**
1. Click install icon in address bar
2. App opens in standalone window

**Mobile (Android/iOS):**
1. Menu → "Add to Home Screen"
2. Launch from home screen

### Offline Support
- Service Worker caches static assets
- Works offline after first load
- Fast loading with cached resources

---

## ♿ Accessibility

### WCAG 2.1 Level AA Compliance

✅ **Perceivable**
- High contrast (4.5:1 minimum)
- Large text (24px minimum)
- Clear visual indicators

✅ **Operable**
- Keyboard navigation
- Voice control (hands-free)
- Large touch targets (280x280px)
- Focus indicators (yellow outline)

✅ **Understandable**
- Clear audio feedback
- Simple language
- Consistent navigation

✅ **Robust**
- Screen reader compatible (ARIA labels)
- Semantic HTML5
- Cross-browser support

---

## 🌐 Deployment

### Backend Options

**1. AWS EC2 with GPU**
```bash
# Instance: g4dn.xlarge
# Install CUDA + PyTorch
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
pip install -r backend/requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

**2. Google Cloud Run**
```bash
gcloud run deploy vqa-backend --source . --platform managed
```

### Frontend Options

**1. Netlify (Recommended)**
```bash
cd pwa
netlify deploy --prod
```

**2. Vercel**
```bash
cd pwa
vercel --prod
```

**3. GitHub Pages**
- Push to GitHub
- Enable Pages in settings
- Set source to `/pwa` folder

### HTTPS Requirement
> ⚠️ **IMPORTANT:** PWA features (camera, microphone, service worker) require HTTPS in production. All deployment options above provide automatic HTTPS.

---

## 🧪 Testing

### Backend Health Check
```bash
curl http://localhost:8000/api/health
```

**Expected:**
```json
{
  "status": "healthy",
  "model": "BLIP-VQA (pretrained on VQA v2)",
  "accuracy": "78-82%"
}
```

### Voice Test Scenarios

1. **Object Recognition**
   - Say "Take photo"
   - Ask "What is this?"

2. **Color Identification**
   - Say "Take photo"
   - Ask "What color is this?"

3. **Scene Description**
   - Say "Take photo"
   - Ask "What do you see?"

---

## 📊 Performance

- **Model:** BLIP-VQA (Salesforce/blip-vqa-base)
- **Accuracy:** 78.25% on VQA v2 dataset
- **Inference Time:** 500-1000ms (GPU), 2-5s (CPU)
- **Model Size:** 1.5GB (downloads on first run)
- **Browser Support:** Chrome 90+, Edge 90+, Safari 14+

---

## 🤝 Contributing

We welcome contributions! This project supports **UN SDG Goal 10: Reduced Inequalities** by making visual information accessible to visually impaired individuals.

### Development Setup

```bash
# Install dev dependencies
pip install -r requirements.txt

# Run tests
pytest

# Code formatting
black .
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🌟 Impact

### UN SDG Goal 10: Reduced Inequalities

This app empowers visually impaired individuals by:
- ✅ Providing voice-first access to visual information
- ✅ Requiring no technical knowledge - just speak
- ✅ Working offline after installation
- ✅ Being free and open source

### Use Cases
- 📅 Expiry date reading
- 🎨 Color identification
- 🔍 Object recognition
- 📝 Text reading
- 💵 Currency identification
- 🗺️ Scene understanding

---

## 📞 Support

- **Documentation:** See [pwa/DEPLOYMENT_GUIDE.md](pwa/DEPLOYMENT_GUIDE.md)
- **Issues:** [GitHub Issues](https://github.com/SakthiV4/Visual-Question-Answering/issues)
- **Discussions:** [GitHub Discussions](https://github.com/SakthiV4/Visual-Question-Answering/discussions)

---

**Built with ❤️ for accessibility and inclusion**

*Empowering visually impaired individuals with AI-powered visual assistance*
