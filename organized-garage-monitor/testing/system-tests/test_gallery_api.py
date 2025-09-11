#!/usr/bin/env python3
"""
Test script to verify the gallery API is working correctly
"""

import requests
import json
import os
from datetime import datetime

def test_gallery_api():
    """Test the gallery API endpoints"""
    print("🧪 Testing Gallery API...")
    print("=" * 40)
    
    base_url = "http://localhost:5000"
    
    # Test 1: Check if web server is running
    print("1️⃣ Testing web server status...")
    try:
        response = requests.get(f"{base_url}/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Web server is running")
            print(f"   📹 Camera connected: {data.get('camera_connected', False)}")
            print(f"   🔄 Streaming: {data.get('is_streaming', False)}")
        else:
            print(f"   ❌ Web server returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Cannot connect to web server: {e}")
        return False
    
    # Test 2: Test photos API
    print("\n2️⃣ Testing photos API...")
    try:
        response = requests.get(f"{base_url}/api/photos", timeout=10)
        if response.status_code == 200:
            data = response.json()
            photos = data.get('photos', [])
            print(f"   ✅ Photos API working")
            print(f"   📸 Found {len(photos)} photos")
            
            if photos:
                print("   📋 Recent photos:")
                for i, photo in enumerate(photos[:3]):  # Show first 3
                    print(f"      {i+1}. {photo['filename']} ({photo['date']} {photo['time']})")
            else:
                print("   📷 No photos found")
        else:
            print(f"   ❌ Photos API returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error testing photos API: {e}")
        return False
    
    # Test 3: Test individual photo serving
    print("\n3️⃣ Testing individual photo serving...")
    try:
        # First get the photos list
        response = requests.get(f"{base_url}/api/photos", timeout=10)
        if response.status_code == 200:
            data = response.json()
            photos = data.get('photos', [])
            
            if photos:
                # Test serving the first photo
                first_photo = photos[0]
                photo_url = f"{base_url}{first_photo['path']}"
                print(f"   📸 Testing photo: {first_photo['filename']}")
                
                response = requests.head(photo_url, timeout=10)
                if response.status_code == 200:
                    print(f"   ✅ Photo serving working")
                    print(f"   📏 Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
                    print(f"   📦 Content-Length: {response.headers.get('Content-Length', 'Unknown')} bytes")
                else:
                    print(f"   ❌ Photo serving returned status {response.status_code}")
                    return False
            else:
                print("   ⚠️ No photos to test serving")
        else:
            print(f"   ❌ Cannot get photos list for testing")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error testing photo serving: {e}")
        return False
    
    # Test 4: Check photos directory
    print("\n4️⃣ Checking photos directory...")
    photos_dir = "photos"
    if os.path.exists(photos_dir):
        files = os.listdir(photos_dir)
        photo_files = [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        print(f"   ✅ Photos directory exists")
        print(f"   📁 Total files: {len(files)}")
        print(f"   📸 Photo files: {len(photo_files)}")
        
        if photo_files:
            print("   📋 Photo files:")
            for photo in photo_files[:5]:  # Show first 5
                filepath = os.path.join(photos_dir, photo)
                mtime = os.path.getmtime(filepath)
                timestamp = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
                print(f"      {photo} ({timestamp})")
    else:
        print(f"   ❌ Photos directory does not exist")
        return False
    
    print("\n✅ All tests passed!")
    return True

def main():
    """Main test function"""
    print("🧪 Gallery API Test Suite")
    print("=" * 50)
    print(f"⏰ Test started at: {datetime.now()}")
    print()
    
    success = test_gallery_api()
    
    if success:
        print("\n🎉 Gallery API is working correctly!")
        print("💡 If the refresh button still doesn't work, check browser console for errors")
    else:
        print("\n❌ Gallery API has issues!")
        print("💡 Check the error messages above and fix the problems")
    
    print("\n🔧 Troubleshooting tips:")
    print("   - Make sure the Flask app is running")
    print("   - Check browser console for JavaScript errors")
    print("   - Try hard refresh (Ctrl+F5) in browser")
    print("   - Check if photos directory exists and has photos")

if __name__ == "__main__":
    main()
