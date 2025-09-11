#!/usr/bin/env python3
"""
Lightweight Stream Server for Raspberry Pi
Serves camera stream for cloud access via port forwarding/tunneling
"""

import cv2
import threading
import time
import logging
from flask import Flask, Response, jsonify, render_template_string, request
import socket
import os
import json
import schedule
import requests
from datetime import datetime
import glob

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stream_server.log'),
        logging.StreamHandler()
    ]
)

class PhotoScheduler:
    def __init__(self, camera_manager):
        self.camera_manager = camera_manager
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
    
    def capture_photo(self, reason="scheduled"):
        """Capture a photo"""
        try:
            frame = self.camera_manager.get_frame()
            if frame is not None:
                # Create photos directory
                os.makedirs(self.photos_dir, exist_ok=True)
                
                # Generate filename
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f'garage_{timestamp}.jpg'
                filepath = os.path.join(self.photos_dir, filename)
                
                # Save photo
                if cv2.imwrite(filepath, frame):
                    # Update metadata
                    self.photo_count += 1
                    date_str = datetime.now().strftime('%Y-%m-%d')
                    
                    if date_str not in self.metadata['photos_by_date']:
                        self.metadata['photos_by_date'][date_str] = 0
                    self.metadata['photos_by_date'][date_str] += 1
                    
                    self.metadata['total_photos'] = self.photo_count
                    self.metadata['last_capture'] = datetime.now().isoformat()
                    
                    # Save metadata
                    self.save_metadata()
                    
                    # Log success
                    logging.info(f"📸 Photo captured: {filename} (Reason: {reason})")
                    logging.info(f"📊 Total photos: {self.photo_count}")
                    
                    return filename
                else:
                    logging.error("Failed to save photo")
                    return None
            else:
                logging.error("No frame available for photo capture")
                return None
                
        except Exception as e:
            logging.error(f"Error capturing photo: {e}")
            return None
    
    def get_current_interval(self):
        """Determine current photo interval based on time of day"""
        now = datetime.now().time()
        
        # High frequency periods: 7:00-9:30 AM and 4:00-7:00 PM (5 minutes)
        morning_start = datetime.time(7, 0)
        morning_end = datetime.time(9, 30)
        evening_start = datetime.time(16, 0)  # 4:00 PM
        evening_end = datetime.time(19, 0)    # 7:00 PM
        
        if (morning_start <= now <= morning_end) or (evening_start <= now <= evening_end):
            return 5  # 5 minutes
        else:
            return 15  # 15 minutes
    
    def schedule_photos(self):
        """Set up photo capture schedule"""
        logging.info("📅 Setting up photo capture schedule...")
        
        # Clear existing schedule
        schedule.clear()
        
        # Schedule test photos for immediate verification
        schedule.every(45).seconds.do(self.capture_photo, reason="test_45s").tag("test")
        schedule.every(90).seconds.do(self.capture_photo, reason="test_90s").tag("test")
        
        # Schedule photos every 5 minutes during high-activity periods
        schedule.every(5).minutes.do(self.capture_photo, reason="high_frequency").tag("high_freq")
        
        # Schedule photos every 15 minutes during low-activity periods  
        schedule.every(15).minutes.do(self.capture_photo, reason="low_frequency").tag("low_freq")
        
        logging.info("✅ Photo schedule configured:")
        logging.info("   - Test photos: 45 seconds and 90 seconds after start")
        logging.info("   - 5 minutes: 7:00-9:30 AM and 4:00-7:00 PM")
        logging.info("   - 15 minutes: All other times")
    
    def start_scheduler(self):
        """Start the photo scheduler"""
        if not self.camera_manager.is_streaming:
            logging.error("Cannot start scheduler - camera not streaming")
            return False
            
        self.is_running = True
        logging.info("🚀 Photo scheduler started!")
        
        # Set up the schedule
        self.schedule_photos()
        
        # Start scheduler thread
        threading.Thread(target=self._scheduler_loop, daemon=True).start()
        return True
    
    def _scheduler_loop(self):
        """Main scheduler loop"""
        start_time = time.time()
        
        try:
            while self.is_running:
                # Run pending scheduled jobs
                schedule.run_pending()
                
                # Clear test photos after they've been taken (after 2 minutes)
                elapsed_time = time.time() - start_time
                if elapsed_time > 120:
                    logging.info("🧹 Clearing test photo schedules after 2 minutes")
                    schedule.clear(tag="test")
                    logging.info("✅ Test schedules cleared, regular schedules continue")
                
                # Sleep for a short time to avoid busy waiting
                time.sleep(1)
                
        except Exception as e:
            logging.error(f"Error in scheduler loop: {e}")
    
    def stop_scheduler(self):
        """Stop the photo scheduler"""
        self.is_running = False
        schedule.clear()
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

