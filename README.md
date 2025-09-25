# 📺🎬 IPTV Browser

A comprehensive web-based application built with Flask that allows you to browse, search, and download both **TV Series** and **Movies** from IPTV providers. Features a modern, responsive interface with advanced search capabilities, real-time progress tracking, and intelligent caching.

## ✨ Features

### 🎯 Core Functionality
- **📱 Responsive Design**: Works perfectly on desktop, tablet, and mobile devices
- **🌓 Dark/Light Mode**: Toggle between themes with persistent preference
- **🔍 Advanced Search**: Search across both series and movies with content type filtering
- **📊 Smart Caching**: Selective caching with detailed progress tracking
- **⚡ Real-time Progress**: Live download progress with speed, ETA, and file size info
- **🎭 Content Types**: Full support for both TV Series and Movies

### 🎬 Movie Features
- **🎪 Movie Categories**: Browse movies by genre and category
- **🎯 Movie Details**: View plot, cast, director, genre, rating, and release date
- **📥 Movie Downloads**: Direct movie downloads with progress tracking
- **🔎 Movie Search**: Search by title, actors, plot, or genre

### 📺 TV Series Features
- **📚 Series Categories**: Organized series browsing by category
- **🎭 Series Information**: Detailed series info with cast and plot
- **📋 Episode Management**: Select specific seasons and episode ranges
- **⬇️ Batch Downloads**: Download multiple episodes with progress tracking

### 🚀 Advanced Features
- **💾 Dual Caching System**: Separate caches for series and movies
- **📈 Statistics Dashboard**: View cached content statistics on main page
- **🔄 Smart Navigation**: Intelligent back buttons that preserve search context
- **🎚️ Pagination Controls**: Customizable items per page (10-100)
- **📊 Progress Analytics**: Detailed download statistics and completion rates

## 📋 Requirements

### System Requirements
- **Python**: 3.8 or higher
- **RAM**: Minimum 512MB, Recommended 1GB+
- **Storage**: 100MB for application + space for downloads
- **Network**: Stable internet connection for IPTV API access

### Dependencies
```bash
Flask>=2.3.0
requests>=2.31.0
urllib3>=2.0.0
tqdm>=4.65.0
aiohttp>=3.8.0
```

### IPTV Provider
- Valid IPTV subscription with API access
- API endpoints for:
  - Series categories (`get_series_categories`)
  - Movie categories (`get_vod_categories`) 
  - Series streams (`get_series`)
  - Movie streams (`get_vod_streams`)
  - Content info (`get_series_info`, `get_vod_info`)

## 🚀 Quick Start

### Method 1: Python Script (Recommended for Development)

#### 1. Clone the Repository
```bash
git clone <repository-url>
cd iptv-browser
```

#### 2. Install Dependencies
```bash
# Using pip
pip install -r requirements.txt

# Or install manually
pip install Flask requests urllib3 tqdm aiohttp
```

#### 3. Configure IPTV Settings
Create or edit `config.py`:
```python
BASE_URL = "http://your-iptv-provider.com:8080/"  # Include trailing slash
USERNAME = "your_username"
PASSWORD = "your_password"
```

#### 4. Run the Application
```bash
# Standard Python execution
python app.py

# Or using Flask CLI
flask run --host=0.0.0.0 --port=5000

# Windows batch file (if available)
run_app.bat
```

#### 5. Access the Application
Open your browser and navigate to:
- **Local**: `http://localhost:5000`
- **Network**: `http://your-ip:5000` (accessible from other devices)

### Method 2: Docker (Recommended for Production)

#### 1. Create Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create downloads directory
RUN mkdir -p downloads

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# Run application
CMD ["python", "app.py"]
```

#### 2. Create requirements.txt
```txt
Flask>=2.3.0
requests>=2.31.0
urllib3>=2.0.0
tqdm>=4.65.0
aiohttp>=3.8.0
```

#### 3. Build Docker Image
```bash
# Build the image
docker build -t iptv-browser:latest .

