# VQA Accessibility App - Production Deployment Guide

## 🚀 Quick Start (Local Testing)

### Prerequisites
- Python 3.8+
- Modern browser (Chrome, Edge, or Safari)
- Camera and microphone
- GPU recommended (but works on CPU)

### Step 1: Start Backend Server

```bash
cd c:\PROJECT\vqa-project\backend
python main.py
```

**Expected output:**
```
Loading VQA model...
Loading processor: Salesforce/blip-vqa-base
Loading pretrained model: Salesforce/blip-vqa-base
Model loaded successfully!
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 2: Serve PWA Frontend

Open a new terminal:

```bash
cd c:\PROJECT\vqa-project\pwa
python -m http.server 8080
```

**Expected output:**
```
Serving HTTP on :: port 8080 (http://[::]:8080/) ...
```

### Step 3: Open in Browser

1. Open Chrome or Edge
2. Navigate to: `http://localhost:8080`
3. **Allow camera and microphone permissions** (critical!)
4. Wait for voice announcement: "Welcome to VQA Assistant..."

---

## 🎤 Voice-First Operation

### For Visually Impaired Users

**The app is designed to work entirely through voice commands - no screen interaction required!**

#### How to Use:

1. **Start the app** - Opens automatically with voice guidance
2. **Listen** - The app will announce: "Voice commands are now active"
3. **Say "Take photo"** - Captures image automatically
4. **Listen** - App asks: "What would you like to know?"
5. **Ask your question** - e.g., "What is in front of me?"
6. **Listen to answer** - App speaks the answer aloud

#### Voice Commands:
- **"Take photo"** or **"Capture"** - Takes a photo
- **"Help"** - Explains how to use the app
- **"Settings"** - Opens settings (for sighted assistants)

#### Alternative (Touch):
- Large circular button in center (280x280px minimum)
- Tap once to capture and ask

---

## ✅ Testing Checklist

### Backend Health Check
```bash
# Test API is running
curl http://localhost:8000/api/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "model": "BLIP-VQA (pretrained on VQA v2)",
  "accuracy": "78-82%"
}
```

### PWA Installation Test

**Desktop (Chrome/Edge):**
1. Open app in browser
2. Look for install icon (⊕) in address bar
3. Click "Install VQA Assistant"
4. App opens in standalone window

**Mobile (Android):**
1. Open in Chrome
2. Tap menu (⋮) → "Add to Home screen"
3. Tap "Add"
4. Launch from home screen

### Voice Test Scenarios

**Test 1: Basic Object Recognition**
- Say: "Take photo"
- Point camera at an object
- Ask: "What is this?"
- Verify: Receives spoken answer

**Test 2: Color Identification**
- Say: "Take photo"
- Point at colored object
- Ask: "What color is this?"
- Verify: Receives color name

**Test 3: Scene Description**
- Say: "Take photo"
- Point at a scene
- Ask: "What do you see?"
- Verify: Receives scene description

### Accessibility Test

**Screen Reader Compatibility:**
- Enable NVDA (Windows) or VoiceOver (Mac)
- Navigate with Tab key
- Verify all elements are announced
- Verify status messages are read aloud

**Keyboard Navigation:**
- Tab through all controls
- Verify focus indicators (yellow outline)
- Press Enter/Space to activate buttons

**High Contrast Mode:**
- Enable Windows High Contrast
- Verify button borders visible
- Verify text readable

---

## 📱 PWA Features

### Installed App Benefits:
- ✅ **Offline Support** - Static assets cached
- ✅ **Standalone Mode** - No browser UI
- ✅ **Home Screen Icon** - Easy access
- ✅ **Fast Loading** - Cached resources
- ✅ **Native Feel** - Fullscreen experience

### Service Worker Status:
Check in browser DevTools → Application → Service Workers

---

## 🔧 Troubleshooting

### Camera Not Working
**Issue:** "Camera access denied"

**Solution:**
1. Check browser permissions
2. Chrome: Settings → Privacy → Camera → Allow
3. Must use HTTPS in production (localhost is exempt)

### Microphone Not Working
**Issue:** Voice commands not responding

**Solution:**
1. Check browser permissions
2. Chrome: Settings → Privacy → Microphone → Allow
3. Ensure no other app is using microphone

### API Connection Failed
**Issue:** "Could not get answer"

**Solution:**
1. Verify backend is running: `http://localhost:8000/api/health`
2. Check API URL in settings (tap gear icon)
3. Ensure CORS is enabled in backend

### Model Loading Slow
**Issue:** Backend takes long to start

**Solution:**
- First run downloads model (~1.5GB)
- Subsequent runs are faster
- Use GPU for better performance

### Voice Too Fast/Slow
**Issue:** Speech rate uncomfortable

**Solution:**
1. Say "Settings" or tap gear icon
2. Adjust "Speech Speed" slider
3. Range: 0.5 (slow) to 1.5 (fast)
4. Default: 0.9 (slightly slower for clarity)

---

## 🌐 Production Deployment

### Backend Deployment

**Option 1: AWS EC2 with GPU**
```bash
# Launch EC2 instance (g4dn.xlarge recommended)
# Install CUDA and PyTorch
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# Install dependencies
pip install fastapi uvicorn transformers pillow

# Run with Uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000
```

**Option 2: Google Cloud Run (CPU)**
```bash
# Build Docker image
docker build -t vqa-backend .

# Deploy to Cloud Run
gcloud run deploy vqa-backend --image vqa-backend --platform managed
```

### Frontend Deployment

**Option 1: Netlify (Recommended)**
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy PWA
cd pwa
netlify deploy --prod
```

**Option 2: Vercel**
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy PWA
cd pwa
vercel --prod
```

**Option 3: GitHub Pages**
```bash
# Push to GitHub
git add pwa/*
git commit -m "Deploy PWA"
git push origin main

# Enable GitHub Pages in repo settings
# Set source to /pwa folder
```

### HTTPS Requirement

**Critical:** PWA features (camera, microphone, service worker) require HTTPS in production.

- Netlify/Vercel: Automatic HTTPS
- Custom domain: Use Let's Encrypt
- GitHub Pages: Automatic HTTPS

### Update API URL

After deploying backend, update frontend:

1. Open `pwa/app.js`
2. Change line 7:
```javascript
apiUrl: 'https://your-backend-url.com'  // Replace with your backend URL
```

Or users can update in Settings after installation.

---

## 📊 Performance Metrics

### Expected Performance:
- **Model Accuracy:** 78-82% on VQA v2
- **Inference Time:** 500-1000ms (GPU), 2-5s (CPU)
- **Model Size:** 1.5GB download
- **PWA Size:** ~50KB (excluding icons)

### Optimization Tips:
- Use GPU for faster inference
- Enable FP16 precision (saves memory)
- Cache model after first load
- Compress images before sending

---

## 🎯 Accessibility Compliance

### WCAG 2.1 Level AA ✅
- ✅ **Perceivable:** High contrast (4.5:1), large text
- ✅ **Operable:** Keyboard navigation, voice control, large touch targets (280x280px)
- ✅ **Understandable:** Clear audio feedback, simple language
- ✅ **Robust:** Screen reader compatible, ARIA labels

### Voice-First Design ✅
- ✅ Auto-start with voice guidance
- ✅ Continuous voice command listening
- ✅ Hands-free operation
- ✅ Clear audio feedback for all actions
- ✅ No login/signup required

---

## 📞 Support

### For Users:
- Say "Help" for voice instructions
- All features work through voice
- No screen interaction required

### For Developers:
- Check browser console for errors
- Monitor Service Worker in DevTools
- Test API endpoints with curl/Postman

---

**Built with ❤️ for accessibility and inclusion**  
**Supporting UN SDG Goal 10: Reduced Inequalities**
