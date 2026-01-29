# 🚀 Complete GitHub Setup - Step by Step

## Quick Start (3 Simple Steps)

### Step 1: Create GitHub Repository

**Go to:** [github.com/new](https://github.com/new)

Fill in:
- **Repository name:** `vqa-accessibility-app`
- **Description:** `Voice-first VQA PWA for visually impaired users - UN SDG Goal 10`
- **Visibility:** ✅ Public (recommended for CodeRabbit free tier)
- **Initialize:** ❌ **DO NOT** check any boxes (no README, no .gitignore, no license)

Click **"Create repository"**

---

### Step 2: Run the Push Script

```powershell
.\PUSH_TO_GITHUB.ps1
```

When prompted, enter your repository URL:
```
https://github.com/YOUR_USERNAME/vqa-accessibility-app.git
```

The script will:
- ✅ Initialize git
- ✅ Add all files
- ✅ Create initial commit
- ✅ Add remote
- ✅ Push to GitHub

---

### Step 3: Setup CodeRabbit

1. **Go to:** [coderabbit.ai](https://coderabbit.ai)
2. **Sign in with GitHub**
3. **Install CodeRabbit:**
   - Click "Install CodeRabbit"
   - Select `vqa-accessibility-app`
   - Click "Install"

**Done!** CodeRabbit will now review all your pull requests automatically.

---

## Alternative: Manual Setup

If you prefer to do it manually:

```bash
# 1. Initialize git
git init

# 2. Add files
git add .

# 3. Commit
git commit -m "feat: Initial commit - Accessible VQA PWA"

# 4. Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/vqa-accessibility-app.git

# 5. Push
git branch -M main
git push -u origin main
```

---

## What's Included

Your repository will have:

✅ **Complete PWA** - Voice-first interface  
✅ **Backend API** - FastAPI with BLIP-VQA  
✅ **Service Worker** - Offline support  
✅ **Accessibility** - WCAG 2.1 Level AA  
✅ **Documentation** - README, guides, deployment docs  
✅ **CodeRabbit Config** - AI code review ready  
✅ **GitHub Actions** - Automated workflows  

---

## Testing CodeRabbit

After setup, create a test PR:

```bash
# Create branch
git checkout -b test/coderabbit-review

# Make a small change (e.g., update README)
# ... edit README.md ...

# Commit and push
git add .
git commit -m "test: Testing CodeRabbit review"
git push origin test/coderabbit-review
```

Then:
1. Go to GitHub
2. Create Pull Request
3. Wait ~1 minute
4. CodeRabbit will comment with review!

---

## Troubleshooting

**"Permission denied"?**
- Run: `gh auth login` (install GitHub CLI first)
- Or use Personal Access Token

**"Repository not found"?**
- Make sure you created the repo on GitHub first
- Check the URL is correct

**"Already exists"?**
- The repo already has content
- Use `git push -f origin main` (⚠️ overwrites remote)

---

## Next Steps

After pushing:

1. ✅ **Enable GitHub Pages** (Settings → Pages → Source: `/pwa`)
2. ✅ **Add topics** (accessibility, pwa, voice-first, wcag)
3. ✅ **Star your repo** ⭐
4. ✅ **Share with community** 🌟

---

**Need help?** See `GITHUB_SETUP.md` for detailed instructions.
