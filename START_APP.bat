@echo off
REM VQA Accessibility App - Startup Script
REM This script starts both backend and frontend servers

echo ============================================
echo VQA Accessibility App - Starting...
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo [1/3] Starting Backend Server...
echo.

REM Start backend in new window
start "VQA Backend" cmd /k "cd /d %~dp0backend && python main.py"

REM Wait for backend to start
timeout /t 5 /nobreak >nul

echo [2/3] Starting Frontend Server...
echo.

REM Start frontend in new window
start "VQA Frontend" cmd /k "cd /d %~dp0pwa && python -m http.server 8080"

REM Wait for frontend to start
timeout /t 3 /nobreak >nul

echo [3/3] Opening Browser...
echo.

REM Open browser
start http://localhost:8080

echo ============================================
echo VQA App Started Successfully!
echo ============================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:8080
echo.
echo IMPORTANT: Allow camera and microphone permissions!
echo.
echo Press any key to stop servers...
pause >nul

REM Stop servers (close windows)
taskkill /FI "WindowTitle eq VQA Backend*" /T /F >nul 2>&1
taskkill /FI "WindowTitle eq VQA Frontend*" /T /F >nul 2>&1

echo.
echo Servers stopped.
pause
