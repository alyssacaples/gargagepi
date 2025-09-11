#!/bin/bash
# Start script for the stream server

echo "🌐 Starting Garage Door Monitor Stream Server"
echo "=============================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

# Check if required packages are installed
echo "📦 Checking dependencies..."
python3 -c "import flask, cv2" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Missing dependencies. Installing..."
    pip3 install -r requirements.txt
fi

# Get local IP
LOCAL_IP=$(hostname -I | awk '{print $1}')
echo "📡 Local IP: $LOCAL_IP"
echo "🔌 Port: 5000"
echo

# Start the stream server
echo "🚀 Starting stream server..."
echo "   Stream URL: http://$LOCAL_IP:5000/video_feed"
echo "   Web Interface: http://$LOCAL_IP:5000/"
echo
echo "🛑 Press Ctrl+C to stop"
echo

python3 stream_server.py
