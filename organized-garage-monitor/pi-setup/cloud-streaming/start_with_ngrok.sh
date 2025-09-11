#!/bin/bash
# Start stream server with ngrok tunnel

echo "🌐 Starting Garage Door Monitor with ngrok Tunnel"
echo "================================================="
echo

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok is not installed. Run ./ngrok_setup.sh first"
    exit 1
fi

# Check if ngrok is authenticated
if ! ngrok config check &> /dev/null; then
    echo "❌ ngrok is not authenticated. Run: ngrok authtoken YOUR_TOKEN"
    exit 1
fi

# Get local IP
LOCAL_IP=$(hostname -I | awk '{print $1}')
echo "📡 Local IP: $LOCAL_IP"
echo "🔌 Port: 5000"
echo

# Start stream server in background
echo "🚀 Starting stream server..."
python3 stream_server.py &
STREAM_PID=$!

# Wait for stream server to start
sleep 3

# Start ngrok tunnel
echo "🌐 Starting ngrok tunnel..."
ngrok http 5000 &
NGROK_PID=$!

# Wait for ngrok to start
sleep 5

# Get ngrok URL
echo "🔍 Getting ngrok URL..."
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | python3 -c "
import sys, json
data = json.load(sys.stdin)
for tunnel in data['tunnels']:
    if tunnel['proto'] == 'https':
        print(tunnel['public_url'])
        break
")

if [ -n "$NGROK_URL" ]; then
    echo "✅ ngrok tunnel active!"
    echo "   Public URL: $NGROK_URL"
    echo "   Stream URL: $NGROK_URL/video_feed"
    echo
    echo "📱 Use this URL in your cloud-hosted website:"
    echo "   $NGROK_URL/video_feed"
    echo
    echo "🌐 Web Interface: $NGROK_URL"
else
    echo "❌ Failed to get ngrok URL"
fi

echo
echo "🛑 Press Ctrl+C to stop both services"
echo

# Function to cleanup on exit
cleanup() {
    echo
    echo "🛑 Stopping services..."
    kill $STREAM_PID 2>/dev/null
    kill $NGROK_PID 2>/dev/null
    echo "✅ Services stopped"
    exit 0
}

# Set trap to cleanup on exit
trap cleanup SIGINT SIGTERM

# Wait for user to stop
wait