# Build with specific tag
docker build -t iptv-browser:v1.0.0 .
```

#### 4. Run Docker Container
```bash
# Basic run
docker run -d \
  --name iptv-browser \
  -p 5000:5000 \
  -v $(pwd)/downloads:/app/downloads \
  -v $(pwd)/config.py:/app/config.py \
  iptv-browser:latest

# Run with environment variables
docker run -d \
  --name iptv-browser \
  -p 5000:5000 \
  -e BASE_URL="http://your-provider.com:8080/" \
  -e USERNAME="your_username" \
  -e PASSWORD="your_password" \
  -v $(pwd)/downloads:/app/downloads \
  iptv-browser:latest

# Run with restart policy
docker run -d \
  --name iptv-browser \
  --restart unless-stopped \
  -p 5000:5000 \
  -v $(pwd)/downloads:/app/downloads \
  -v $(pwd)/config.py:/app/config.py \
  iptv-browser:latest
```

#### 5. Docker Image Management

##### Export/Import Images

**Linux/macOS:**
```bash
# Export image to compressed file
docker save iptv-browser:latest | gzip > iptv-browser-latest.tar.gz

# Export image to uncompressed file
docker save iptv-browser:latest > iptv-browser-latest.tar

# Import image from compressed file
docker load < iptv-browser-latest.tar.gz

# Import image from uncompressed file
docker load < iptv-browser-latest.tar

# Import and verify the image
gunzip -c iptv-browser-latest.tar.gz | docker load
docker images | grep iptv-browser

# Import from different location
docker load -i /path/to/iptv-browser-latest.tar.gz
```

**Windows (PowerShell):**
```powershell
# Export image to uncompressed file (recommended for Windows)
docker save iptv-browser:latest -o iptv-browser-latest.tar

# Import image from file
docker load -i iptv-browser-latest.tar

# Alternative: Export and compress using PowerShell
docker save iptv-browser:latest | Compress-Archive -DestinationPath iptv-browser-latest.zip

# Import compressed image (extract first)
Expand-Archive -Path iptv-browser-latest.zip -DestinationPath temp
docker load -i temp/iptv-browser-latest.tar

# Verify imported image
docker images | Select-String "iptv-browser"
```

**Windows (Command Prompt):**
```cmd
# Export image to file
docker save iptv-browser:latest -o iptv-browser-latest.tar

# Import image from file
docker load -i iptv-browser-latest.tar

# Verify imported image
docker images | findstr "iptv-browser"
```

**Cross-Platform (Recommended):**
```bash
# Export (works on all platforms)
docker save iptv-browser:latest -o iptv-browser-latest.tar

# Import (works on all platforms)
docker load -i iptv-browser-latest.tar

# List images to verify
docker images iptv-browser
```

##### Registry Operations
```bash
# Push to registry (if you have one)
docker tag iptv-browser:latest your-registry/iptv-browser:latest
docker push your-registry/iptv-browser:latest

# Pull from registry
docker pull your-registry/iptv-browser:latest
```

##### Container Management
```bash
# View running containers
docker ps

# View all containers (including stopped)
docker ps -a

# View logs
docker logs iptv-browser

# Follow logs in real-time
docker logs -f iptv-browser

# Stop container
docker stop iptv-browser

# Start stopped container
docker start iptv-browser

# Restart container
docker restart iptv-browser

# Remove container
docker rm iptv-browser

# Remove container forcefully
docker rm -f iptv-browser
```

##### Image Management
```bash
# List all images
docker images

# Remove image
docker rmi iptv-browser:latest

# Remove unused images
docker image prune

# Remove all unused images
docker image prune -a

# View image details
docker inspect iptv-browser:latest
```

### 💡 Common Usage Scenarios

#### Scenario 1: Sharing Image Locally (Cross-Platform)
```bash
# On source machine (any OS)
docker save iptv-browser:latest -o iptv-browser-latest.tar

# Transfer file to target machine, then import:
docker load -i iptv-browser-latest.tar

