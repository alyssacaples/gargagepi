#!/usr/bin/env python3
"""
System Status Checker for Garage Door Monitor
Shows system information and network details
"""

import subprocess
import socket
import os
import json
from datetime import datetime

def get_ip_address():
    """Get the Pi's IP address"""
    try:
        # Connect to a remote address to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "Unable to determine"

def get_system_info():
    """Get system information"""
    info = {}
    
    # Check if we're on Raspberry Pi
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()
            if 'BCM' in cpuinfo or 'Raspberry Pi' in cpuinfo:
                info['device'] = 'Raspberry Pi'
            else:
                info['device'] = 'Unknown'
    except:
        info['device'] = 'Unknown'
    
    # Get IP address
    info['ip_address'] = get_ip_address()
    
    # Check available video devices
    try:
        result = subprocess.run(['ls', '/dev/video*'], capture_output=True, text=True)
        if result.returncode == 0:
            info['video_devices'] = result.stdout.strip().split('\n')
        else:
            info['video_devices'] = []
    except:
        info['video_devices'] = []
    
    # Check USB devices
    try:
        result = subprocess.run(['lsusb'], capture_output=True, text=True)
        if result.returncode == 0:
            info['usb_devices'] = result.stdout.strip().split('\n')
        else:
            info['usb_devices'] = []
    except:
        info['usb_devices'] = []
    
    # Check if photos directory exists and count photos
    photos_dir = "photos"
    if os.path.exists(photos_dir):
        try:
            photo_files = [f for f in os.listdir(photos_dir) if f.endswith('.jpg')]
            info['photo_count'] = len(photo_files)
            info['photos_dir'] = os.path.abspath(photos_dir)
        except:
            info['photo_count'] = 0
            info['photos_dir'] = "Error reading directory"
    else:
        info['photo_count'] = 0
        info['photos_dir'] = "Directory does not exist"
    
    # Check if metadata file exists
    metadata_file = "photo_metadata.json"
    if os.path.exists(metadata_file):
        try:
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
                info['total_photos_captured'] = metadata.get('total_photos', 0)
                info['last_capture'] = metadata.get('last_capture', 'Never')
        except:
            info['total_photos_captured'] = 0
            info['last_capture'] = 'Error reading metadata'
    else:
        info['total_photos_captured'] = 0
        info['last_capture'] = 'No metadata file'
    
    return info

def main():
    """Main function"""
    print("🔍 Garage Door Monitor - System Status")
    print("=" * 50)
    
    info = get_system_info()
    
    print(f"🖥️  Device: {info['device']}")
    print(f"🌐 IP Address: {info['ip_address']}")
    print(f"📱 Web Interface: http://{info['ip_address']}:5000")
    print()
    
    print("📹 Video Devices:")
    if info['video_devices']:
        for device in info['video_devices']:
            print(f"   ✅ {device}")
    else:
        print("   ❌ No video devices found")
    print()
    
    print("🔌 USB Devices:")
    if info['usb_devices']:
        for device in info['usb_devices']:
            print(f"   📱 {device}")
    else:
        print("   ❌ No USB devices found")
    print()
    
    print("📸 Photo Storage:")
    print(f"   📁 Directory: {info['photos_dir']}")
    print(f"   📊 Files in directory: {info['photo_count']}")
    print(f"   📈 Total photos captured: {info['total_photos_captured']}")
    print(f"   ⏰ Last capture: {info['last_capture']}")
    print()
    
    print("🚀 Quick Start Commands:")
    print("   Test camera: python3 test_camera.py")
    print("   Start web server: python3 app.py")
    print("   Start photo scheduler: python3 photo_scheduler.py")
    print("   Start everything: python3 start_monitor.py")
    print()
    
    print("📱 Access from other devices:")
    print(f"   - Open browser to: http://{info['ip_address']}:5000")
    print("   - Make sure your device is on the same network")
    print("   - If accessing from outside network, configure port forwarding")

if __name__ == "__main__":
    main()


