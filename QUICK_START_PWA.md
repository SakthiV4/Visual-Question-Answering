# Quick Start - VQA Accessibility App

## Step 1: Install All Dependencies

Run this command to install all required packages:

```bash
pip install torch torchvision transformers fastapi uvicorn pillow python-multipart
```

**Note:** This will download ~2GB of packages (PyTorch + Transformers). It may take 5-10 minutes.

## Step 2: Start Backend Server

Open a terminal and run:

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

**Note:** First run will download the BLIP model (~1.5GB). This is one-time only.

## Step 3: Start Frontend Server

Open a **NEW** terminal and run:

```bash
cd c:\PROJECT\vqa-project\pwa
python -m http.server 8080
```

**Expected output:**
```
Serving HTTP on :: port 8080 (http://[::]:8080/) ...
```

## Step 4: Open in Browser

1. Open Chrome or Edge
2. Go to: **http://localhost:8080**
3. **Allow camera and microphone permissions** (CRITICAL!)
4. Wait for voice: "Welcome to VQA Assistant..."

## Step 5: Use the App

### Voice-First Operation:
- Say **"Take photo"** → Captures image
- Ask your question → Get spoken answer
- Say **"Help"** → Instructions

### Or use touch:
- Tap large circular button → Captures and asks

---

## Troubleshooting

### If backend fails to start:

**Missing dependencies?**
```bash
pip install torch torchvision transformers fastapi uvicorn pillow python-multipart
```

**Out of memory?**
- Close other applications
- The model needs ~2GB RAM minimum

### If frontend doesn't work:

**Port already in use?**
```bash
# Use a different port
python -m http.server 8081
# Then open http://localhost:8081
```

### If voice doesn't work:

1. Check browser permissions (camera + microphone)
2. Ensure no other app is using microphone
3. Try Chrome or Edge (best support)

---

## Quick Commands Reference

```bash
# Install everything
pip install torch torchvision transformers fastapi uvicorn pillow python-multipart

# Terminal 1 - Backend
cd c:\PROJECT\vqa-project\backend
python main.py

# Terminal 2 - Frontend  
cd c:\PROJECT\vqa-project\pwa
python -m http.server 8080

# Browser
http://localhost:8080
```

---

**That's it! The app should now be running with full voice control!** 🎉