# Verify import
docker images iptv-browser
```

#### Scenario 2: Windows-Specific Sharing with Compression
```powershell
# Export and compress (PowerShell)
docker save iptv-browser:latest -o iptv-browser-latest.tar
Compress-Archive -Path iptv-browser-latest.tar -DestinationPath iptv-browser-latest.zip

# On target Windows machine:
Expand-Archive -Path iptv-browser-latest.zip -DestinationPath .
docker load -i iptv-browser-latest.tar
Remove-Item iptv-browser-latest.tar  # Cleanup
```

#### Scenario 3: Backup and Restore
```bash
# Backup (create backup directory first)
mkdir -p backup
docker save iptv-browser:latest -o backup/iptv-browser-backup.tar

# Restore
docker load -i backup/iptv-browser-backup.tar
```

#### Scenario 4: Offline Deployment
```bash
# Prepare offline package
docker save iptv-browser:latest -o iptv-browser-offline.tar

# Deploy on offline system
docker load -i iptv-browser-offline.tar
docker run -d --name iptv-browser -p 5000:5000 iptv-browser:latest
```

#### Scenario 5: Multiple Image Export/Import
```bash
# Export multiple images
docker save iptv-browser:latest iptv-browser:v1.0.0 -o iptv-browser-multi.tar

# Import multiple images
docker load -i iptv-browser-multi.tar

# List imported images
docker images iptv-browser
```

### Method 3: Docker Compose (Recommended for Easy Management)

#### 1. Choose Your Configuration

**Basic Configuration (docker-compose.yml):**
- Uses config.py file for IPTV settings
- Suitable for development and testing

**Environment Variables (docker-compose.env.yml):**
- Uses environment variables for IPTV settings
- Better for containerized deployments

**Production Ready (docker-compose.prod.yml):**
- Includes resource limits and security options
- Logging configuration and network isolation

#### 2. Run with Docker Compose

**Basic Setup:**
```bash
# Start services (uses docker-compose.yml by default)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

**Using Environment Variables:**
```bash
# Use the environment variables version
docker-compose -f docker-compose.env.yml up -d

# Edit environment variables first
nano docker-compose.env.yml  # Update BASE_URL, USERNAME, PASSWORD

# Then start
docker-compose -f docker-compose.env.yml up -d
```

**Production Deployment:**
```bash
# Use production configuration
docker-compose -f docker-compose.prod.yml up -d

# Monitor with resource limits
docker-compose -f docker-compose.prod.yml logs -f
docker stats iptv-browser
```

#### 3. Docker Compose Management
```bash
# View running services
docker-compose ps

# Scale services (if needed)
docker-compose up -d --scale iptv-browser=2

# Update and restart
docker-compose pull
docker-compose up -d

# Clean up everything
docker-compose down -v --remove-orphans
```

## 🎯 Usage Guide

### Initial Setup
1. **Access Main Page**: Navigate to the application URL
2. **Choose Content Type**: Select "TV Series" or "Movies"
3. **Cache Data**: Go to Search → Caching Management → Select content types → "Process and Cache Data"
4. **Wait for Caching**: Monitor progress with detailed statistics

### Browsing Content
- **Categories**: Browse organized categories with item counts
- **Pagination**: Customize items per page (10-100)
- **Search**: Use advanced search with content type filtering
- **Details**: View comprehensive information before downloading

### Downloading
- **Series**: Select seasons and episode ranges
- **Movies**: Direct download with progress tracking
- **Progress**: Monitor speed, ETA, file size, and completion
- **Management**: Downloads saved to organized folders

## 📁 Project Structure

