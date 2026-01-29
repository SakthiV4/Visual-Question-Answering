# VQA Training Project Setup Script
# Run this script to set up your environment

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "VQA Training Project Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
Write-Host $pythonVersion -ForegroundColor Green

# Create virtual environment
Write-Host "`nCreating virtual environment..." -ForegroundColor Yellow
python -m venv venv

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "`nUpgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install requirements
Write-Host "`nInstalling dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Download VQA v2 dataset from https://visualqa.org/download.html" -ForegroundColor White
Write-Host "2. Extract dataset to data/raw/ directory" -ForegroundColor White
Write-Host "3. Open notebooks/03_model_training.ipynb in VSCode" -ForegroundColor White
Write-Host "4. Run all cells to start training" -ForegroundColor White
Write-Host ""
Write-Host "For quick testing, modify the notebook to use limited samples:" -ForegroundColor Yellow
Write-Host "  train_max_samples=1000, val_max_samples=500" -ForegroundColor White
Write-Host ""
Write-Host "Happy training! 🚀" -ForegroundColor Green
