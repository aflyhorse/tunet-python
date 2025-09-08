#!/bin/bash

# Tsinghua University Network Auto Login - Setup Script
echo "Setting up Tsinghua University Network Auto Login..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is not installed. Please install pip3 first."
    exit 1
fi

# Install Python dependencies
echo "Installing Python dependencies..."
if pip3 install --user -r requirements.txt; then
    echo "Dependencies installed successfully."
else
    echo "Detected externally managed environment. Retrying with --break-system-packages..."
    pip3 install --user --break-system-packages -r requirements.txt
fi

# Check if Chrome is installed
if command -v google-chrome &> /dev/null || command -v chromium-browser &> /dev/null; then
    echo "Chrome/Chromium browser found."
else
    echo "Warning: Chrome/Chromium browser not found."
    echo "Please install Chrome or Chromium:"
    echo "  Ubuntu/Debian: sudo apt-get install chromium-browser"
    echo "  CentOS/RHEL: sudo yum install chromium"
    echo "  Arch: sudo pacman -S chromium"
fi

# Make the script executable
chmod +x tunet_login.py

echo ""
echo "Setup complete!"
echo ""
echo "Usage examples:"
echo "1. Set environment variables (recommended):"
echo "   export TUNET_USERNAME='your_username'"
echo "   export TUNET_PASSWORD='your_password'"
echo "   python3 tunet_login.py"
echo ""
echo "2. Use command line arguments:"
echo "   python3 tunet_login.py -u your_username -p your_password"
echo ""
echo "3. Run with visible browser (for debugging):"
echo "   python3 tunet_login.py --no-headless"
echo ""