```
iptv-browser/
├── 📄 app.py                      # Main Flask application
├── 📄 cache_manager.py            # Caching system for series/movies
├── 📄 config.py                   # IPTV provider configuration
├── 📄 requirements.txt            # Python dependencies
├── 📄 Dockerfile                  # Docker container configuration
├── 📄 docker-compose.yml          # Docker Compose setup
├── 📄 run_app.bat                 # Windows batch file
├── 📄 README.md                   # This file
├── 📄 .gitignore                  # Git ignore rules
├── 📁 static/                     # Static assets
│   └── 📄 style.css              # Application styles
├── 📁 templates/                  # HTML templates
│   ├── 📄 base.html              # Base template
│   ├── 📄 main.html              # Main selection page
│   ├── 📄 index.html             # Series categories
│   ├── 📄 movies_index.html      # Movie categories
│   ├── 📄 series.html            # Series listing
│   ├── 📄 movies.html            # Movies listing
│   ├── 📄 download.html          # Series download page
│   ├── 📄 movie_download.html    # Movie download page
│   ├── 📄 search.html            # Search interface
│   └── 📄 error.html             # Error page
├── 📁 downloads/                  # Downloaded content
│   ├── 📁 Series Name - S01/     # Series episodes
│   └── 📁 Movies/                # Movie files
├── 📄 cached_series_data.json    # Series cache file
└── 📄 cached_movies_data.json    # Movies cache file
```

## 🔧 Configuration Options

### Environment Variables
```bash
# IPTV Provider Settings
BASE_URL=http://your-provider.com:8080/
USERNAME=your_username
PASSWORD=your_password

# Application Settings
FLASK_ENV=production
FLASK_DEBUG=false
```

### Advanced Configuration
Edit `config.py` for advanced settings:
```python
# API Configuration
BASE_URL = "http://your-provider.com:8080/"
USERNAME = "your_username"
PASSWORD = "your_password"

# Download Settings
DOWNLOADS_DIR = "downloads"
MAX_CONCURRENT_DOWNLOADS = 3
CHUNK_SIZE = 8192

# Cache Settings
CACHE_EXPIRY_HOURS = 24
AUTO_CACHE_ON_STARTUP = False
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. Connection Errors
```bash
# Check IPTV provider connectivity
curl "http://your-provider.com:8080/player_api.php?username=USER&password=PASS&action=get_series_categories"
```

#### 2. Permission Issues
```bash
# Fix download directory permissions
chmod 755 downloads/
chown -R $USER:$USER downloads/
```

#### 3. Port Already in Use
```bash
# Find process using port 5000
lsof -i :5000
# Kill process
kill -9 <PID>
# Or use different port
python app.py --port 5001
```

#### 4. Docker Issues
```bash
# Check container logs
docker logs iptv-browser

# Restart container
docker restart iptv-browser

# Rebuild image
docker-compose down
docker-compose up -d --build
```

### Performance Optimization

#### 1. Caching Strategy
- Cache during off-peak hours
- Use selective caching (series OR movies)
- Monitor cache file sizes
- Regular cache updates

#### 2. Download Optimization
- Limit concurrent downloads
- Use appropriate chunk sizes
- Monitor disk space
- Organize download folders

#### 3. System Resources
```bash
# Monitor system resources
htop
df -h
free -h

# Docker resource monitoring
docker stats iptv-browser
```

## 🔒 Security Considerations

### 1. Configuration Security
- Never commit `config.py` with real credentials
- Use environment variables in production
- Rotate credentials regularly
- Use strong passwords

### 2. Network Security
- Use HTTPS when possible
- Implement rate limiting
- Monitor API usage
- Use VPN if required

### 3. File System Security
```bash
# Secure download directory
chmod 750 downloads/
# Secure config file
chmod 600 config.py
```

## 📊 Monitoring & Logging

### Application Logs
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Docker Logs
```bash
# View real-time logs
docker logs -f iptv-browser

# Export logs
docker logs iptv-browser > app.log 2>&1
```

### Performance Metrics
- Monitor cache hit rates
- Track download speeds
- Monitor API response times
- Check error rates

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This application is for educational and personal use only. Users are responsible for ensuring they have proper rights and permissions to access and download content from their IPTV providers. The developers are not responsible for any misuse of this software.

## 🆘 Support

- **Issues**: Report bugs via GitHub Issues
- **Documentation**: Check this README and code comments
- **Community**: Join discussions in GitHub Discussions

---

**Made with ❤️ for IPTV enthusiasts**