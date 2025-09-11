#!/usr/bin/env python3
"""
Photo Scheduler Debug Script
Helps diagnose issues with the photo scheduler
"""

import requests
import time
import os
import json
from datetime import datetime

def check_web_server():
    """Check if the Flask web server is running and accessible"""
    print("🔍 Checking Flask web server...")
    try:
        response = requests.get("http://localhost:5000/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Web server is running")
            print(f"   Camera connected: {data.get('camera_connected', False)}")
            print(f"   Streaming: {data.get('is_streaming', False)}")
            print(f"   Camera index: {data.get('camera_index', 'Unknown')}")
            return True
        else:
            print(f"❌ Web server responded with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to web server: {e}")
        return False

def test_capture():
    """Test the capture endpoint"""
    print("\n📸 Testing photo capture...")
    try:
        response = requests.get("http://localhost:5000/capture", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success', False):
                filename = data.get('filename', 'unknown')
                print(f"✅ Photo captured successfully: {filename}")
                return True
            else:
                print(f"❌ Capture failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Capture endpoint returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error testing capture: {e}")
        return False

def check_photos_directory():
    """Check if photos directory exists and list photos"""
    print("\n📁 Checking photos directory...")
    photos_dir = "photos"
    
    if not os.path.exists(photos_dir):
        print(f"❌ Photos directory '{photos_dir}' does not exist")
        return False
    
    photos = [f for f in os.listdir(photos_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    print(f"✅ Photos directory exists")
    print(f"   Found {len(photos)} photos")
    
    if photos:
        print("   Recent photos:")
        # Sort by modification time, newest first
        photos_with_time = []
        for photo in photos:
            filepath = os.path.join(photos_dir, photo)
            mtime = os.path.getmtime(filepath)
            photos_with_time.append((photo, mtime))
        
        photos_with_time.sort(key=lambda x: x[1], reverse=True)
        
        for photo, mtime in photos_with_time[:5]:  # Show 5 most recent
            timestamp = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
            print(f"     {photo} ({timestamp})")
    
    return True

def check_photo_scheduler_logs():
    """Check if photo scheduler log file exists and show recent entries"""
    print("\n📋 Checking photo scheduler logs...")
    log_file = "photo_scheduler.log"
    
    if not os.path.exists(log_file):
        print(f"❌ Photo scheduler log file '{log_file}' not found")
        return False
    
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
        
        print(f"✅ Log file exists with {len(lines)} lines")
        
        if lines:
            print("   Recent log entries:")
            # Show last 10 lines
            for line in lines[-10:]:
                print(f"     {line.strip()}")
        
        return True
    except Exception as e:
        print(f"❌ Error reading log file: {e}")
        return False

def check_systemd_service():
    """Check if the systemd service is running"""
    print("\n⚙️ Checking systemd service...")
    try:
        import subprocess
        result = subprocess.run(['systemctl', 'is-active', 'garage-monitor'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            status = result.stdout.strip()
            print(f"✅ Service status: {status}")
            
            # Get more detailed status
            result = subprocess.run(['systemctl', 'status', 'garage-monitor', '--no-pager'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines[:5]:  # Show first 5 lines
                    if line.strip():
                        print(f"     {line.strip()}")
            
            return status == 'active'
        else:
            print(f"❌ Service is not active")
            return False
            
    except Exception as e:
        print(f"❌ Error checking service: {e}")
        return False

def main():
    """Run all diagnostic checks"""
    print("🚗 Photo Scheduler Diagnostic Tool")
    print("=" * 40)
    print(f"⏰ Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run all checks
    web_server_ok = check_web_server()
    capture_ok = test_capture() if web_server_ok else False
    photos_dir_ok = check_photos_directory()
    logs_ok = check_photo_scheduler_logs()
    service_ok = check_systemd_service()
    
    print("\n" + "=" * 40)
    print("📊 DIAGNOSTIC SUMMARY:")
    print(f"   Web Server: {'✅ OK' if web_server_ok else '❌ FAIL'}")
    print(f"   Photo Capture: {'✅ OK' if capture_ok else '❌ FAIL'}")
    print(f"   Photos Directory: {'✅ OK' if photos_dir_ok else '❌ FAIL'}")
    print(f"   Logs: {'✅ OK' if logs_ok else '❌ FAIL'}")
    print(f"   Systemd Service: {'✅ OK' if service_ok else '❌ FAIL'}")
    
    print("\n💡 TROUBLESHOOTING TIPS:")
    if not web_server_ok:
        print("   - Start the Flask app: python3 app.py")
        print("   - Or start the service: ./enable_service.sh")
    elif not capture_ok:
        print("   - Check camera connection")
        print("   - Restart the Flask app")
    elif not service_ok:
        print("   - Enable the service: ./enable_service.sh")
        print("   - Check service logs: sudo journalctl -u garage-monitor -f")
    else:
        print("   - Everything looks good! Check photo scheduler logs for timing issues")
        print("   - Run photo scheduler manually: python3 photo_scheduler.py")

if __name__ == "__main__":
    main()
