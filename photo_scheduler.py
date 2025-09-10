#!/usr/bin/env python3
"""
Photo Scheduler for Garage Door Monitor
Captures photos at specified intervals for ML training data collection
"""

import cv2
import time
import schedule
import threading
from datetime import datetime, time as dt_time
import os
import json
import logging
import requests

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('photo_scheduler.log'),
        logging.StreamHandler()
    ]
)

class PhotoScheduler:
    def __init__(self):
        self.camera = None
        self.camera_index = None
        self.is_running = False
        self.photo_count = 0
        self.photos_dir = "photos"
        self.metadata_file = "photo_metadata.json"
        self.web_server_url = "http://localhost:5000"
        
        # Create photos directory
        os.makedirs(self.photos_dir, exist_ok=True)
        
        # Load existing metadata
        self.metadata = self.load_metadata()
        
    def load_metadata(self):
        """Load photo metadata from file"""
        if os.path.exists(self.metadata_file):
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            'total_photos': 0,
            'photos_by_date': {},
            'last_capture': None
        }
    
    def save_metadata(self):
        """Save photo metadata to file"""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            logging.error(f"Failed to save metadata: {e}")
    
    def check_web_server(self):
        """Check if the web server is running and accessible"""
        try:
            response = requests.get(f"{self.web_server_url}/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                logging.info(f"✅ Web server is running, camera connected: {data.get('camera_connected', False)}")
                return data.get('camera_connected', False)
            else:
                logging.warning(f"⚠️ Web server responded with status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            logging.error(f"❌ Cannot connect to web server: {e}")
            return False
    
    def capture_photo(self, reason="scheduled"):
        """Capture a photo using the Flask app's camera API"""
        try:
            # Use the Flask app's capture endpoint
            response = requests.get(f"{self.web_server_url}/capture", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success', False):
                    # The Flask app already saved the photo, we just need to update our metadata
                    filename = data.get('filename', 'unknown.jpg')
                    timestamp = datetime.now()
                    
                    # Update metadata
                    self.photo_count += 1
                    date_str = timestamp.strftime('%Y-%m-%d')
                    
                    if date_str not in self.metadata['photos_by_date']:
                        self.metadata['photos_by_date'][date_str] = 0
                    self.metadata['photos_by_date'][date_str] += 1
                    
                    self.metadata['total_photos'] = self.photo_count
                    self.metadata['last_capture'] = timestamp.isoformat()
                    
                    # Save metadata
                    self.save_metadata()
                    
                    # Log success
                    logging.info(f"📸 Photo captured via API: {filename} (Reason: {reason})")
                    logging.info(f"📊 Total photos: {self.photo_count}")
                    
                    return True
                else:
                    logging.error(f"Flask app capture failed: {data.get('error', 'Unknown error')}")
                    return False
            else:
                logging.error(f"Failed to capture photo via API: HTTP {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            logging.error(f"Error connecting to Flask app for photo capture: {e}")
            return False
        except Exception as e:
            logging.error(f"Error capturing photo: {e}")
            return False
    
    def get_current_interval(self):
        """Determine current photo interval based on time of day"""
        now = datetime.now().time()
        
        # High frequency periods: 7:00-9:30 AM and 4:00-7:00 PM (5 minutes)
        morning_start = dt_time(7, 0)
        morning_end = dt_time(9, 30)
        evening_start = dt_time(16, 0)  # 4:00 PM
        evening_end = dt_time(19, 0)    # 7:00 PM
        
        if (morning_start <= now <= morning_end) or (evening_start <= now <= evening_end):
            return 5  # 5 minutes
        else:
            return 15  # 15 minutes
    
    def schedule_photos(self):
        """Set up photo capture schedule"""
        logging.info("📅 Setting up photo capture schedule...")
        
        # Clear existing schedule
        schedule.clear()
        
        # Schedule photos every 5 minutes during high-activity periods
        schedule.every(5).minutes.do(self.capture_photo, reason="high_frequency").tag("high_freq")
        
        # Schedule photos every 15 minutes during low-activity periods  
        schedule.every(15).minutes.do(self.capture_photo, reason="low_frequency").tag("low_freq")
        
        logging.info("✅ Photo schedule configured:")
        logging.info("   - 5 minutes: 7:00-9:30 AM and 4:00-7:00 PM")
        logging.info("   - 15 minutes: All other times")
    
    def run_scheduler(self):
        """Run the photo scheduler"""
        if not self.check_web_server():
            logging.error("Cannot start scheduler - web server not available or camera not connected")
            return
        
        self.is_running = True
        logging.info("🚀 Photo scheduler started! Using Flask app's camera API")
        
        try:
            while self.is_running:
                # Check if web server is still available
                if not self.check_web_server():
                    logging.error("Web server became unavailable, stopping scheduler")
                    break
                
                # Check current time and adjust schedule if needed
                current_interval = self.get_current_interval()
                
                # Run pending scheduled jobs
                schedule.run_pending()
                
                # Sleep for a short time to avoid busy waiting
                time.sleep(1)
                
        except KeyboardInterrupt:
            logging.info("🛑 Photo scheduler stopped by user")
        except Exception as e:
            logging.error(f"Error in scheduler: {e}")
        finally:
            self.stop_scheduler()
    
    def stop_scheduler(self):
        """Stop the photo scheduler"""
        self.is_running = False
        # No need to release camera since we're using the Flask app's camera
        logging.info("📸 Photo scheduler stopped")
    
    def get_stats(self):
        """Get photo capture statistics"""
        return {
            'total_photos': self.photo_count,
            'photos_today': self.metadata['photos_by_date'].get(
                datetime.now().strftime('%Y-%m-%d'), 0
            ),
            'last_capture': self.metadata['last_capture'],
            'is_running': self.is_running,
            'current_interval': self.get_current_interval()
        }

def main():
    """Main function to run the photo scheduler"""
    print("📸 Garage Door Monitor - Photo Scheduler")
    print("=" * 50)
    
    scheduler = PhotoScheduler()
    
    # Set up the schedule
    scheduler.schedule_photos()
    
    # Show initial stats
    stats = scheduler.get_stats()
    print(f"📊 Current stats:")
    print(f"   Total photos: {stats['total_photos']}")
    print(f"   Photos today: {stats['photos_today']}")
    print(f"   Current interval: {stats['current_interval']} minutes")
    print()
    
    print("🕐 Schedule:")
    print("   - 7:00-9:30 AM: Every 5 minutes")
    print("   - 4:00-7:00 PM: Every 5 minutes") 
    print("   - All other times: Every 15 minutes")
    print()
    print("📡 Using Flask app's camera API for photo capture")
    print("🛑 Press Ctrl+C to stop")
    print()
    
    try:
        # Run the scheduler
        scheduler.run_scheduler()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down photo scheduler...")
    finally:
        scheduler.stop_scheduler()
        print("✅ Photo scheduler stopped")

if __name__ == "__main__":
    main()


