# MOKA NEWS Logo Setup

## Current Status

✅ **Completed:**
- Created `assets/` directory for project assets
- Updated `README.md` to display logo from `assets/logo.png`  
- Created `download-logo.sh` script for easy logo download
- Added comprehensive documentation in `assets/README.md`
- Added user-friendly note in README about downloading the logo

❌ **Requires User Action:**
- Download and commit the actual logo file

## Why Manual Download is Needed

The automated environment has network restrictions that prevent downloading from Amazon S3 (where GitHub user-attachments are hosted). The DNS resolution for S3 domains is blocked for security reasons.

## How to Complete the Setup

### Option 1: Use the Download Script (Recommended)
```bash
cd /path/to/moka-news
./download-logo.sh
git add assets/logo.png
git commit -m "Add MOKA NEWS logo image"
git push
```

### Option 2: Manual Download
1. Open https://github.com/user-attachments/assets/b7ba51ff-ecc2-478e-a652-698b7c1b31ca in your browser
2. Right-click and save the image
3. Save it as `assets/logo.png` in the repository
4. Commit and push:
```bash
git add assets/logo.png
git commit -m "Add MOKA NEWS logo image"
git push
```

### Option 3: Use curl/wget Directly
```bash
curl -L -o assets/logo.png "https://github.com/user-attachments/assets/b7ba51ff-ecc2-478e-a652-698b7c1b31ca"
# Or
wget -O assets/logo.png "https://github.com/user-attachments/assets/b7ba51ff-ecc2-478e-a652-698b7c1b31ca"

# Then commit
git add assets/logo.png
git commit -m "Add MOKA NEWS logo image"
git push
```

## Verification

After downloading and committing the logo, verify it displays correctly:
1. View the README on GitHub
2. The logo should appear at the top, centered and properly sized
3. If viewing locally, use a markdown previewer that supports local image paths

## Technical Details

- **Logo Location**: `assets/logo.png`
- **Logo Source**: https://github.com/user-attachments/assets/b7ba51ff-ecc2-478e-a652-698b7c1b31ca
- **Display Width**: 400px
- **Image Format**: PNG
- **Repository**: calca/moka-news

## Issue Reference

This addresses the issue: "Salva l'immagine in git ed usala come logo nel readme"  
(Save the image in git and use it as a logo in the readme)
