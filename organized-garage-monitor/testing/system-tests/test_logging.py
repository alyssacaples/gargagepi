#!/usr/bin/env python3
"""
Test script to verify photo scheduler logging is working
"""

import logging
import time
import requests
from datetime import datetime

def setup_logging():
    """Set up logging configuration"""
    # Clear any existing handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # File handler
    file_handler = logging.FileHandler('test_logging.log')
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        handlers=[file_handler, console_handler]
    )

def test_photo_capture():
    """Test photo capture and logging"""
    print("🧪 Testing photo capture and logging...")
    
    # Test logging
    logging.info("🧪 Starting photo capture test...")
    
    try:
        # Test web server connection
        response = requests.get("http://localhost:5000/status", timeout=5)
        if response.status_code == 200:
            logging.info("✅ Web server is accessible")
            
            # Test photo capture
            logging.info("📸 Attempting to capture test photo...")
            response = requests.get("http://localhost:5000/capture", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success', False):
                    filename = data.get('filename', 'unknown')
                    logging.info(f"✅ Test photo captured successfully: {filename}")
                    logging.info(f"📊 Photo capture test completed at {datetime.now()}")
                    return True
                else:
                    logging.error(f"❌ Photo capture failed: {data.get('error', 'Unknown error')}")
                    return False
            else:
                logging.error(f"❌ Capture endpoint returned status {response.status_code}")
                return False
        else:
            logging.error(f"❌ Web server not accessible: status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Connection error: {e}")
        return False
    except Exception as e:
        logging.error(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main test function"""
    setup_logging()
    
    print("🧪 Photo Scheduler Logging Test")
    print("=" * 40)
    print(f"⏰ Test started at: {datetime.now()}")
    print()
    
    # Test logging setup
    logging.info("🚀 Logging test started")
    logging.info("📝 This is a test log message")
    
    # Test photo capture
    success = test_photo_capture()
    
    if success:
        print("✅ Logging test completed successfully!")
        print("📋 Check 'test_logging.log' file for log entries")
    else:
        print("❌ Logging test failed!")
        print("📋 Check 'test_logging.log' file for error details")
    
    print()
    print("💡 If you see log messages above and in the log file, logging is working correctly")

if __name__ == "__main__":
    main()
