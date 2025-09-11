#!/bin/bash
# ngrok setup script for easy tunneling

echo "🌐 ngrok Setup for Garage Door Monitor"
echo "======================================"
echo

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "📦 ngrok is not installed. Installing..."
    
    # Detect architecture
    ARCH=$(uname -m)
    if [ "$ARCH" = "armv7l" ] || [ "$ARCH" = "aarch64" ]; then
        echo "🔧 Detected ARM architecture (Raspberry Pi)"
        # Download ngrok for ARM
        wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-arm.tgz
        tar xvzf ngrok-v3-stable-linux-arm.tgz
        sudo mv ngrok /usr/local/bin/
        rm ngrok-v3-stable-linux-arm.tgz
    else
        echo "🔧 Detected x86 architecture"
        # Download ngrok for x86
        wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-386.tgz
        tar xvzf ngrok-v3-stable-linux-386.tgz
        sudo mv ngrok /usr/local/bin/
        rm ngrok-v3-stable-linux-386.tgz
    fi
    
    echo "✅ ngrok installed successfully"
else
    echo "✅ ngrok is already installed"
fi

echo
echo "🔑 To complete setup:"
echo "1. Sign up for free account at: https://ngrok.com/"
echo "2. Get your auth token from: https://dashboard.ngrok.com/get-started/your-authtoken"
echo "3. Run: ngrok authtoken YOUR_TOKEN"
echo "4. Run: ngrok http 5000"
echo
echo "📱 Your public URL will be shown in ngrok output"
echo "   Use this URL in your cloud-hosted website"
echo
echo "🚀 To start both stream server and ngrok:"
echo "   ./start_with_ngrok.sh"
