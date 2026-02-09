# Git Repository Best Practices

## ⚠️ CRITICAL: Avoid Binary Files in Git

**Never commit these to git**:
- PDFs (presentation decks, documentation PDFs)
- Large images (>500KB PNGs, JPGs)
- Videos, audio files
- Compiled binaries, executables
- Archives (ZIP, TAR, GZ)

**Why?**
1. **Bloats repository** - Binary files increase repo size permanently (even after deletion)
2. **Deployment issues** - Some platforms (Hugging Face, Heroku) reject binary files
3. **Slow clones** - Large repos take longer to clone
4. **No meaningful diffs** - Git can't show useful changes for binaries
5. **History pollution** - Removing them later requires rewriting history

---

## What to Do Instead

### For Documentation (PDFs, Presentations)
```bash
# Store in external services:
- Google Drive / Dropbox (for sharing)
- Confluence / Notion (for docs)
- Create regeneration scripts (see DECKS_REGENERATION.md)

# Add to .gitignore:
*.pdf
*_deck*/
presentations/
```

### For Images
```bash
# Small images (<100KB): OK in git
# Large images (>500KB): Use alternatives

# Alternatives:
- Cloud storage (Firebase, S3, Cloudinary)
- Image optimization (compress PNGs/JPGs)
- SVG instead of PNG when possible
```

### For Generated Assets
```bash
# Never commit generated files
# Add to .gitignore:
tmp/
.tmp/
output/
generated/
build/
dist/
```

---

## Current Repository Protection

### Active .gitignore Rules
```
.tmp/
tmp/
*.pyc
__pycache__/

# Binary documentation (added after cleanup)
investor_deck_v1/
technical_deck_v1/
IgniteAI_Investor_Deck.pdf
```

### Good: Already Excluded
- ✅ `tmp/` - Temporary files
- ✅ `.env` - Secrets
- ✅ `__pycache__/` - Python cache

### Watch Out For
- ⚠️ Any `*.pdf` files
- ⚠️ Large `*.png` files (>500KB)
- ⚠️ Video files in `brand/` or elsewhere

---

## If You Accidentally Commit Binary Files

### Immediate Fix (< 1 hour old)
```bash
git reset HEAD~1  # Undo last commit
git add .gitignore  # Update gitignore
git commit -m "Add gitignore rules"
```

### Recent Fix (< 5 commits)
```bash
git rebase -i HEAD~5
# Mark commit with binary for "edit"
git rm offending_file.pdf
git commit --amend --no-edit
git rebase --continue
git push origin main --force
```

### Deep Cleanup (old commits)
```bash
# Use BFG Repo-Cleaner
curl -L https://repo1.maven.org/maven2/com/madgag/bfg/1.14.0/bfg-1.14.0.jar -o bfg.jar
java -jar bfg.jar --delete-files "*.pdf" .
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push origin main --force
```

---

## Before Every Commit

**Check what you're committing**:
```bash
git status
git diff --cached --stat  # See file sizes

# Look for:
- Files > 100KB
- .pdf, .zip, .mp4, .mov extensions
- Anything in tmp/ or generated folders
```

**Pro tip**: Use `git-lfs` for unavoidable large files
```bash
git lfs install
git lfs track "*.psd"  # Track large files
```

---

## This Repo's History

We learned this lesson the hard way:
- **Issue**: Presentation decks (PDFs + PNGs) blocked Hugging Face deployment
- **Files**: 15 binary files, ~6.4 MB total
- **Solution**: BFG Repo-Cleaner to remove from all 130 commits
- **Time spent**: ~30 minutes debugging + cleanup

**Prevent this**: Always check before committing! 🚨
