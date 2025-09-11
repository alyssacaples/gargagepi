# Cloud Streaming Setup for Garage Door Monitor

This folder contains the new cloud-hosted approach for accessing your Raspberry Pi camera stream remotely.

## Architecture Overview

```
Raspberry Pi (Local)          Cloud Hosting (Remote)
┌─────────────────┐          ┌─────────────────────┐
│ Camera Stream   │          │ Website with        │
│ Port 5000       │ ────────▶│ Embedded Stream     │
│                 │          │                     │
│ ngrok/Cloudflare│          │ Public URL          │
│ Tunnel          │          │                     │
└─────────────────┘          └─────────────────────┘
```

## Folder Structure

- **`pi-side/`** - Files to run on your Raspberry Pi
- **`cloud-side/`** - Files for your cloud-hosted website

## Setup Steps

### 1. Raspberry Pi Side
1. Copy files from `pi-side/` to your Raspberry Pi
2. Install required dependencies
3. Set up port forwarding or tunnel (ngrok/Cloudflare)
4. Start the streaming service

### 2. Cloud Side
1. Deploy files from `cloud-side/` to your cloud hosting
2. Configure the public stream URL
3. Access your camera stream from anywhere

## Benefits

- ✅ **Remote Access**: View your garage from anywhere
- ✅ **No VPN Required**: Direct web access
- ✅ **Scalable**: Easy to add multiple cameras
- ✅ **Secure**: Use HTTPS and authentication
- ✅ **Mobile Friendly**: Works on phones/tablets

## Security Considerations

- Use HTTPS for all connections
- Implement authentication if needed
- Consider IP whitelisting
- Use strong passwords for tunnel services
- Regularly update dependencies

## Troubleshooting

- Check port forwarding configuration
- Verify tunnel service is running
- Test local stream first
- Check firewall settings
- Monitor bandwidth usage
