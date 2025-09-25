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

### Method 2: Docker (Recommended)

#### Quick Start with Docker
```bash
# 1. Build the image
docker build -t iptv-browser .

# 2. Run with config file
docker run -d \
  --name iptv-browser \
  --restart unless-stopped \
  -p 5000:5000 \
  -v $(pwd)/downloads:/app/downloads \
  -v $(pwd)/config.py:/app/config.py \
  iptv-browser:latest

# 3. Access at http://localhost:5000
```

#### Alternative: Run with Environment Variables
```bash
docker run -d \
  --name iptv-browser \
  --restart unless-stopped \
  -p 5000:5000 \
  -e BASE_URL="http://your-provider.com:8080/" \
  -e USERNAME="your_username" \
  -e PASSWORD="your_password" \
  -v $(pwd)/downloads:/app/downloads \
  iptv-browser:latest
```

#### Docker Management Commands

**Basic Operations:**
```bash
# View containers and logs
docker ps
docker logs iptv-browser

# Stop/start/restart
docker stop iptv-browser
docker start iptv-browser
docker restart iptv-browser
```

**Image Sharing (Cross-Platform):**
```bash
# Export image
docker save iptv-browser:latest -o iptv-browser.tar

# Import image
docker load -i iptv-browser.tar
```

## 🐳 Docker Image Creation & Management on Windows

### Prerequisites for Windows
- **Docker Desktop**: Install Docker Desktop for Windows
- **WSL2**: Enable Windows Subsystem for Linux 2 (recommended)
- **PowerShell**: Use PowerShell or Command Prompt as administrator

### Building Docker Image on Windows

#### Method 1: Using PowerShell
```powershell
# Navigate to project directory
cd C:\path\to\iptv-browser

# Build the Docker image
docker build -t iptv-browser:latest .

# Verify image was created
docker images | findstr iptv-browser
```

#### Method 2: Using Command Prompt
```cmd
# Navigate to project directory
cd C:\path\to\iptv-browser

# Build the Docker image
docker build -t iptv-browser:latest .

# List all images
docker images
```

### Saving Docker Images on Windows

#### Save Image to TAR File
```powershell
# Save to current directory
docker save iptv-browser:latest -o iptv-browser-latest.tar

# Save to specific location
docker save iptv-browser:latest -o "C:\Docker-Images\iptv-browser-latest.tar"

# Save with compression (using 7-Zip if installed)
docker save iptv-browser:latest | 7z a -si "C:\Docker-Images\iptv-browser-latest.tar.7z"
```

#### Save Multiple Tags
```powershell
# Save multiple versions
docker save iptv-browser:latest iptv-browser:v1.0 -o "C:\Docker-Images\iptv-browser-all-versions.tar"
```

### Loading Docker Images on Windows

#### Load from TAR File
```powershell
# Load from current directory
docker load -i iptv-browser-latest.tar

# Load from specific location
docker load -i "C:\Docker-Images\iptv-browser-latest.tar"

# Verify loaded image
docker images | findstr iptv-browser
```

### Windows-Specific Docker Commands

#### Using Windows Paths in Docker
```powershell
# Mount Windows directories (PowerShell)
docker run -d `
  --name iptv-browser `
  -p 5000:5000 `
  -v "C:\IPTV-Downloads:/app/downloads" `
  -v "C:\IPTV-Config\config.py:/app/config.py" `
  iptv-browser:latest

# Using Command Prompt (escape quotes)
docker run -d ^
  --name iptv-browser ^
  -p 5000:5000 ^
  -v "C:\IPTV-Downloads:/app/downloads" ^
  -v "C:\IPTV-Config\config.py:/app/config.py" ^
  iptv-browser:latest
```

#### Windows Docker Desktop GUI
1. **Open Docker Desktop**
2. **Go to Images tab**
3. **Click on your image**
4. **Use "Save" button to export**
5. **Choose destination folder**

### Advanced Windows Docker Management

#### Create Batch Scripts for Easy Management

**build-image.bat:**
```batch
@echo off
echo Building IPTV Browser Docker Image...
cd /d "%~dp0"
docker build -t iptv-browser:latest .
if %ERRORLEVEL% EQU 0 (
    echo Build completed successfully!
    docker images | findstr iptv-browser
) else (
    echo Build failed!
)
pause
```

**save-image.bat:**
```batch
@echo off
set IMAGE_NAME=iptv-browser:latest
set SAVE_PATH=C:\Docker-Images
set FILENAME=iptv-browser-%date:~-4,4%%date:~-10,2%%date:~-7,2%.tar

