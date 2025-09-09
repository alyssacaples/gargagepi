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
    
    def initialize_camera(self):
        """Initialize the USB camera"""
        logging.info("🔍 Initializing camera for photo scheduler...")
        
        # Try to find working camera
        for i in range(3):
            logging.info(f"Trying camera index {i}...")
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    self.camera = cap
                    self.camera_index = i
                    logging.info(f"✅ Camera found at index {i}")
                    return True
                else:
                    cap.release()
            else:
                cap.release()
        
        logging.error("❌ No working camera found!")
        return False
    
    def capture_photo(self, reason="scheduled"):
        """Capture a photo and save with metadata"""
        if not self.camera:
            if not self.initialize_camera():
                logging.error("Cannot capture photo - camera not available")
                return False
        
        try:
            ret, frame = self.camera.read()
            if ret and frame is not None:
                # Generate filename with timestamp
                timestamp = datetime.now()
                filename = f"garage_{timestamp.strftime('%Y%m%d_%H%M%S')}.jpg"
                filepath = os.path.join(self.photos_dir, filename)
                
                # Save photo
                cv2.imwrite(filepath, frame)
                
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
                logging.info(f"📸 Photo captured: {filename} (Reason: {reason})")
                logging.info(f"📊 Total photos: {self.photo_count}")
                
                return True
            else:
                logging.error("Failed to capture frame from camera")
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
        if not self.initialize_camera():
            logging.error("Cannot start scheduler - camera not available")
            return
        
        self.is_running = True
        logging.info("🚀 Photo scheduler started!")
        
        try:
            while self.is_running:
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
        if self.camera:
            self.camera.release()
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


