#!/bin/bash
# Script to download the MOKA NEWS logo
# This script downloads the logo image and saves it to the assets directory

set -e  # Exit on error

LOGO_URL="https://github.com/user-attachments/assets/b7ba51ff-ecc2-478e-a652-698b7c1b31ca"
LOGO_PATH="assets/logo.png"

# Ensure assets directory exists
mkdir -p assets

echo "Downloading MOKA NEWS logo..."
echo "From: $LOGO_URL"
echo "To: $LOGO_PATH"
echo ""

# Try curl first, then wget
if command -v curl &> /dev/null; then
    echo "Using curl..."
    curl -L -o "$LOGO_PATH" "$LOGO_URL"
elif command -v wget &> /dev/null; then
    echo "Using wget..."
    wget -O "$LOGO_PATH" "$LOGO_URL"
else
    echo "Error: Neither curl nor wget is available."
    echo "Please download the logo manually from:"
    echo "$LOGO_URL"
    echo "And save it as: $LOGO_PATH"
    exit 1
fi

# Verify the download
if [ -f "$LOGO_PATH" ] && [ -s "$LOGO_PATH" ]; then
    echo ""
    echo "✓ Logo downloaded successfully!"
    echo "  File: $LOGO_PATH"
    echo "  Size: $(du -h "$LOGO_PATH" | cut -f1)"
    echo ""
    echo "The logo is now ready to be committed to the repository."
else
    echo ""
    echo "✗ Download failed or file is empty."
    echo "Please download manually from: $LOGO_URL"
    exit 1
fi
