#!/bin/bash
# Setup script for cloud streaming with tunneling options

echo "🌐 Garage Door Monitor - Cloud Streaming Setup"
echo "=============================================="
echo

# Get local IP
LOCAL_IP=$(hostname -I | awk '{print $1}')
echo "📡 Local IP: $LOCAL_IP"
echo "🔌 Stream Port: 5000"
echo

echo "🔧 Choose your tunneling method:"
echo "1) ngrok (Free, easy setup)"
echo "2) Cloudflare Tunnel (Free, more secure)"
echo "3) Manual port forwarding (Router setup)"
echo "4) Skip tunneling (Local access only)"
echo

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo "📦 Setting up ngrok..."
        echo "1. Install ngrok: https://ngrok.com/download"
        echo "2. Sign up for free account"
        echo "3. Get your auth token"
        echo "4. Run: ngrok authtoken YOUR_TOKEN"
        echo "5. Run: ngrok http 5000"
        echo
        echo "Your public URL will be shown in ngrok output"
        echo "Use this URL in your cloud-hosted website"
        ;;
    2)
        echo "☁️ Setting up Cloudflare Tunnel..."
        echo "1. Install cloudflared: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/"
        echo "2. Run: cloudflared tunnel login"
        echo "3. Run: cloudflared tunnel create garage-monitor"
        echo "4. Run: cloudflared tunnel route dns garage-monitor your-domain.com"
        echo "5. Run: cloudflared tunnel run garage-monitor"
        echo
        echo "Your tunnel will be available at your-domain.com"
        ;;
    3)
        echo "🔧 Manual Port Forwarding Setup:"
        echo "1. Access your router admin panel"
        echo "2. Find 'Port Forwarding' or 'Virtual Server'"
        echo "3. Add rule: External Port 5000 -> Internal IP $LOCAL_IP:5000"
        echo "4. Save and restart router"
        echo
        echo "Your stream will be available at: http://YOUR_PUBLIC_IP:5000"
        echo "Find your public IP at: https://whatismyipaddress.com/"
        ;;
    4)
        echo "🏠 Local access only"
        echo "Stream will be available at: http://$LOCAL_IP:5000"
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo
echo "🚀 To start the stream server:"
echo "   python3 stream_server.py"
echo
echo "📱 Test your stream:"
echo "   http://$LOCAL_IP:5000"
echo
echo "✅ Setup complete!"
