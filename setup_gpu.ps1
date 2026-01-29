# VQA Project - Python 3.11 Setup with GPU Support
# This script recreates the virtual environment with Python 3.11 and CUDA-enabled PyTorch

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "VQA Project - Python 3.11 GPU Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check if Python 3.11 is available
Write-Host "[1/6] Checking for Python 3.11..." -ForegroundColor Yellow
$python311 = $null

# Try common Python 3.11 locations
$pythonPaths = @(
    "py -3.11",
    "python3.11",
    "C:\Python311\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe"
)

foreach ($pyPath in $pythonPaths) {
    try {
        $version = & $pyPath --version 2>&1
        if ($version -match "Python 3\.11") {
            $python311 = $pyPath
            Write-Host "  Found: $version" -ForegroundColor Green
            break
        }
    } catch {
        continue
    }
}

if (-not $python311) {
    Write-Host "  Python 3.11 not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Python 3.11 from:" -ForegroundColor Yellow
    Write-Host "  https://www.python.org/downloads/" -ForegroundColor White
    Write-Host ""
    Write-Host "After installation, run this script again." -ForegroundColor Yellow
    exit 1
}

# Step 2: Backup current environment info
Write-Host "`n[2/6] Backing up current environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "  Removing old virtual environment..." -ForegroundColor White
    Remove-Item -Recurse -Force venv
}

# Step 3: Create new virtual environment with Python 3.11
Write-Host "`n[3/6] Creating virtual environment with Python 3.11..." -ForegroundColor Yellow
& $python311 -m venv venv
Write-Host "  Virtual environment created!" -ForegroundColor Green

# Step 4: Upgrade pip
Write-Host "`n[4/6] Upgrading pip..." -ForegroundColor Yellow
& .\venv\Scripts\python.exe -m pip install --upgrade pip

# Step 5: Install PyTorch with CUDA support
Write-Host "`n[5/6] Installing PyTorch with CUDA support..." -ForegroundColor Yellow
Write-Host "  This may take a few minutes (downloading ~2-3GB)..." -ForegroundColor White
& .\venv\Scripts\pip.exe install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Step 6: Install other dependencies
Write-Host "`n[6/6] Installing other dependencies..." -ForegroundColor Yellow
& .\venv\Scripts\pip.exe install -r requirements.txt

# Verify GPU support
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Verifying GPU Support" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
& .\venv\Scripts\python.exe scripts\check_gpu.py

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Your environment is now ready with:" -ForegroundColor White
Write-Host "  - Python 3.11" -ForegroundColor Green
Write-Host "  - PyTorch with CUDA support" -ForegroundColor Green
Write-Host "  - GPU acceleration enabled" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Run training: .\venv\Scripts\python.exe scripts\train_model.py" -ForegroundColor White
Write-Host "  2. Training will now use your RTX 4060 GPU!" -ForegroundColor White
Write-Host ""