class CameraManager:
    def __init__(self, camera_index=0):
        self.camera_index = camera_index
        self.camera = None
        self.is_streaming = False
        self.frame = None
        self.lock = threading.Lock()
        
    def initialize_camera(self):
        """Initialize camera"""
        try:
            self.camera = cv2.VideoCapture(self.camera_index)
            if not self.camera.isOpened():
                logging.error(f"Failed to open camera {self.camera_index}")
                return False
                
            # Set camera properties
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)
            
            logging.info(f"Camera {self.camera_index} initialized successfully")
            return True
            
        except Exception as e:
            logging.error(f"Error initializing camera: {e}")
            return False
    
    def start_streaming(self):
        """Start camera streaming in separate thread"""
        if not self.camera:
            if not self.initialize_camera():
                return False
                
        self.is_streaming = True
        threading.Thread(target=self._stream_loop, daemon=True).start()
        logging.info("Camera streaming started")
        return True
    
    def _stream_loop(self):
        """Main streaming loop"""
        while self.is_streaming:
            try:
                ret, frame = self.camera.read()
                if ret:
                    with self.lock:
                        self.frame = frame.copy()
                else:
                    logging.warning("Failed to read frame from camera")
                    time.sleep(0.1)
            except Exception as e:
                logging.error(f"Error in stream loop: {e}")
                time.sleep(0.1)
    
    def get_frame(self):
        """Get current frame"""
        with self.lock:
            return self.frame.copy() if self.frame is not None else None
    
    def stop_streaming(self):
        """Stop camera streaming"""
        self.is_streaming = False
        if self.camera:
            self.camera.release()
        logging.info("Camera streaming stopped")

def get_local_ip():
    """Get local IP address"""
    try:
        # Connect to a remote address to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"

# Initialize Flask app
app = Flask(__name__)
camera_manager = CameraManager()
photo_scheduler = None

