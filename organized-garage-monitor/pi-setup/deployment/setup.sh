#!/bin/bash
# Legacy setup script for Raspberry Pi Garage Door Monitor
# NOTE: Use deploy.sh for new installations

echo "🚗 Legacy Setup Script for Raspberry Pi Garage Door Monitor"
echo "=========================================================="
echo "⚠️  WARNING: This is the legacy setup script."
echo "   For new installations, please use: ./deploy.sh"
echo ""

read -p "Do you want to continue with legacy setup? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Setup cancelled. Please use ./deploy.sh for new installations."
    exit 1
fi

echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

echo "🐍 Installing Python dependencies..."
sudo apt install -y python3-pip python3-venv

echo "🔧 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "📚 Installing Python packages..."
pip install -r requirements.txt

echo "📹 Installing camera support packages..."
sudo apt install -y v4l-utils

echo "🔐 Making scripts executable..."
chmod +x *.py
chmod +x *.sh

echo "✅ Legacy setup complete!"
echo ""
echo "⚠️  Note: This setup does not include:"
echo "   - Systemd service configuration"
echo "   - Auto-start on boot"
echo "   - Service management"
echo ""
echo "For full deployment with service management, please use:"
echo "   ./deploy.sh"
echo ""
echo "To activate the virtual environment:"
echo "   source venv/bin/activate"
