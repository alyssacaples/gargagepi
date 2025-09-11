#!/usr/bin/env python3
"""
Quick test script for photo_scheduler.py
This tests the photo scheduler in isolation
"""

import sys
import time
import subprocess
import requests
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_photo_scheduler():
    """Test photo scheduler functionality"""
    print("🧪 Testing Photo Scheduler")
    print("=" * 40)
    
    # First, start Flask app
    print("1. Starting Flask app...")
    flask_process = subprocess.Popen([sys.executable, 'app.py'], 
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for Flask to start
    time.sleep(3)
    
    # Check if Flask is running
    try:
        response = requests.get("http://localhost:5000/status", timeout=5)
        if response.status_code == 200:
            print("✅ Flask app is running")
        else:
            print("❌ Flask app not responding")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to Flask app: {e}")
        return False
    
    # Test photo scheduler
    print("2. Testing photo scheduler...")
    try:
        # Run photo scheduler for a short time
        scheduler_process = subprocess.Popen([sys.executable, 'photo_scheduler.py'],
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Wait for test photos
        print("⏳ Waiting for test photos (45s and 90s)...")
        time.sleep(100)  # Wait for both test photos
        
        # Check if scheduler is still running
        if scheduler_process.poll() is None:
            print("✅ Photo scheduler is running stable")
            
            # Check for photos
            import os
            if os.path.exists("photos"):
                photos = [f for f in os.listdir("photos") if f.endswith('.jpg')]
                print(f"📸 Found {len(photos)} photos in photos directory")
                if photos:
                    print("✅ Photos are being captured")
                else:
                    print("⚠️  No photos found")
            else:
                print("❌ Photos directory not found")
                
            # Stop scheduler
            scheduler_process.terminate()
            scheduler_process.wait()
            print("✅ Photo scheduler stopped cleanly")
            
        else:
            stdout, stderr = scheduler_process.communicate()
            print(f"❌ Photo scheduler exited: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing photo scheduler: {e}")
        return False
    finally:
        # Clean up Flask
        flask_process.terminate()
        flask_process.wait()
        print("✅ Flask app stopped")
    
    print("\n🎉 Photo scheduler test completed!")
    return True

if __name__ == "__main__":
    test_photo_scheduler()