echo Saving Docker image %IMAGE_NAME%...
if not exist "%SAVE_PATH%" mkdir "%SAVE_PATH%"
docker save %IMAGE_NAME% -o "%SAVE_PATH%\%FILENAME%"

if %ERRORLEVEL% EQU 0 (
    echo Image saved successfully to: %SAVE_PATH%\%FILENAME%
    dir "%SAVE_PATH%\%FILENAME%"
) else (
    echo Failed to save image!
)
pause
```

**load-image.bat:**
```batch
@echo off
set /p IMAGE_PATH="Enter full path to TAR file: "
echo Loading Docker image from %IMAGE_PATH%...
docker load -i "%IMAGE_PATH%"

if %ERRORLEVEL% EQU 0 (
    echo Image loaded successfully!
    docker images
) else (
    echo Failed to load image!
)
pause
```

#### PowerShell Scripts for Advanced Users

**Build-IPTVImage.ps1:**
```powershell
param(
    [string]$Tag = "latest",
    [string]$ImageName = "iptv-browser"
)

Write-Host "Building Docker image: $ImageName:$Tag" -ForegroundColor Green

try {
    docker build -t "$ImageName:$Tag" .
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Build completed successfully!" -ForegroundColor Green
        docker images | Select-String $ImageName
    } else {
        Write-Host "❌ Build failed!" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}
```

**Save-IPTVImage.ps1:**
```powershell
param(
    [string]$ImageName = "iptv-browser:latest",
    [string]$SavePath = "C:\Docker-Images",
    [switch]$Compress
)

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$filename = "iptv-browser-$timestamp.tar"
$fullPath = Join-Path $SavePath $filename

# Create directory if it doesn't exist
if (!(Test-Path $SavePath)) {
    New-Item -ItemType Directory -Path $SavePath -Force
    Write-Host "Created directory: $SavePath" -ForegroundColor Yellow
}

Write-Host "Saving Docker image: $ImageName" -ForegroundColor Green
Write-Host "Destination: $fullPath" -ForegroundColor Cyan

try {
    docker save $ImageName -o $fullPath
    
    if ($LASTEXITCODE -eq 0) {
        $fileInfo = Get-Item $fullPath
        Write-Host "✅ Image saved successfully!" -ForegroundColor Green
        Write-Host "File size: $([math]::Round($fileInfo.Length / 1MB, 2)) MB" -ForegroundColor Cyan
        
        if ($Compress) {
            Write-Host "Compressing with 7-Zip..." -ForegroundColor Yellow
            & 7z a "$fullPath.7z" $fullPath
            Remove-Item $fullPath
            Write-Host "✅ Compressed file created: $fullPath.7z" -ForegroundColor Green
        }
    } else {
        Write-Host "❌ Failed to save image!" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}
```

### Windows Docker Troubleshooting

#### Common Windows Issues

**1. Path Issues:**
```powershell
# Use forward slashes or escape backslashes
docker run -v "C:/IPTV-Downloads:/app/downloads" iptv-browser:latest
# OR
docker run -v "C:\\IPTV-Downloads:/app/downloads" iptv-browser:latest
```

**2. Permission Issues:**
```powershell
# Run PowerShell as Administrator
# Enable Docker Desktop integration with WSL2
# Check Docker Desktop settings
```

**3. WSL2 Integration:**
```powershell
# Enable WSL2 in Docker Desktop settings
# Restart Docker Desktop
# Verify WSL2 backend is active
docker version
```

#### Windows Performance Tips

**1. Use WSL2 Backend:**
- Better performance than Hyper-V
- Native Linux compatibility
- Faster file system operations

**2. Optimize Docker Desktop:**
```json
// Docker Desktop settings
{
  "memoryMiB": 4096,
  "cpus": 4,
  "swapMiB": 1024,
  "diskSizeMiB": 61440
}
```

**3. Use Windows Container Mode (if needed):**
```powershell
# Switch to Windows containers (for Windows-specific apps)
& "C:\Program Files\Docker\Docker\DockerCli.exe" -SwitchWindowsEngine

# Switch back to Linux containers
& "C:\Program Files\Docker\Docker\DockerCli.exe" -SwitchLinuxEngine
```

### Method 3: Docker Compose (Easiest)

#### Quick Start
```bash
# 1. Start the application
docker-compose up -d

# 2. View logs
docker-compose logs -f

# 3. Stop when done
docker-compose down
```

#### Using Environment Variables
Edit `docker-compose.env.yml` with your IPTV credentials, then:
```bash
docker-compose -f docker-compose.env.yml up -d
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