#!/usr/bin/env python3
"""
Garage Door Monitor Launcher
Starts both the web server and photo scheduler
"""

import subprocess
import sys
import time
import signal
import os
import socket
from threading import Thread

def get_local_ip():
    """Get the local IP address of the Raspberry Pi"""
    try:
        # Connect to a remote address to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        # Fallback method
        try:
            result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
            return result.stdout.strip().split()[0]
        except:
            return "localhost"

class MonitorLauncher:
    def __init__(self):
        self.web_server_process = None
        self.photo_scheduler_process = None
        self.running = False
    
    def start_web_server(self):
        """Start the Flask web server"""
        print("🌐 Starting web server...")
        try:
            # Use unbuffered output and proper working directory
            self.web_server_process = subprocess.Popen([
                sys.executable, '-u', 'app.py'  # -u for unbuffered output
            ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
               universal_newlines=True, bufsize=1)
            
            # Give it a moment to start
            time.sleep(2)
            
            # Check if it's still running
            if self.web_server_process.poll() is None:
                print("✅ Web server started successfully")
                return True
            else:
                # Get any error output
                stdout, stderr = self.web_server_process.communicate()
                print(f"❌ Web server failed to start")
                if stdout:
                    print(f"Output: {stdout}")
                if stderr:
                    print(f"Error: {stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to start web server: {e}")
            return False
    
    def start_photo_scheduler(self):
        """Start the photo scheduler"""
        print("📸 Starting photo scheduler...")
        try:
            # Use unbuffered output
            self.photo_scheduler_process = subprocess.Popen([
                sys.executable, '-u', 'photo_scheduler.py'
            ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
               universal_newlines=True, bufsize=1)
            
            # Give it a moment to start
            time.sleep(1)
            
            # Check if it's still running
            if self.photo_scheduler_process.poll() is None:
                print("✅ Photo scheduler started successfully")
                return True
            else:
                # Get any error output
                stdout, stderr = self.photo_scheduler_process.communicate()
                print(f"❌ Photo scheduler failed to start")
                if stdout:
                    print(f"Output: {stdout}")
                if stderr:
                    print(f"Error: {stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to start photo scheduler: {e}")
            return False
    
    def stop_all(self):
        """Stop all processes"""
        print("\n🛑 Stopping all services...")
        self.running = False
        
        if self.web_server_process:
            self.web_server_process.terminate()
            print("🌐 Web server stopped")
        
        if self.photo_scheduler_process:
            self.photo_scheduler_process.terminate()
            print("📸 Photo scheduler stopped")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n🛑 Received signal {signum}, shutting down...")
        self.stop_all()
        sys.exit(0)
    
    def run(self):
        """Run the complete garage door monitor system"""
        print("🚗 Garage Door Monitor - Starting Complete System")
        print("=" * 60)
        
        # Debug info
        print(f"🐍 Python executable: {sys.executable}")
        print(f"📁 Working directory: {os.getcwd()}")
        print(f"📋 Files in directory: {os.listdir('.')}")
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Start web server
        if not self.start_web_server():
            print("❌ Cannot start without web server")
            print("💡 Try running 'python3 app.py' directly to see the error")
            return False
        
        # Start photo scheduler
        if not self.start_photo_scheduler():
            print("⚠️  Photo scheduler failed to start, continuing with web server only")
        
        self.running = True
        
        # Get the Pi's IP address
        pi_ip = get_local_ip()
        
        print("\n🎉 Garage Door Monitor is running!")
        print("=" * 40)
        print(f"📱 Web Interface: http://{pi_ip}:5000")
        print(f"💡 Your Pi's IP address: {pi_ip}")
        print("📸 Photos will be saved to: ./photos/")
        print("📊 Check logs for status updates")
        print("\n🛑 Press Ctrl+C to stop all services")
        print()
        
        try:
            # Monitor processes
            while self.running:
                # Check if web server is still running
                if self.web_server_process and self.web_server_process.poll() is not None:
                    print("❌ Web server stopped unexpectedly")
                    break
                
                # Check if photo scheduler is still running
                if self.photo_scheduler_process and self.photo_scheduler_process.poll() is not None:
                    print("⚠️  Photo scheduler stopped unexpectedly")
                    # Don't break, continue with web server only
                
                time.sleep(5)  # Check every 5 seconds
                
        except KeyboardInterrupt:
            pass
        finally:
            self.stop_all()
            print("✅ All services stopped")

def main():
    """Main function"""
    launcher = MonitorLauncher()
    launcher.run()

if __name__ == "__main__":
    main()


