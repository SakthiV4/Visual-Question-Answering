# Python 3.11.14 Installation - Step by Step Guide

## STEP 1: Download the Correct Installer

1. **Click this direct download link:**
   https://www.python.org/ftp/python/3.11.14/python-3.11.14-amd64.exe

2. **Save the file** to your Downloads folder
   - File name: `python-3.11.14-amd64.exe`
   - File size: Should be around 25-30 MB
   - File type: Application (.exe)

---

## STEP 2: Run the Installer

1. **Go to your Downloads folder**
   - Press `Windows Key + E` to open File Explorer
   - Click "Downloads" in the left sidebar

2. **Find the file:** `python-3.11.14-amd64.exe`
   - It should show as Type: "Application"
   - NOT the "Python-3.11.14" folder (that's source code, not the installer)

3. **Right-click** on `python-3.11.14-amd64.exe`

4. **Select "Run as administrator"**
   - Click "Yes" when Windows asks for permission

---

## STEP 3: Configure the Installer (CRITICAL!)

When the installer window opens, you'll see:

### ⚠️ BEFORE CLICKING ANYTHING:

**At the BOTTOM of the window**, you'll see TWO checkboxes:

1. ✅ **"Install launcher for all users (recommended)"** - Usually already checked
2. ⬜ **"Add Python 3.11 to PATH"** - **YOU MUST CHECK THIS BOX!**

### 📌 CRITICAL ACTION:
**CHECK the box that says "Add Python 3.11 to PATH"**

This is THE MOST IMPORTANT step! Without this, Python 3.11 won't work.

---

## STEP 4: Install

1. **After checking "Add Python 3.11 to PATH"**, click the big blue button that says:
   - **"Install Now"** (recommended)
   - OR "Customize installation" if you want to choose location

2. **Wait for installation** (1-2 minutes)
   - You'll see a progress bar
   - Don't close the window

3. **When it says "Setup was successful"**, click **"Close"**

---

## STEP 5: Verify Installation

1. **Close ALL PowerShell windows** (very important!)

2. **Open a NEW PowerShell window:**
   - Press `Windows Key`
   - Type "PowerShell"
   - Click "Windows PowerShell"

3. **Type this command:**
   ```powershell
   py -3.11 --version
   ```

4. **You should see:**
   ```
   Python 3.11.14
   ```

✅ **If you see this, SUCCESS! Python 3.11 is installed!**

❌ **If you see an error**, the installation didn't work - let me know and we'll troubleshoot.

---

## STEP 6: Run GPU Setup Script

Once Python 3.11 is verified:

1. **In the same PowerShell window**, navigate to your project:
   ```powershell
   cd c:\PROJECT\vqa-project
   ```

2. **Run the setup script:**
   ```powershell
   powershell -ExecutionPolicy Bypass -File setup_gpu.ps1
   ```

3. **Wait 15-20 minutes** while it:
   - Creates new virtual environment with Python 3.11
   - Downloads PyTorch with CUDA (~2-3 GB)
   - Installs all dependencies
   - Verifies GPU is working

---

## Troubleshooting

### If Python 3.11 is not found after installation:

**Most common issue:** You didn't check "Add Python 3.11 to PATH"

**Solution:** Uninstall and reinstall:
1. Go to Windows Settings → Apps → Installed apps
2. Find "Python 3.11.14" and click Uninstall
3. Start over from STEP 1, making sure to check the PATH checkbox

---

## Quick Checklist

Before running the installer, make sure:
- [ ] Downloaded the `.exe` file (not source code)
- [ ] Running as Administrator
- [ ] Will check "Add Python 3.11 to PATH" checkbox
- [ ] Will close all PowerShell windows after installation
- [ ] Will open NEW PowerShell to verify

---

**Ready? Let's do this! 🚀**

Start with STEP 1 and work your way through. Let me know when you complete STEP 5 (verification).
