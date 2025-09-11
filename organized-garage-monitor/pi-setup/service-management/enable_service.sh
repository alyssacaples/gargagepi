#!/bin/bash
# Enable Garage Monitor Service
# This script enables the garage monitor service to start automatically on boot

echo "🚗 Enabling Garage Monitor Service..."
echo "=================================="

# Check if service file exists
if [ ! -f "/etc/systemd/system/garage-monitor.service" ]; then
    echo "❌ Service file not found. Please run ./deploy.sh first to set up the service."
    exit 1
fi

# Reload systemd daemon
echo "🔄 Reloading systemd daemon..."
sudo systemctl daemon-reload

# Enable the service
echo "✅ Enabling garage-monitor service..."
sudo systemctl enable garage-monitor.service

# Start the service
echo "🚀 Starting garage-monitor service..."
sudo systemctl start garage-monitor.service

# Check status
echo ""
echo "📊 Service Status:"
sudo systemctl status garage-monitor.service --no-pager -l

echo ""
echo "✅ Garage Monitor Service is now ENABLED and RUNNING!"
echo ""
echo "💡 Useful commands:"
echo "   - Check status: sudo systemctl status garage-monitor"
echo "   - View logs: sudo journalctl -u garage-monitor -f"
echo "   - Stop service: sudo systemctl stop garage-monitor"
echo "   - Restart service: sudo systemctl restart garage-monitor"
echo "   - Disable service: ./disable_service.sh"
echo ""
echo "🌐 Access your garage monitor at: http://$(hostname -I | awk '{print $1}'):5000"
