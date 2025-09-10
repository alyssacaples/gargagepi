# 🚗 Garage Door Monitor

A Raspberry Pi-based garage door monitoring system with live camera streaming and photo capture capabilities.

## Features

- 📹 Live camera streaming via web interface
- 📸 Photo capture functionality
- 🌐 Web-based interface accessible from any device on your network
- 🔄 Automatic startup on boot
- 📊 System status monitoring
- 📅 Scheduled photo capture (optional)

## Hardware Requirements

- Raspberry Pi (3B+ or newer recommended)
- USB webcam
- MicroSD card (16GB+ recommended)
- Power supply for Raspberry Pi

## Quick Start

### 1. Clone the Repository

On your Raspberry Pi:

```bash
git clone <YOUR_REPO_URL>
cd garage-pi
```

### 2. Deploy

Run the deployment script:

```bash
chmod +x deploy.sh
./deploy.sh
```

This script will:
- Update system packages
- Install Python dependencies
- Create a virtual environment
- Install required packages
- Set up the systemd service for auto-start
- Configure the camera

### 3. Test the Installation

```bash
# Activate virtual environment
source venv/bin/activate

# Test the application
python3 app.py
```

### 4. Start the Service

```bash
# Start the service
sudo systemctl start garage-monitor

# Check status
sudo systemctl status garage-monitor

# View logs
sudo journalctl -u garage-monitor -f
```

## Accessing the Web Interface

Once running, access the web interface at:
- **Main interface**: `http://[YOUR_PI_IP]:5000`
- **Live stream**: `http://[YOUR_PI_IP]:5000/stream`
- **Status API**: `http://[YOUR_PI_IP]:5000/status`
- **Capture photo**: `http://[YOUR_PI_IP]:5000/capture`

The application will automatically detect and display your Pi's IP address when it starts. You can also find it manually:
```bash
hostname -I
```

## Project Structure

```
garage-pi/
├── app.py                 # Main Flask web server
├── photo_scheduler.py     # Scheduled photo capture
├── check_system.py        # System health monitoring
├── start_monitor.py       # Alternative startup script
├── deploy.sh             # Deployment script for Pi
├── setup.sh              # Original setup script
├── requirements.txt      # Python dependencies
├── templates/
│   └── index.html        # Web interface template
└── photos/               # Captured photos (created on first run)
```

## API Endpoints

- `GET /` - Main web interface
- `GET /stream` - Live camera stream (MJPEG)
- `GET /capture` - Capture a single photo
- `GET /status` - System status information

## Service Management

The application runs as a systemd service for automatic startup and management:

```bash
# Start service
sudo systemctl start garage-monitor

# Stop service
sudo systemctl stop garage-monitor

# Restart service
sudo systemctl restart garage-monitor

# Check status
sudo systemctl status garage-monitor

# View logs
sudo journalctl -u garage-monitor -f

# Disable auto-start
sudo systemctl disable garage-monitor

# Enable auto-start
sudo systemctl enable garage-monitor
```

## Troubleshooting

### Camera Issues

1. **Camera not detected**:
   ```bash
   # List available cameras
   ls /dev/video*
   
   # Test camera with v4l2
   v4l2-ctl --list-devices
   ```

2. **Permission issues**:
   ```bash
   # Add user to video group
   sudo usermod -a -G video pi
   ```

### Network Issues

1. **Can't access web interface**:
   - The IP address is automatically displayed when the service starts
   - You can also check Pi's IP: `hostname -I`
   - Ensure firewall allows port 5000
   - Verify service is running: `sudo systemctl status garage-monitor`

### Service Issues

1. **Service won't start**:
   ```bash
   # Check logs
   sudo journalctl -u garage-monitor -n 50
   
   # Test manually
   source venv/bin/activate
   python3 app.py
   ```

## Development

### Local Development

1. Clone the repository
2. Create virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python3 app.py
   ```

### Updating the Pi

To update your Pi with new changes:

```bash
# On the Pi
cd garage-pi
git pull
sudo systemctl restart garage-monitor
```

## Configuration

The application uses default settings that work for most setups:

- **Port**: 5000
- **Host**: 0.0.0.0 (accessible from network)
- **Camera**: Auto-detects first available USB camera
- **Photo storage**: `./photos/` directory

## Security Notes

- The web interface is accessible from any device on your network
- No authentication is implemented (suitable for trusted home networks)
- Consider adding authentication for production use

## License

This project is open source. Feel free to modify and distribute.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs: `sudo journalctl -u garage-monitor -f`
3. Test camera manually: `python3 app.py`
4. Open an issue on the repository
