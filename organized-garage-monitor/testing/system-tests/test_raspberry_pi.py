#!/usr/bin/env python3
"""
Raspberry Pi Test Suite for Garage Door Monitor
This script simulates the Raspberry Pi environment and tests all components
"""

import os
import sys
import time
import subprocess
import threading
import requests
import json
from datetime import datetime
import signal
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_raspberry_pi.log'),
        logging.StreamHandler()
    ]
)

class RaspberryPiTester:
    def __init__(self):
        self.flask_process = None
        self.scheduler_process = None
        self.start_monitor_process = None
        self.test_results = {}
        self.base_url = "http://localhost:5000"
        
    def log_test(self, test_name, success, message=""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        logging.info(f"{status} {test_name}: {message}")
        self.test_results[test_name] = {"success": success, "message": message}
        
    def cleanup_processes(self):
        """Clean up any running processes"""
        processes = [self.flask_process, self.scheduler_process, self.start_monitor_process]
        for process in processes:
            if process and process.poll() is None:
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except:
                    try:
                        process.kill()
                    except:
                        pass
                        
    def test_file_structure(self):
        """Test that all required files exist"""
        logging.info("🔍 Testing file structure...")
        
        required_files = [
            'app.py',
            'photo_scheduler.py', 
            'start_monitor.py',
            'requirements.txt',
            'templates/index.html'
        ]
        
        all_exist = True
        for file in required_files:
            if os.path.exists(file):
                self.log_test(f"File exists: {file}", True)
            else:
                self.log_test(f"File exists: {file}", False, "File not found")
                all_exist = False
                
        return all_exist
        
    def test_python_imports(self):
        """Test that all Python imports work"""
        logging.info("🐍 Testing Python imports...")
        
        test_scripts = ['app.py', 'photo_scheduler.py', 'start_monitor.py']
        all_imports_work = True
        
        for script in test_scripts:
            try:
                # Test imports by running python -c "import script_name"
                result = subprocess.run([
                    sys.executable, '-c', f'import sys; sys.path.insert(0, "."); exec(open("{script}").read())'
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    self.log_test(f"Imports work: {script}", True)
                else:
                    self.log_test(f"Imports work: {script}", False, result.stderr)
                    all_imports_work = False
                    
            except Exception as e:
                self.log_test(f"Imports work: {script}", False, str(e))
                all_imports_work = False
                
        return all_imports_work
        
    def test_flask_app_startup(self):
        """Test Flask app startup"""
        logging.info("🌐 Testing Flask app startup...")
        
        try:
            # Start Flask app in background
            self.flask_process = subprocess.Popen([
                sys.executable, 'app.py'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Wait for startup
            time.sleep(3)
            
            # Check if process is still running
            if self.flask_process.poll() is None:
                self.log_test("Flask app startup", True, "Process running")
                
                # Test if web server is responding
                try:
                    response = requests.get(f"{self.base_url}/", timeout=5)
                    if response.status_code == 200:
                        self.log_test("Flask web server responding", True)
                        return True
                    else:
                        self.log_test("Flask web server responding", False, f"HTTP {response.status_code}")
                        return False
                except Exception as e:
                    self.log_test("Flask web server responding", False, str(e))
                    return False
            else:
                stdout, stderr = self.flask_process.communicate()
                self.log_test("Flask app startup", False, f"Process exited: {stderr}")
                return False
                
        except Exception as e:
            self.log_test("Flask app startup", False, str(e))
            return False
            
    def test_flask_endpoints(self):
        """Test Flask app endpoints"""
        logging.info("🔗 Testing Flask endpoints...")
        
        endpoints = [
            ('/', 'Home page'),
            ('/status', 'Status endpoint'),
            ('/capture', 'Photo capture endpoint'),
            ('/gallery', 'Photo gallery'),
            ('/api/photos', 'Photos API')
        ]
        
        all_endpoints_work = True
        
        for endpoint, description in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                if response.status_code == 200:
                    self.log_test(f"Endpoint: {endpoint}", True, description)
                else:
                    self.log_test(f"Endpoint: {endpoint}", False, f"HTTP {response.status_code}")
                    all_endpoints_work = False
            except Exception as e:
                self.log_test(f"Endpoint: {endpoint}", False, str(e))
                all_endpoints_work = False
                
        return all_endpoints_work
        
    def test_photo_capture(self):
        """Test photo capture functionality"""
        logging.info("📸 Testing photo capture...")
        
        try:
            # Test capture endpoint
            response = requests.get(f"{self.base_url}/capture", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success', False):
                    filename = data.get('filename', '')
                    if filename and os.path.exists(f"photos/{filename}"):
                        self.log_test("Photo capture", True, f"Photo saved: {filename}")
                        return True
                    else:
                        self.log_test("Photo capture", False, "Photo file not found")
                        return False
                else:
                    self.log_test("Photo capture", False, data.get('error', 'Unknown error'))
                    return False
            else:
                self.log_test("Photo capture", False, f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Photo capture", False, str(e))
            return False
            
    def test_photo_scheduler(self):
        """Test photo scheduler functionality"""
        logging.info("⏰ Testing photo scheduler...")
        
        try:
            # Start photo scheduler in background
            self.scheduler_process = subprocess.Popen([
                sys.executable, 'photo_scheduler.py'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Wait for startup
            time.sleep(2)
            
            # Check if process is still running
            if self.scheduler_process.poll() is None:
                self.log_test("Photo scheduler startup", True, "Process running")
                
                # Wait for test photos (45 seconds and 90 seconds)
                logging.info("⏳ Waiting for test photos (45s and 90s)...")
                time.sleep(100)  # Wait 100 seconds to catch both test photos
                
                # Check if scheduler is still running
                if self.scheduler_process.poll() is None:
                    self.log_test("Photo scheduler stability", True, "Still running after 100s")
                    return True
                else:
                    stdout, stderr = self.scheduler_process.communicate()
                    self.log_test("Photo scheduler stability", False, f"Process exited: {stderr}")
                    return False
            else:
                stdout, stderr = self.scheduler_process.communicate()
                self.log_test("Photo scheduler startup", False, f"Process exited: {stderr}")
                return False
                
        except Exception as e:
            self.log_test("Photo scheduler", False, str(e))
            return False
            
    def test_start_monitor(self):
        """Test start_monitor.py functionality"""
        logging.info("🚀 Testing start_monitor.py...")
        
        try:
            # Start start_monitor in background
            self.start_monitor_process = subprocess.Popen([
                sys.executable, 'start_monitor.py'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Wait for startup
            time.sleep(5)
            
            # Check if process is still running
            if self.start_monitor_process.poll() is None:
                self.log_test("Start monitor startup", True, "Process running")
                
                # Test if web server is accessible
                try:
                    response = requests.get(f"{self.base_url}/status", timeout=5)
                    if response.status_code == 200:
                        self.log_test("Start monitor web server", True, "Web server accessible")
                        
                        # Wait a bit more to see if photo scheduler starts
                        time.sleep(10)
                        
                        # Check if still running
                        if self.start_monitor_process.poll() is None:
                            self.log_test("Start monitor stability", True, "Still running after 15s")
                            return True
                        else:
                            self.log_test("Start monitor stability", False, "Process exited")
                            return False
                    else:
                        self.log_test("Start monitor web server", False, f"HTTP {response.status_code}")
                        return False
                except Exception as e:
                    self.log_test("Start monitor web server", False, str(e))
                    return False
            else:
                stdout, stderr = self.start_monitor_process.communicate()
                self.log_test("Start monitor startup", False, f"Process exited: {stderr}")
                return False
                
        except Exception as e:
            self.log_test("Start monitor", False, str(e))
            return False
            
    def test_photos_directory(self):
        """Test photos directory and file handling"""
        logging.info("📁 Testing photos directory...")
        
        try:
            # Create photos directory if it doesn't exist
            os.makedirs("photos", exist_ok=True)
            self.log_test("Photos directory creation", True)
            
            # Test if we can write to it
            test_file = "photos/test.txt"
            with open(test_file, 'w') as f:
                f.write("test")
            
            if os.path.exists(test_file):
                self.log_test("Photos directory write access", True)
                os.remove(test_file)  # Clean up
                return True
            else:
                self.log_test("Photos directory write access", False, "Cannot write files")
                return False
                
        except Exception as e:
            self.log_test("Photos directory", False, str(e))
            return False
            
    def test_logging(self):
        """Test logging functionality"""
        logging.info("📝 Testing logging...")
        
        try:
            # Test if we can create log files
            test_log = "test_logging.log"
            with open(test_log, 'w') as f:
                f.write("test log entry\n")
            
            if os.path.exists(test_log):
                self.log_test("Log file creation", True)
                os.remove(test_log)  # Clean up
                return True
            else:
                self.log_test("Log file creation", False, "Cannot create log files")
                return False
                
        except Exception as e:
            self.log_test("Logging", False, str(e))
            return False
            
    def run_all_tests(self):
        """Run all tests"""
        logging.info("🧪 Starting Raspberry Pi Test Suite")
        logging.info("=" * 50)
        
        # Clean up any existing processes
        self.cleanup_processes()
        
        try:
            # Run tests
            tests = [
                ("File Structure", self.test_file_structure),
                ("Python Imports", self.test_python_imports),
                ("Photos Directory", self.test_photos_directory),
                ("Logging", self.test_logging),
                ("Flask App Startup", self.test_flask_app_startup),
                ("Flask Endpoints", self.test_flask_endpoints),
                ("Photo Capture", self.test_photo_capture),
                ("Photo Scheduler", self.test_photo_scheduler),
                ("Start Monitor", self.test_start_monitor)
            ]
            
            passed = 0
            total = len(tests)
            
            for test_name, test_func in tests:
                logging.info(f"\n🔍 Running: {test_name}")
                try:
                    if test_func():
                        passed += 1
                except Exception as e:
                    self.log_test(test_name, False, f"Test failed with exception: {e}")
                    
                # Clean up between tests
                self.cleanup_processes()
                time.sleep(1)
                
            # Print summary
            logging.info("\n" + "=" * 50)
            logging.info("📊 TEST SUMMARY")
            logging.info("=" * 50)
            logging.info(f"Total Tests: {total}")
            logging.info(f"Passed: {passed}")
            logging.info(f"Failed: {total - passed}")
            logging.info(f"Success Rate: {(passed/total)*100:.1f}%")
            
            if passed == total:
                logging.info("🎉 ALL TESTS PASSED! System is ready for Raspberry Pi deployment.")
            else:
                logging.info("⚠️  Some tests failed. Review the results above.")
                
            # Print detailed results
            logging.info("\n📋 DETAILED RESULTS:")
            for test_name, result in self.test_results.items():
                status = "✅" if result["success"] else "❌"
                logging.info(f"  {status} {test_name}: {result['message']}")
                
        except KeyboardInterrupt:
            logging.info("\n🛑 Tests interrupted by user")
        finally:
            self.cleanup_processes()
            logging.info("🧹 Cleanup completed")

def main():
    """Main function"""
    print("🧪 Raspberry Pi Test Suite for Garage Door Monitor")
    print("=" * 60)
    print("This script will test all components to ensure they work")
    print("before deploying to your Raspberry Pi.")
    print()
    print("⚠️  Note: This test requires a camera to be connected.")
    print("   If you don't have a camera, some tests will fail.")
    print()
    
    input("Press Enter to start testing...")
    
    tester = RaspberryPiTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
