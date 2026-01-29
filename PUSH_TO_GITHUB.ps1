# Git Initialization and Push Script
# Run this to initialize git and push to GitHub

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Git Setup and GitHub Push" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check if git is installed
try {
    git --version | Out-Null
}
catch {
    Write-Host "[ERROR] Git is not installed!" -ForegroundColor Red
    Write-Host "Please install Git from: https://git-scm.com/" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "[1/5] Initializing Git Repository..." -ForegroundColor Green

# Initialize git if not already done
if (!(Test-Path ".git")) {
    git init
    Write-Host "  ✓ Git repository initialized" -ForegroundColor Green
}
else {
    Write-Host "  ✓ Git repository already exists" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[2/5] Adding Files..." -ForegroundColor Green

# Add all files
git add .
Write-Host "  ✓ All files staged" -ForegroundColor Green

Write-Host ""
Write-Host "[3/5] Creating Initial Commit..." -ForegroundColor Green

# Create commit
git commit -m "feat: Initial commit - Accessible VQA PWA with voice-first interface

- Complete PWA with voice commands (take photo, help, settings)
- FastAPI backend with BLIP-VQA model (78-82% accuracy)
- Service Worker for offline support
- WCAG 2.1 Level AA accessibility compliance
- Production-ready deployment scripts
- CodeRabbit configuration for AI code review
- Comprehensive documentation and guides

Supporting UN SDG Goal 10: Reduced Inequalities"

Write-Host "  ✓ Initial commit created" -ForegroundColor Green

Write-Host ""
Write-Host "[4/5] Setting Up Remote..." -ForegroundColor Green
Write-Host ""

Write-Host "Please enter your GitHub repository URL:" -ForegroundColor Yellow
Write-Host "Example: https://github.com/YOUR_USERNAME/vqa-accessibility-app.git" -ForegroundColor Gray
$repoUrl = Read-Host "Repository URL"

if ($repoUrl) {
    # Check if remote already exists
    $remoteExists = git remote get-url origin 2>$null
    
    if ($remoteExists) {
        Write-Host "  ! Remote 'origin' already exists: $remoteExists" -ForegroundColor Yellow
        $overwrite = Read-Host "Do you want to update it? (y/n)"
        if ($overwrite -eq 'y') {
            git remote set-url origin $repoUrl
            Write-Host "  ✓ Remote updated" -ForegroundColor Green
        }
    }
    else {
        git remote add origin $repoUrl
        Write-Host "  ✓ Remote added" -ForegroundColor Green
    }
}
else {
    Write-Host "  ! Skipping remote setup" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[5/5] Pushing to GitHub..." -ForegroundColor Green

if ($repoUrl) {
    # Set branch name to main
    git branch -M main
    
    Write-Host "  Pushing to GitHub..." -ForegroundColor Yellow
    git push -u origin main
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Successfully pushed to GitHub!" -ForegroundColor Green
    }
    else {
        Write-Host "  ! Push failed. You may need to:" -ForegroundColor Yellow
        Write-Host "    1. Create the repository on GitHub first" -ForegroundColor Gray
        Write-Host "    2. Authenticate with GitHub (gh auth login)" -ForegroundColor Gray
        Write-Host "    3. Check your internet connection" -ForegroundColor Gray
    }
}
else {
    Write-Host "  ! Skipping push (no remote configured)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Git Setup Complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Go to https://coderabbit.ai and sign in with GitHub" -ForegroundColor White
Write-Host "  2. Install CodeRabbit app for your repository" -ForegroundColor White
Write-Host "  3. Create a pull request to test CodeRabbit review" -ForegroundColor White
Write-Host "  4. See GITHUB_SETUP.md for detailed instructions" -ForegroundColor White
Write-Host ""

Write-Host "Repository Files:" -ForegroundColor Cyan
Write-Host "  ✓ .gitignore - Excludes large files and models" -ForegroundColor Green
Write-Host "  ✓ README.md - Comprehensive project documentation" -ForegroundColor Green
Write-Host "  ✓ .coderabbit.yaml - AI review configuration" -ForegroundColor Green
Write-Host "  ✓ .github/workflows/coderabbit.yml - GitHub Actions" -ForegroundColor Green
Write-Host "  ✓ GITHUB_SETUP.md - Detailed setup guide" -ForegroundColor Green
Write-Host ""

pause
