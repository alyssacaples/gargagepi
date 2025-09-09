#!/usr/bin/env python3
"""
Garage Door Monitor - Web Server
Provides live camera stream and basic web interface
"""

import cv2
import threading
import time
from flask import Flask, render_template, Response, jsonify
from datetime import datetime
import os

app = Flask(__name__)

class CameraManager:
    def __init__(self):
        self.camera = None
        self.camera_index = None
        self.is_streaming = False
        self.last_frame = None
        self.frame_lock = threading.Lock()
        
    def initialize_camera(self):
        """Initialize the USB camera"""
        print("🔍 Initializing camera...")
        
        # Try to find working camera
        for i in range(3):
            print(f"Trying camera index {i}...")
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    self.camera = cap
                    self.camera_index = i
                    print(f"✅ Camera found at index {i}")
                    return True
                else:
                    cap.release()
            else:
                cap.release()
        
        print("❌ No working camera found!")
        return False
    
    def start_streaming(self):
        """Start camera streaming in background thread"""
        if not self.camera:
            if not self.initialize_camera():
                return False
        
        self.is_streaming = True
        self.stream_thread = threading.Thread(target=self._stream_frames)
        self.stream_thread.daemon = True
        self.stream_thread.start()
        return True
    
    def _stream_frames(self):
        """Background thread to capture frames"""
        while self.is_streaming and self.camera:
            ret, frame = self.camera.read()
            if ret and frame is not None:
                with self.frame_lock:
                    self.last_frame = frame.copy()
            time.sleep(0.033)  # ~30 FPS
    
    def get_frame(self):
        """Get the latest frame for streaming"""
        with self.frame_lock:
            if self.last_frame is not None:
                return self.last_frame.copy()
        return None
    
    def capture_photo(self, filename=None):
        """Capture a single photo"""
        if not self.camera:
            return None
        
        ret, frame = self.camera.read()
        if ret and frame is not None:
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"photos/garage_{timestamp}.jpg"
            
            # Create photos directory if it doesn't exist
            os.makedirs("photos", exist_ok=True)
            
            cv2.imwrite(filename, frame)
            return filename
        return None
    
    def stop_streaming(self):
        """Stop camera streaming"""
        self.is_streaming = False
        if self.camera:
            self.camera.release()

# Global camera manager
camera_manager = CameraManager()

def generate_frames():
    """Generate frames for video streaming"""
    while True:
        frame = camera_manager.get_frame()
        if frame is not None:
            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            if ret:
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        time.sleep(0.033)  # ~30 FPS

@app.route('/')
def index():
    """Main page with live stream"""
    return render_template('index.html')

@app.route('/stream')
def stream():
    """Video streaming route"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/capture')
def capture():
    """Capture a single photo"""
    filename = camera_manager.capture_photo()
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

@app.route('/status')
def status():
    """Get system status"""
    return jsonify({
        'camera_connected': camera_manager.camera is not None,
        'is_streaming': camera_manager.is_streaming,
        'camera_index': camera_manager.camera_index,
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🚗 Starting Garage Door Monitor Web Server...")
    print("=" * 50)
    
    # Initialize camera
    if camera_manager.start_streaming():
        print("✅ Camera streaming started")
        print("🌐 Web server starting on http://0.0.0.0:5000")
        print("📱 Access from any device on your network:")
        print("   - Live stream: http://[PI_IP]:5000")
        print("   - Status API: http://[PI_IP]:5000/status")
        print("   - Capture photo: http://[PI_IP]:5000/capture")
        print("\n💡 To find your Pi's IP: hostname -I")
        print("🛑 Press Ctrl+C to stop")
        
        try:
            app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
        finally:
            camera_manager.stop_streaming()
    else:
        print("❌ Failed to initialize camera. Check your USB webcam connection.")


