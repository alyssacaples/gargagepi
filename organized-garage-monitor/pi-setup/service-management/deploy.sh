#!/bin/bash
# Deployment script for Raspberry Pi Garage Door Monitor
# This script should be run on the Raspberry Pi after cloning the repository

echo "🚗 Deploying Garage Door Monitor to Raspberry Pi..."
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found. Please run this script from the project root directory."
    exit 1
fi

# Update system packages
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
sudo apt install -y python3-pip python3-venv git

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install packages
echo "📚 Installing Python packages..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Install additional system packages for camera
echo "📹 Installing camera support packages..."
sudo apt install -y v4l-utils

# Create photos directory
echo "📁 Creating photos directory..."
mkdir -p photos

# Make scripts executable
echo "🔐 Making scripts executable..."
chmod +x *.py
chmod +x *.sh

# Create systemd service file
echo "⚙️ Setting up systemd service..."
sudo tee /etc/systemd/system/garage-monitor.service > /dev/null <<EOF
[Unit]
Description=Garage Door Monitor
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable service
sudo systemctl daemon-reload
sudo systemctl enable garage-monitor.service

# Get the Pi's IP address
PI_IP=$(hostname -I | awk '{print $1}')

echo "✅ Deployment complete!"
echo ""
echo "🌐 Your Raspberry Pi's IP address: $PI_IP"
echo ""
echo "📱 Access your garage monitor at:"
echo "   Main Interface: http://$PI_IP:5000"
echo "   Live Stream: http://$PI_IP:5000/stream"
echo "   Status API: http://$PI_IP:5000/status"
echo "   Capture Photo: http://$PI_IP:5000/capture"
echo ""
echo "Next steps:"
echo "1. Test the camera: source venv/bin/activate && python3 app.py"
echo "2. If everything works, start the service: sudo systemctl start garage-monitor"
echo "3. Check service status: sudo systemctl status garage-monitor"
echo "4. View logs: sudo journalctl -u garage-monitor -f"
echo ""
echo "The service will automatically start on boot."
echo ""
echo "💡 Save this IP address: $PI_IP"
echo ""
echo "🚀 Quick test - starting the service now..."
sudo systemctl start garage-monitor
sleep 3

# Check if service started successfully
if sudo systemctl is-active --quiet garage-monitor; then
    echo "✅ Service started successfully!"
    echo ""
    echo "🎉 Your garage monitor is now running!"
    echo "📱 Open your browser and go to: http://$PI_IP:5000"
    echo ""
    echo "To stop the service: sudo systemctl stop garage-monitor"
    echo "To restart the service: sudo systemctl restart garage-monitor"
else
    echo "❌ Service failed to start. Check logs with:"
    echo "   sudo journalctl -u garage-monitor -f"
fi
