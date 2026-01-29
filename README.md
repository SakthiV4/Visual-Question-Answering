# VQA Accessibility App - Quick Start

## 🎤 Voice-First PWA for Visually Impaired Users

A Progressive Web App that enables visually impaired users to ask questions about their surroundings using **voice commands only** - no screen interaction required!

---

## ⚡ Quick Start (2 Steps)

### Step 1: Start Backend
```bash
cd c:\PROJECT\vqa-project\backend
python main.py
```

### Step 2: Start Frontend
Open a new terminal:
```bash
cd c:\PROJECT\vqa-project\pwa
python -m http.server 8080
```

### Step 3: Open Browser
Navigate to: **http://localhost:8080**

✅ Allow camera and microphone permissions  
✅ Listen for voice instructions  
✅ Say **"Take photo"** to begin!

---

## 🎯 How to Use (Voice-Only)

### For Visually Impaired Users:

1. **Open the app** → Automatic voice welcome
2. **Say "Take photo"** → Camera captures image
3. **Ask your question** → e.g., "What is this?"
4. **Listen to answer** → Spoken response

### Voice Commands:
- **"Take photo"** - Captures image
- **"Help"** - Instructions
- **"Settings"** - Open settings

### Alternative:
- Tap large circular button in center

---

## ✅ What's Included

### Frontend (PWA)
- ✅ Voice input (Web Speech API)
- ✅ Voice output (Text-to-Speech)
- ✅ Camera access
- ✅ Offline support (Service Worker)
- ✅ Installable (Add to Home Screen)
- ✅ WCAG 2.1 Level AA compliant

### Backend (FastAPI)
- ✅ VQA inference API
- ✅ BLIP model (78-82% accuracy)
- ✅ CORS enabled
- ✅ Production-ready

### Files:
```
pwa/
├── index.html          # Accessible UI
├── style.css           # High-contrast design
├── app.js              # Voice I/O + Camera
├── sw.js               # Service Worker
├── manifest.json       # PWA config
├── icon-192.png        # App icon (small)
├── icon-512.png        # App icon (large)
└── DEPLOYMENT_GUIDE.md # Full deployment guide
```

---

## 📱 Install as App

### Desktop (Chrome/Edge):
1. Click install icon (⊕) in address bar
2. Click "Install"

### Mobile (Android):
1. Menu (⋮) → "Add to Home screen"
2. Tap "Add"

---

## 🔧 Troubleshooting

**Camera not working?**
- Allow camera permissions in browser

**Voice not working?**
- Allow microphone permissions
- Ensure no other app is using mic

**API error?**
- Check backend is running: http://localhost:8000/api/health

---

## 📚 Full Documentation

See **DEPLOYMENT_GUIDE.md** for:
- Production deployment
- Testing checklist
- Accessibility compliance
- Performance optimization

---

**Built for UN SDG Goal 10: Reduced Inequalities**  
**Empowering visually impaired individuals with AI** 🌟
