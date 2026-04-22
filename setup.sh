#!/bin/bash
# ServerOS Setup Script
# Designed for Raspberry Pi Zero 2 W (also works on any Linux/macOS)

set -e

echo "╔══════════════════════════════════════╗"
echo "║     🖥️  ServerOS Setup              ║"
echo "╚══════════════════════════════════════╝"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Installing..."
    sudo apt-get update && sudo apt-get install -y python3 python3-pip
else
    echo "✅ Python 3 found: $(python3 --version)"
fi

# Install pip dependencies
echo ""
echo "📦 Installing Python dependencies..."
pip3 install --upgrade pip
pip3 install flask psutil

# Create data directory
mkdir -p "$(dirname "$0")/data"

echo ""
echo "╔══════════════════════════════════════╗"
echo "║     ✅ Setup Complete!              ║"
echo "╠══════════════════════════════════════╣"
echo "║                                      ║"
echo "║  Start ServerOS:                     ║"
echo "║    cd ServerOS && python3 server.py  ║"
echo "║                                      ║"
echo "║  Open in browser:                    ║"
echo "║    http://localhost:5000             ║"
echo "║    http://<pi-ip>:5000              ║"
echo "║                                      ║"
echo "╚══════════════════════════════════════╝"
