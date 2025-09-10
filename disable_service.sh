#!/bin/bash
# Disable Garage Monitor Service
# This script disables the garage monitor service and stops it from starting on boot

echo "🚗 Disabling Garage Monitor Service..."
echo "==================================="

# Check if service exists
if ! systemctl list-unit-files | grep -q "garage-monitor.service"; then
    echo "❌ Garage monitor service not found. Nothing to disable."
    exit 1
fi

# Stop the service
echo "🛑 Stopping garage-monitor service..."
sudo systemctl stop garage-monitor.service

# Disable the service
echo "❌ Disabling garage-monitor service..."
sudo systemctl disable garage-monitor.service

# Check status
echo ""
echo "📊 Service Status:"
sudo systemctl status garage-monitor.service --no-pager -l

echo ""
echo "✅ Garage Monitor Service is now DISABLED and STOPPED!"
echo ""
echo "💡 The service will NOT start automatically on boot."
echo "💡 To re-enable: ./enable_service.sh"
echo "💡 To run manually: python3 app.py (in the project directory)"
echo ""
echo "🔧 For debugging, you can now:"
echo "   - Run manually: python3 app.py"
echo "   - Run with scheduler: python3 start_monitor.py"
echo "   - Check logs: sudo journalctl -u garage-monitor -n 50"
