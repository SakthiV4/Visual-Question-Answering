# Python 3.11.14 Installation Steps

## Step-by-Step Installation Guide

### Step 1: Find the Installer
Go to your **Downloads** folder and find `Python-3.11.14` (the folder you showed in the screenshot)

### Step 2: Run the Installer
**Double-click** on the `Python-3.11.14` folder, then double-click the installer file inside (it will be named something like `python-3.11.14-amd64.exe`)

### Step 3: CRITICAL - First Screen of Installer
When the installer opens, you'll see a screen that looks like this:

![Python Installer](file:///C:/Users/sakth/.gemini/antigravity/brain/29193744-f245-4445-b403-22d9efc28b86/python_installer_guide.png)

**IMPORTANT:** 
- ✅ **CHECK the box** at the bottom that says **"Add Python 3.11 to PATH"**
- This is THE MOST IMPORTANT step!
- Then click the big **"Install Now"** button

### Step 4: Wait for Installation
The installer will run for 1-2 minutes. Wait for it to complete.

### Step 5: Close the Installer
When it says "Setup was successful", click "Close"

### Step 6: Verify Installation
1. **Close ALL PowerShell windows** (very important!)
2. Open a **NEW PowerShell window**
3. Type: `py -3.11 --version`
4. You should see: `Python 3.11.14`

### Step 7: Run GPU Setup
Once verified, navigate to your project and run the setup:
```powershell
cd c:\PROJECT\vqa-project
powershell -ExecutionPolicy Bypass -File setup_gpu.ps1
```

---

## Quick Summary
1. Double-click installer in Downloads
2. ✅ CHECK "Add Python 3.11 to PATH"
3. Click "Install Now"
4. Wait for completion
5. Close all PowerShell windows
6. Open new PowerShell and run setup script

**The "Add to PATH" checkbox is crucial - don't skip it!**
