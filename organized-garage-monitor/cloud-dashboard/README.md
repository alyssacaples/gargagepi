# Cloud-Side Files for Garage Door Monitor

This folder contains the files for your cloud-hosted website that will display your Raspberry Pi camera stream.

## Files

- **`index.html`** - Main dashboard for remote access
- **`README.md`** - This file

## Deployment Options

### 1. GitHub Pages (Free)
1. Create a new GitHub repository
2. Upload `index.html` to the repository
3. Enable GitHub Pages in repository settings
4. Your site will be available at `https://yourusername.github.io/repository-name`

### 2. Netlify (Free)
1. Go to [netlify.com](https://netlify.com)
2. Drag and drop the `index.html` file
3. Your site will be available at a custom URL
4. You can add a custom domain if desired

### 3. Vercel (Free)
1. Go to [vercel.com](https://vercel.com)
2. Import your project or drag and drop files
3. Deploy automatically
4. Your site will be available at a custom URL

### 4. Any Web Hosting Service
- Upload `index.html` to your web hosting service
- Ensure it's accessible via HTTPS
- Update the stream URL in the dashboard

## Configuration

1. **Deploy the HTML file** to your chosen hosting service
2. **Access your dashboard** via the provided URL
3. **Configure the stream URL** in the dashboard:
   - Local network: `http://YOUR_PI_IP:5000/video_feed`
   - ngrok tunnel: `https://abc123.ngrok.io/video_feed`
   - Cloudflare tunnel: `https://your-domain.com/video_feed`

## Features

- ✅ **Real-time stream display**
- ✅ **Status monitoring**
- ✅ **Photo capture**
- ✅ **Mobile responsive**
- ✅ **Auto-refresh**
- ✅ **Connection status**
- ✅ **Uptime tracking**

## Security Considerations

- Use HTTPS for all connections
- Consider adding authentication if needed
- Use strong passwords for tunnel services
- Regularly update your Pi's software
- Monitor access logs

## Troubleshooting

- **Stream not loading**: Check if your Pi is online and accessible
- **Connection errors**: Verify the stream URL is correct
- **Slow loading**: Check your internet connection and Pi's performance
- **Authentication issues**: Ensure your tunnel service is properly configured
