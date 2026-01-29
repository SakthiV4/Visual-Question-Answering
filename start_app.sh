#!/bin/bash
# VQA Accessibility App - Startup Script (Linux/Mac)
# This script starts both backend and frontend servers

echo "============================================"
echo "VQA Accessibility App - Starting..."
echo "============================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed"
    echo "Please install Python 3.8+ from https://www.python.org/"
    exit 1
fi

echo "[1/3] Starting Backend Server..."
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Start backend in background
cd "$SCRIPT_DIR/backend"
python3 main.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 5

echo "[2/3] Starting Frontend Server..."
echo ""

# Start frontend in background
cd "$SCRIPT_DIR/pwa"
python3 -m http.server 8080 &
FRONTEND_PID=$!

# Wait for frontend to start
sleep 3

echo "[3/3] Opening Browser..."
echo ""

# Open browser (platform-specific)
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open http://localhost:8080
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    xdg-open http://localhost:8080 2>/dev/null || echo "Please open http://localhost:8080 in your browser"
fi

echo "============================================"
echo "VQA App Started Successfully!"
echo "============================================"
echo ""
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:8080"
echo ""
echo "IMPORTANT: Allow camera and microphone permissions!"
echo ""
echo "Press Ctrl+C to stop servers..."

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo ''; echo 'Servers stopped.'; exit 0" INT

# Keep script running
wait
