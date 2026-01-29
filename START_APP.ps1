# VQA Accessibility App - PowerShell Startup Script
# Starts both backend and frontend servers

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "VQA Accessibility App - Starting..." -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check if venv exists
if (!(Test-Path "venv\Scripts\Activate.ps1")) {
    Write-Host "[ERROR] Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please create venv first: python -m venv venv" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "[1/3] Starting Backend Server..." -ForegroundColor Green
Write-Host ""

# Start backend in new PowerShell window
$backendScript = @"
Set-Location '$PSScriptRoot'
.\venv\Scripts\Activate.ps1
Write-Host 'Backend Server Starting...' -ForegroundColor Green
python backend\main.py
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendScript

# Wait for backend to start
Start-Sleep -Seconds 8

Write-Host "[2/3] Starting Frontend Server..." -ForegroundColor Green
Write-Host ""

# Start frontend in new PowerShell window
$frontendScript = @"
Set-Location '$PSScriptRoot\pwa'
Write-Host 'Frontend Server Starting...' -ForegroundColor Green
python -m http.server 8080
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendScript

# Wait for frontend to start
Start-Sleep -Seconds 3

Write-Host "[3/3] Opening Browser..." -ForegroundColor Green
Write-Host ""

# Open browser
Start-Process "http://localhost:8080"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "VQA App Started Successfully!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend:  http://localhost:8000" -ForegroundColor Yellow
Write-Host "Frontend: http://localhost:8080" -ForegroundColor Yellow
Write-Host ""
Write-Host "IMPORTANT: Allow camera and microphone permissions!" -ForegroundColor Red
Write-Host ""
Write-Host "Voice Commands:" -ForegroundColor Cyan
Write-Host "  - Say 'Take photo' to capture" -ForegroundColor White
Write-Host "  - Say 'Help' for instructions" -ForegroundColor White
Write-Host "  - Or tap the large purple button" -ForegroundColor White
Write-Host ""
Write-Host "Press any key to close this window (servers will keep running)..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