# HTML template for the stream page
STREAM_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Garage Door Monitor - Live Stream</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f0f0f0;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 20px;
        }
        .stream-container {
            text-align: center;
            margin: 20px 0;
        }
        img {
            max-width: 100%;
            height: auto;
            border: 2px solid #ddd;
            border-radius: 5px;
        }
        .status {
            text-align: center;
            margin: 10px 0;
            padding: 10px;
            border-radius: 5px;
        }
        .status.online {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .status.offline {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .info {
            background-color: #e2e3e5;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .info h3 {
            margin-top: 0;
        }
        .info code {
            background-color: #f8f9fa;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: monospace;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏠 Garage Door Monitor</h1>
        
        <div class="status online">
            ✅ Stream Server Online
        </div>
        
        <div class="stream-container">
            <img src="/video_feed" alt="Live Stream" id="stream">
        </div>
        
        <div class="info">
            <h3>📡 Stream Information</h3>
            <p><strong>Local IP:</strong> <code>{{ local_ip }}</code></p>
            <p><strong>Port:</strong> <code>5000</code></p>
            <p><strong>Stream URL:</strong> <code>http://{{ local_ip }}:5000/video_feed</code></p>
            <p><strong>Status:</strong> <code>/status</code></p>
        </div>
        
        <div class="info">
            <h3>🔧 For Cloud Hosting</h3>
            <p>Use this stream URL in your cloud-hosted website:</p>
            <p><code>http://{{ local_ip }}:5000/video_feed</code></p>
            <p>Or use ngrok/Cloudflare tunnel for public access.</p>
        </div>
    </div>
    
    <script>
        // Auto-refresh stream every 30 seconds to prevent timeout
        setInterval(function() {
            const img = document.getElementById('stream');
            img.src = '/video_feed?t=' + new Date().getTime();
        }, 30000);
        
        // Handle stream errors
        document.getElementById('stream').onerror = function() {
            this.src = '/video_feed?t=' + new Date().getTime();
        };
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Main page with stream"""
    local_ip = get_local_ip()
    return render_template_string(STREAM_TEMPLATE, local_ip=local_ip)

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    def generate_frames():
        while True:
            frame = camera_manager.get_frame()
            if frame is not None:
                # Encode frame as JPEG
                ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                if ret:
                    frame_bytes = buffer.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                else:
                    time.sleep(0.1)
            else:
                time.sleep(0.1)
    
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/status')
def status():
    """Get stream status"""
    return jsonify({
        'camera_connected': camera_manager.camera is not None,
        'is_streaming': camera_manager.is_streaming,
        'local_ip': get_local_ip(),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/capture')
def capture():
    """Capture a single photo"""
    if photo_scheduler:
        filename = photo_scheduler.capture_photo("manual")
        if filename:
            return jsonify({
                'success': True,
                'filename': filename,
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to capture photo'
            }), 500
    else:
        return jsonify({
            'success': False,
            'error': 'Photo scheduler not initialized'
        }), 500

@app.route('/api/photos')
def api_photos():
    """Get list of photos"""
    try:
        photos_dir = "photos"
        if not os.path.exists(photos_dir):
            return jsonify({
                'photos': [],
                'total_photos': 0,
                'photos_today': 0,
                'last_capture': None
            })
        
        # Get all photo files
        photo_files = glob.glob(os.path.join(photos_dir, "*.jpg"))
        photo_files.sort(key=os.path.getmtime, reverse=True)  # Newest first
        
        photos = []
        for filepath in photo_files:
            filename = os.path.basename(filepath)
            stat = os.stat(filepath)
            photos.append({
                'filename': filename,
                'url': f'/photos/{filename}?t={int(stat.st_mtime)}',
                'timestamp': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'size': stat.st_size
            })
        
        # Get metadata
        metadata = photo_scheduler.metadata if photo_scheduler else {}
        
        return jsonify({
            'photos': photos,
            'total_photos': len(photos),
            'photos_today': metadata.get('photos_by_date', {}).get(
                datetime.now().strftime('%Y-%m-%d'), 0
            ),
            'last_capture': metadata.get('last_capture')
        })
        
    except Exception as e:
        logging.error(f"Error getting photos: {e}")
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/photos/<filename>')
def serve_photo(filename):
    """Serve individual photos"""
    try:
        photos_dir = "photos"
        filepath = os.path.join(photos_dir, filename)
        
        if os.path.exists(filepath):
            return Response(
                open(filepath, 'rb').read(),
                mimetype='image/jpeg',
                headers={
                    'Cache-Control': 'no-cache, no-store, must-revalidate',
                    'Pragma': 'no-cache',
                    'Expires': '0'
                }
            )
        else:
            return jsonify({'error': 'Photo not found'}), 404
            
    except Exception as e:
        logging.error(f"Error serving photo {filename}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/photos/<filename>', methods=['DELETE'])
def delete_photo(filename):
    """Delete a photo"""
    try:
        photos_dir = "photos"
        filepath = os.path.join(photos_dir, filename)
        
        if os.path.exists(filepath):
            os.remove(filepath)
            logging.info(f"Photo deleted: {filename}")
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Photo not found'}), 404
            
    except Exception as e:
        logging.error(f"Error deleting photo {filename}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/scheduler/start', methods=['POST'])
def start_scheduler():
    """Start the photo scheduler"""
    try:
        global photo_scheduler
        if not photo_scheduler:
            photo_scheduler = PhotoScheduler(camera_manager)
        
        if photo_scheduler.start_scheduler():
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Failed to start scheduler'}), 500
            
    except Exception as e:
        logging.error(f"Error starting scheduler: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/scheduler/stop', methods=['POST'])
def stop_scheduler():
    """Stop the photo scheduler"""
    try:
        global photo_scheduler
        if photo_scheduler:
            photo_scheduler.stop_scheduler()
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Scheduler not running'}), 400
            
    except Exception as e:
        logging.error(f"Error stopping scheduler: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/scheduler/status')
def scheduler_status():
    """Get scheduler status"""
    try:
        global photo_scheduler
        if photo_scheduler:
            stats = photo_scheduler.get_stats()
            return jsonify({
                'is_running': stats['is_running'],
                'current_interval': stats['current_interval'],
                'next_photo': 'Unknown',  # Could be enhanced to show next scheduled time
                'total_photos': stats['total_photos'],
                'photos_today': stats['photos_today'],
                'last_capture': stats['last_capture']
            })
        else:
            return jsonify({
                'is_running': False,
                'current_interval': None,
                'next_photo': 'Unknown',
                'total_photos': 0,
                'photos_today': 0,
                'last_capture': None
            })
            
    except Exception as e:
        logging.error(f"Error getting scheduler status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/scheduler/test', methods=['POST'])
def test_scheduler():
    """Schedule test photos"""
    try:
        global photo_scheduler
        if not photo_scheduler:
            photo_scheduler = PhotoScheduler(camera_manager)
        
        # Schedule test photos
        schedule.every(10).seconds.do(photo_scheduler.capture_photo, reason="test_10s").tag("test")
        schedule.every(20).seconds.do(photo_scheduler.capture_photo, reason="test_20s").tag("test")
        
        return jsonify({'success': True})
        
    except Exception as e:
        logging.error(f"Error scheduling test photos: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/scheduler/clear-test', methods=['POST'])
def clear_test_photos():
    """Clear test photo schedules"""
    try:
        schedule.clear(tag="test")
        return jsonify({'success': True})
        
    except Exception as e:
        logging.error(f"Error clearing test photos: {e}")
        return jsonify({'error': str(e)}), 500

def main():
    """Main function"""
    print("🌐 Garage Door Monitor - Complete Stream Server")
    print("=" * 60)
    
    # Initialize camera
    if not camera_manager.start_streaming():
        print("❌ Failed to initialize camera")
        return
    
    # Initialize photo scheduler
    global photo_scheduler
    photo_scheduler = PhotoScheduler(camera_manager)
    print("✅ Photo scheduler initialized")
    
    # Get local IP
    local_ip = get_local_ip()
    port = 5000
    
    print(f"📡 Stream Server Starting...")
    print(f"   Local IP: {local_ip}")
    print(f"   Port: {port}")
    print(f"   Stream URL: http://{local_ip}:{port}/video_feed")
    print(f"   Web Interface: http://{local_ip}:{port}/")
    print()
    print("🔧 For Cloud Hosting:")
    print(f"   Use this URL in your cloud website: http://{local_ip}:{port}/video_feed")
    print("   Or set up ngrok/Cloudflare tunnel for public access")
    print()
    print("📸 Features Available:")
    print("   - Live streaming")
    print("   - Photo capture")
    print("   - Photo gallery")
    print("   - Photo scheduler")
    print("   - Remote control")
    print()
    print("🛑 Press Ctrl+C to stop")
    print()
    
    try:
        # Start Flask app
        app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down stream server...")
    finally:
        if photo_scheduler:
            photo_scheduler.stop_scheduler()
        camera_manager.stop_streaming()
        print("✅ Stream server stopped")

if __name__ == "__main__":
    main()
