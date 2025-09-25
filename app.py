from flask import Flask, render_template, request, jsonify, session, redirect, url_for, Response
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import os
import time
import logging
from tqdm import tqdm
import asyncio
import aiohttp
import threading
from queue import Queue, Empty
import json
from flask import Response, stream_with_context, Flask, request, jsonify, render_template
from cache_manager import (
    process_and_cache_series_data, process_and_cache_movies_data,
    search_series, search_movies, search_all_content,
    get_cached_data, get_series_count_by_category, get_movies_count_by_category
)
import config
from config import BASE_URL, USERNAME, PASSWORD

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.secret_key = 'your-secret-key'

# Add JSON filter for Jinja2 templates
import json
def tojsonfilter(obj):
    return json.dumps(obj)

app.jinja_env.filters['tojsonfilter'] = tojsonfilter

# Context processor to make current user available in all templates
@app.context_processor
def inject_user():
    return dict(current_user=get_current_user())


DOWNLOADS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads')

# Configure session for requests with more robust settings
session = requests.Session()
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "POST"],
    raise_on_redirect=True,
    raise_on_status=True
)

adapter = HTTPAdapter(
    max_retries=retry_strategy,
    pool_connections=10,
    pool_maxsize=10
)
session.mount("http://", adapter)
session.mount("https://", adapter)
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
})

# Authentication helper functions
def get_current_user():
    """Get current user configuration."""
    if config.CURRENT_USER and config.CURRENT_USER in config.USERS:
        return config.USERS[config.CURRENT_USER]
    return None

def is_user_authenticated():
    """Check if current user is authenticated."""
    user = get_current_user()
    return user and user.get('user_info', {}).get('auth') == 1

def test_connection(server, username, password):
    """Test API connectivity and return user info."""
    try:
        # Ensure server URL ends with /
        if not server.endswith('/'):
            server += '/'
            
        url = f"{server}player_api.php"
        params = {
            "username": username,
            "password": password
        }
        
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Check if authentication was successful
        user_info = data.get('user_info', {})
        if user_info.get('auth') == 1:
            return {'success': True, 'data': data}
        else:
            return {'success': False, 'error': 'Invalid username or password'}
            
    except requests.exceptions.Timeout:
        return {'success': False, 'error': 'Connection timeout. Please check your connection.'}
    except requests.exceptions.ConnectionError:
        return {'success': False, 'error': 'Server is not responding. Please check the server URL.'}
    except requests.exceptions.RequestException as e:
        return {'success': False, 'error': f'Network error: {str(e)}'}
    except ValueError:
        return {'success': False, 'error': 'Invalid response from server'}
    except Exception as e:
        return {'success': False, 'error': f'Unexpected error: {str(e)}'}

def save_user_to_config(user_id, server, username, password, user_info=None, server_info=None):
    """Save user configuration to config.py file."""
    try:
        # Create new user entry
        new_user = {
            "id": user_id,
            "server": server,
            "username": username,
            "password": password,
            "user_info": user_info or {},
            "server_info": server_info or {}
        }
        
        # Update the USERS dictionary in memory
        config.USERS[user_id] = new_user
        
        # If this is the first user or no current user is set, make it current
        if not config.CURRENT_USER:
            config.CURRENT_USER = user_id
            # Update legacy variables
            config.BASE_URL = server
            config.USERNAME = username
            config.PASSWORD = password
        
        # Write updated config back to file
        users_str = "USERS = {\n"
        for uid, user_data in config.USERS.items():
            users_str += f'    "{uid}": {{\n'
            users_str += f'        "id": "{user_data["id"]}",\n'
            users_str += f'        "server": "{user_data["server"]}",\n'
            users_str += f'        "username": "{user_data["username"]}",\n'
            users_str += f'        "password": "{user_data["password"]}",\n'
            users_str += f'        "user_info": {user_data["user_info"]},\n'
            users_str += f'        "server_info": {user_data["server_info"]}\n'
            users_str += '    },\n'
        users_str += "}\n\n"
        
        current_user_str = f'CURRENT_USER = "{config.CURRENT_USER}"\n\n' if config.CURRENT_USER else 'CURRENT_USER = None\n\n'
        
        # Keep the rest of the config.py content (helper functions)
        helper_functions = '''# Legacy support (points to current user's config)
def get_current_config():
    if CURRENT_USER and CURRENT_USER in USERS:
        user = USERS[CURRENT_USER]
        return {
            'BASE_URL': user['server'],
            'USERNAME': user['username'], 
            'PASSWORD': user['password']
        }
    return {'BASE_URL': '', 'USERNAME': '', 'PASSWORD': ''}

# For backward compatibility - these will be updated dynamically
BASE_URL = ""
USERNAME = ""
PASSWORD = ""'''
        
        new_content = "# Multi-user configuration\n" + users_str + current_user_str + helper_functions
        
        with open('config.py', 'w') as f:
            f.write(new_content)
            
        return True
        
    except Exception as e:
        logger.error(f"Error saving user to config: {str(e)}")
        return False

def switch_user(user_id):
    """Switch to different user and update config.py."""
    if user_id in config.USERS:
        try:
            config.CURRENT_USER = user_id
            
            # Update legacy variables
            user = config.USERS[user_id]
            config.BASE_URL = user['server']
            config.USERNAME = user['username']
            config.PASSWORD = user['password']
            
            # Update the config file
            users_str = "USERS = {\n"
            for uid, user_data in config.USERS.items():
                users_str += f'    "{uid}": {{\n'
                users_str += f'        "id": "{user_data["id"]}",\n'
                users_str += f'        "server": "{user_data["server"]}",\n'
                users_str += f'        "username": "{user_data["username"]}",\n'
                users_str += f'        "password": "{user_data["password"]}",\n'
                users_str += f'        "user_info": {user_data["user_info"]},\n'
                users_str += f'        "server_info": {user_data["server_info"]}\n'
                users_str += '    },\n'
            users_str += "}\n\n"
            
            current_user_str = f'CURRENT_USER = "{config.CURRENT_USER}"\n\n'
            
            helper_functions = '''# Legacy support (points to current user's config)
def get_current_config():
    if CURRENT_USER and CURRENT_USER in USERS:
        user = USERS[CURRENT_USER]
        return {
            'BASE_URL': user['server'],
            'USERNAME': user['username'], 
            'PASSWORD': user['password']
        }
    return {'BASE_URL': '', 'USERNAME': '', 'PASSWORD': ''}

# For backward compatibility - these will be updated dynamically
BASE_URL = ""
USERNAME = ""
PASSWORD = ""'''
            
            new_content = "# Multi-user configuration\n" + users_str + current_user_str + helper_functions
            
            with open('config.py', 'w') as f:
                f.write(new_content)
            
            return True
        except Exception as e:
            logger.error(f"Error switching user: {str(e)}")
            return False
    return False

def get_categories():
    """Fetch all series categories with improved error handling"""
    user = get_current_user()
    if not user:
        logger.error("No current user configured")
        return []
        
    # Ensure server URL has trailing slash
    server_url = user['server'].rstrip('/') + '/'
    url = f"{server_url}player_api.php"
    params = {
        "username": user['username'],
        "password": user['password'],
        "action": "get_series_categories"
    }
    
    try:
        logger.debug(f"Fetching categories from: {url}")
        response = session.get(url, params=params, timeout=(5, 15))
        response.raise_for_status()
        categories = response.json()
        logger.debug(f"Retrieved {len(categories)} categories")
        return categories
    except requests.exceptions.Timeout:
        logger.error("Request timed out while fetching categories")
        return []
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return []

def get_series_by_category(category_id):
    """Fetch all series in a category"""
    user = get_current_user()
    if not user:
        logger.error("No current user configured")
        return []
        
    # Ensure server URL has trailing slash
    server_url = user['server'].rstrip('/') + '/'
    url = f"{server_url}player_api.php"
    params = {
        "username": user['username'],
        "password": user['password'],
        "action": "get_series",
        "category_id": category_id
    }
    
    try:
        response = session.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching series list: {str(e)}")
        return []

def get_series_info(series_id):
    """Fetch series information"""
    user = get_current_user()
    if not user:
        logger.error("No current user configured")
        return None
        
    # Ensure server URL has trailing slash
    server_url = user['server'].rstrip('/') + '/'
    url = f"{server_url}player_api.php"
    params = {
        "username": user['username'],
        "password": user['password'],
        "action": "get_series_info",
        "series_id": series_id
    }
    
    try:
        response = session.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching series info: {str(e)}")
        return None

def get_movie_categories():
    """Fetch all movie categories"""
    user = get_current_user()
    if not user:
        logger.error("No current user configured")
        return []
        
    # Ensure server URL has trailing slash
    server_url = user['server'].rstrip('/') + '/'
    url = f"{server_url}player_api.php"
    params = {
        "username": user['username'],
        "password": user['password'],
        "action": "get_vod_categories"
    }
    
    try:
        logger.debug(f"Fetching movie categories from: {url}")
        response = session.get(url, params=params, timeout=(5, 15))
        response.raise_for_status()
        categories = response.json()
        logger.debug(f"Retrieved {len(categories)} movie categories")
        return categories
    except requests.exceptions.Timeout:
        logger.error("Request timed out while fetching movie categories")
        return []
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return []

def get_movies_by_category(category_id):
    """Fetch all movies in a category"""
    user = get_current_user()
    if not user:
        logger.error("No current user configured")
        return []
        
    # Ensure server URL has trailing slash
    server_url = user['server'].rstrip('/') + '/'
    url = f"{server_url}player_api.php"
    params = {
        "username": user['username'],
        "password": user['password'],
        "action": "get_vod_streams",
        "category_id": category_id
    }
    
    try:
        response = session.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching movies list: {str(e)}")
        return []

def get_movie_info(vod_id):
    """Fetch movie information"""
    user = get_current_user()
    if not user:
        logger.error("No current user configured")
        return None
        
    # Ensure server URL has trailing slash
    server_url = user['server'].rstrip('/') + '/'
    url = f"{server_url}player_api.php"
    params = {
        "username": user['username'],
        "password": user['password'],
        "action": "get_vod_info",
        "vod_id": vod_id
    }
    
    try:
        logger.debug(f"Fetching movie info from: {url} with params: {params}")
        response = session.get(url, params=params)
        response.raise_for_status()
        movie_data = response.json()
        logger.debug(f"Movie API response: {movie_data}")
        return movie_data
    except Exception as e:
        logger.error(f"Error fetching movie info: {str(e)}")
        return None

def download_movie_file(movie_info, output_path, stream_id=None):
    """Download a single movie file with enhanced progress tracking"""
    # Try multiple ways to get the stream_id
    if not stream_id:
        stream_id = (movie_info.get('stream_id') or 
                    movie_info.get('id') or 
                    movie_info.get('movie_id'))
    
    if not stream_id:
        raise ValueError("No valid stream_id found for movie download")
    
    container_extension = movie_info.get('container_extension', 'mp4')
    title = movie_info.get('name', 'Unknown Movie')
    
    # Fix URL construction to avoid double slashes using current user
    user = get_current_user()
    if not user:
        logger.error("No current user configured for movie download")
        return False
        
    base_url = user['server'].rstrip('/')
    url = f"{base_url}/movie/{user['username']}/{user['password']}/{stream_id}.{container_extension}"
    
    try:
        logger.debug(f"Attempting to download movie from: {url}")
        response = session.get(url, stream=True, allow_redirects=True)
        logger.debug(f"Response status: {response.status_code}")
        logger.debug(f"Response headers: {dict(response.headers)}")
        logger.debug(f"Final URL after redirects: {response.url}")
        
        response.raise_for_status()
        
        file_size = int(response.headers.get('content-length', 0))
        logger.debug(f"Movie file size: {file_size} bytes")
        
        if file_size == 0:
            logger.warning("File size is 0 bytes, this might indicate an issue with the stream")
            # Try to read a small chunk to see if there's actually data
            test_chunk = next(response.iter_content(chunk_size=1024), None)
            if not test_chunk:
                raise ValueError("No data available in the stream")
            else:
                logger.debug(f"Found data in stream despite 0 content-length header")
                # Reset the response by making a new request
                response = session.get(url, stream=True, allow_redirects=True)
        
        # Set up CLI progress bar
        progress_bar = tqdm(
            total=file_size,
            unit='iB',
            unit_scale=True,
            desc=f"Downloading {title}"
        )
        
        downloaded = 0
        start_time = time.time()
        last_update_time = start_time
        update_interval = 0.5  # Update every 0.5 seconds
        
        # If file_size is 0, we'll update progress based on downloaded bytes
        use_size_based_progress = file_size > 0
        
        with open(output_path, 'wb') as f:
            for data in response.iter_content(chunk_size=8192):
                if data:
                    size = f.write(data)
                    downloaded += size
                    progress_bar.update(size)
                    
                    # Update file_size if it was initially 0 and we're getting data
                    if not use_size_based_progress and downloaded > 0:
                        # Estimate total size based on download speed (rough estimate)
                        progress_bar.total = None  # Make it indeterminate
                    
                    current_time = time.time()
                    
                    # Update web UI progress at intervals
                    if current_time - last_update_time >= update_interval:
                        elapsed_time = current_time - start_time
                        
                        # Calculate download speed
                        if elapsed_time > 0:
                            speed_bytes_per_sec = downloaded / elapsed_time
                            
                            # Calculate ETA
                            if speed_bytes_per_sec > 0 and file_size > 0:
                                remaining_bytes = file_size - downloaded
                                eta_seconds = remaining_bytes / speed_bytes_per_sec
                            else:
                                eta_seconds = float('inf')
                        else:
                            speed_bytes_per_sec = 0
                            eta_seconds = float('inf')
                        
                        # Calculate progress percentage
                        if use_size_based_progress:
                            progress_percent = (downloaded / file_size) * 100
                        else:
                            # For unknown file size, show indeterminate progress
                            progress_percent = min(99, (downloaded / (1024 * 1024)) * 10)  # Rough progress based on MB downloaded
                        
                        # Update web UI progress via SSE with enhanced data
                        progress = {
                            'movie': title,
                            'progress': progress_percent,
                            'status': 'downloading',
                            'downloaded_bytes': downloaded,
                            'total_bytes': file_size,
                            'download_speed': speed_bytes_per_sec,
                            'eta_seconds': eta_seconds,
                            'formatted_speed': f"{format_bytes(speed_bytes_per_sec)}/s",
                            'formatted_eta': format_time(eta_seconds),
                            'formatted_downloaded': format_bytes(downloaded),
                            'formatted_total': format_bytes(file_size),
                            'elapsed_time': elapsed_time,
                            'formatted_elapsed': format_time(elapsed_time)
                        }
                        sse_queue.put(progress)
                        
                        last_update_time = current_time
        
        progress_bar.close()
        
        # Send final completion update
        final_time = time.time() - start_time
        final_file_size = downloaded if not use_size_based_progress else file_size
        final_progress = {
            'movie': title,
            'progress': 100,
            'status': 'complete',
            'downloaded_bytes': final_file_size,
            'total_bytes': final_file_size,
            'download_speed': final_file_size / final_time if final_time > 0 else 0,
            'eta_seconds': 0,
            'formatted_speed': f"{format_bytes(final_file_size / final_time if final_time > 0 else 0)}/s",
            'formatted_eta': "00:00",
            'formatted_downloaded': format_bytes(final_file_size),
            'formatted_total': format_bytes(final_file_size),
            'elapsed_time': final_time,
            'formatted_elapsed': format_time(final_time)
        }
        sse_queue.put(final_progress)
        
        return True
    except Exception as e:
        logger.error(f"Error downloading {title}: {str(e)}")
        if os.path.exists(output_path):
            os.remove(output_path)
        
        # Send error progress update
        error_progress = {
            'movie': title,
            'progress': 0,
            'status': 'error',
            'error': str(e)
        }
        sse_queue.put(error_progress)
        return False

def format_bytes(bytes_value):
    """Convert bytes to human readable format"""
    if bytes_value == 0:
        return "0 B"
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} TB"

def format_time(seconds):
    """Convert seconds to human readable time format"""
    if seconds < 0 or seconds == float('inf'):
        return "∞"
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"

def download_episode_file(episode, output_path, episode_num=1, total_episodes=1):
    """Download a single episode file with enhanced progress tracking"""
    # Fix URL construction to avoid double slashes using current user
    user = get_current_user()
    if not user:
        logger.error("No current user configured for episode download")
        return False
        
    base_url = user['server'].rstrip('/')
    url = f"{base_url}/series/{user['username']}/{user['password']}/{episode['id']}.{episode['container_extension']}"
    
    try:
        logger.debug(f"Attempting to download from: {url}")
        response = session.get(url, stream=True)
        response.raise_for_status()
        
        file_size = int(response.headers.get('content-length', 0))
        logger.debug(f"File size: {file_size} bytes")
        
        # Set up CLI progress bar
        progress_bar = tqdm(
            total=file_size,
            unit='iB',
            unit_scale=True,
            desc=f"Downloading {episode['title']}"
        )
        
        downloaded = 0
        start_time = time.time()
        last_update_time = start_time
        last_downloaded = 0
        update_interval = 0.5  # Update every 0.5 seconds
        
        with open(output_path, 'wb') as f:
            for data in response.iter_content(chunk_size=8192):
                if data:
                    size = f.write(data)
                    downloaded += size
                    progress_bar.update(size)
                    
                    current_time = time.time()
                    
                    # Update web UI progress at intervals to avoid flooding
                    if current_time - last_update_time >= update_interval:
                        elapsed_time = current_time - start_time
                        
                        # Calculate download speed
                        if elapsed_time > 0:
                            speed_bytes_per_sec = downloaded / elapsed_time
                            
                            # Calculate ETA
                            if speed_bytes_per_sec > 0 and file_size > 0:
                                remaining_bytes = file_size - downloaded
                                eta_seconds = remaining_bytes / speed_bytes_per_sec
                            else:
                                eta_seconds = float('inf')
                        else:
                            speed_bytes_per_sec = 0
                            eta_seconds = float('inf')
                        
                        # Calculate progress percentage
                        progress_percent = (downloaded / file_size) * 100 if file_size > 0 else 0
                        
                        # Update web UI progress via SSE with enhanced data
                        progress = {
                            'episode': episode['title'],
                            'episode_num': episode_num,
                            'total_episodes': total_episodes,
                            'progress': progress_percent,
                            'status': 'downloading',
                            'downloaded_bytes': downloaded,
                            'total_bytes': file_size,
                            'download_speed': speed_bytes_per_sec,
                            'eta_seconds': eta_seconds,
                            'formatted_speed': f"{format_bytes(speed_bytes_per_sec)}/s",
                            'formatted_eta': format_time(eta_seconds),
                            'formatted_downloaded': format_bytes(downloaded),
                            'formatted_total': format_bytes(file_size),
                            'elapsed_time': elapsed_time,
                            'formatted_elapsed': format_time(elapsed_time)
                        }
                        sse_queue.put(progress)
                        
                        last_update_time = current_time
                        last_downloaded = downloaded
        
        progress_bar.close()
        
        # Send final completion update for this episode
        final_time = time.time() - start_time
        final_progress = {
            'episode': episode['title'],
            'episode_num': episode_num,
            'total_episodes': total_episodes,
            'progress': 100,
            'status': 'episode_complete',
            'downloaded_bytes': file_size,
            'total_bytes': file_size,
            'download_speed': file_size / final_time if final_time > 0 else 0,
            'eta_seconds': 0,
            'formatted_speed': f"{format_bytes(file_size / final_time if final_time > 0 else 0)}/s",
            'formatted_eta': "00:00",
            'formatted_downloaded': format_bytes(file_size),
            'formatted_total': format_bytes(file_size),
            'elapsed_time': final_time,
            'formatted_elapsed': format_time(final_time)
        }
        sse_queue.put(final_progress)
        
        return True
    except Exception as e:
        logger.error(f"Error downloading {episode['title']}: {str(e)}")
        if os.path.exists(output_path):
            os.remove(output_path)
        
        # Send error progress update
        error_progress = {
            'episode': episode['title'],
            'episode_num': episode_num,
            'total_episodes': total_episodes,
            'progress': 0,
            'status': 'error',
            'error': str(e)
        }
        sse_queue.put(error_progress)
        return False

# Authentication routes
@app.route('/')
def main_redirect():
    # Check if any users are configured
    if not config.USERS or not any(config.USERS.values()):
        return redirect(url_for('setup'))
    
    # Check if current user is set and valid
    if not config.CURRENT_USER or config.CURRENT_USER not in config.USERS:
        return redirect(url_for('setup'))
    
    return redirect(url_for('main'))

@app.route('/setup')
def setup():
    """Setup page for configuring user credentials."""
    return render_template('setup.html')

@app.route('/setup', methods=['POST'])
def setup_post():
    """Handle setup form submission."""
    server = request.form.get('server', '').strip()
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    
    if not all([server, username, password]):
        return jsonify({'success': False, 'error': 'Please fill in all required fields.'})
    
    # Normalize server URL for comparison
    normalized_server = server.rstrip('/')
    
    # Check for duplicate users (same server + username combination)
    for user_data in config.USERS.values():
        existing_server = user_data.get('server', '').rstrip('/')
        if (existing_server == normalized_server and 
            user_data.get('username') == username):
            return jsonify({'success': False, 'error': 'User with this server and username already exists.'})
    
    # Test connection
    result = test_connection(server, username, password)
    
    if result['success']:
        # Generate user ID
        import uuid
        user_id = f"user_{str(uuid.uuid4())[:8]}"
        
        # Save user configuration
        user_info = result['data'].get('user_info', {})
        server_info = result['data'].get('server_info', {})
        
        if save_user_to_config(user_id, server, username, password, user_info, server_info):
            return jsonify({'success': True, 'message': 'Configuration saved successfully!'})
        else:
            return jsonify({'success': False, 'error': 'Failed to save configuration.'})
    else:
        return jsonify(result)

@app.route('/test_connection', methods=['POST'])
def test_connection_route():
    """Test connection endpoint for AJAX calls."""
    data = request.get_json()
    server = data.get('server', '').strip()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    if not all([server, username, password]):
        return jsonify({'success': False, 'error': 'Please fill in all required fields.'})
    
    result = test_connection(server, username, password)
    return jsonify(result)

@app.route('/user_info')
def user_info():
    """Get current user information."""
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'error': 'No user logged in'})
    
    return jsonify({
        'success': True,
        'user': {
            'username': user.get('username'),
            'server': user.get('server'),
            'user_info': user.get('user_info', {}),
            'server_info': user.get('server_info', {})
        }
    })

@app.route('/switch_user', methods=['POST'])
def switch_user_route():
    """Switch to different user."""
    data = request.get_json()
    user_id = data.get('user_id')
    
    if not user_id or user_id not in config.USERS:
        return jsonify({'success': False, 'error': 'Invalid user ID'})
    
    if switch_user(user_id):
        return jsonify({'success': True, 'message': 'User switched successfully'})
    else:
        return jsonify({'success': False, 'error': 'Failed to switch user'})

@app.route('/add_user', methods=['POST'])
def add_user():
    """Add a new user."""
    data = request.get_json()
    server = data.get('server', '').strip()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    if not all([server, username, password]):
        return jsonify({'success': False, 'error': 'Please fill in all required fields.'})
    
    # Normalize server URL for comparison
    normalized_server = server.rstrip('/')
    
    # Check for duplicate users (same server + username combination)
    for user_data in config.USERS.values():
        existing_server = user_data.get('server', '').rstrip('/')
        if (existing_server == normalized_server and 
            user_data.get('username') == username):
            return jsonify({'success': False, 'error': 'User with this server and username already exists.'})
    
    # Test connection
    result = test_connection(server, username, password)
    
    if result['success']:
        # Generate user ID
        import uuid
        user_id = f"user_{str(uuid.uuid4())[:8]}"
        
        # Save user configuration
        user_info = result['data'].get('user_info', {})
        server_info = result['data'].get('server_info', {})
        
        if save_user_to_config(user_id, server, username, password, user_info, server_info):
            return jsonify({'success': True, 'message': 'User added successfully!', 'user_id': user_id})
        else:
            return jsonify({'success': False, 'error': 'Failed to save user configuration.'})
    else:
        return jsonify(result)

@app.route('/logout')
def logout():
    """Logout current user and remove from config."""
    try:
        # Remove current user from USERS dictionary
        if config.CURRENT_USER and config.CURRENT_USER in config.USERS:
            del config.USERS[config.CURRENT_USER]
        
        # Clear current user in memory
        config.CURRENT_USER = None
        config.BASE_URL = ""
        config.USERNAME = ""
        config.PASSWORD = ""
        
        # Update the config file - write remaining users (if any)
        users_str = "USERS = {\n"
        for uid, user_data in config.USERS.items():
            users_str += f'    "{uid}": {{\n'
            users_str += f'        "id": "{user_data["id"]}",\n'
            users_str += f'        "server": "{user_data["server"]}",\n'
            users_str += f'        "username": "{user_data["username"]}",\n'
            users_str += f'        "password": "{user_data["password"]}",\n'
            users_str += f'        "user_info": {user_data["user_info"]},\n'
            users_str += f'        "server_info": {user_data["server_info"]}\n'
            users_str += '    },\n'
        users_str += "}\n\n"
        
        current_user_str = 'CURRENT_USER = None\n\n'
        
        helper_functions = '''# Legacy support (points to current user's config)
def get_current_config():
    if CURRENT_USER and CURRENT_USER in USERS:
        user = USERS[CURRENT_USER]
        return {
            'BASE_URL': user['server'],
            'USERNAME': user['username'], 
            'PASSWORD': user['password']
        }
    return {'BASE_URL': '', 'USERNAME': '', 'PASSWORD': ''}

# For backward compatibility - these will be updated dynamically
BASE_URL = ""
USERNAME = ""
PASSWORD = ""'''
        
        new_content = "# Multi-user configuration\n" + users_str + current_user_str + helper_functions
        
        with open('config.py', 'w') as f:
            f.write(new_content)
            
    except Exception as e:
        logger.error(f"Error during logout: {str(e)}")
    
    return redirect(url_for('setup'))

@app.route('/clear_all_users')
def clear_all_users():
    """Clear all users and reset config (for debugging/testing)."""
    try:
        # Clear all users
        config.USERS = {}
        config.CURRENT_USER = None
        config.BASE_URL = ""
        config.USERNAME = ""
        config.PASSWORD = ""
        
        # Write empty config
        new_content = '''# Multi-user configuration
USERS = {}

CURRENT_USER = None

# Legacy support (points to current user's config)
def get_current_config():
    if CURRENT_USER and CURRENT_USER in USERS:
        user = USERS[CURRENT_USER]
        return {
            'BASE_URL': user['server'],
            'USERNAME': user['username'], 
            'PASSWORD': user['password']
        }
    return {'BASE_URL': '', 'USERNAME': '', 'PASSWORD': ''}

# For backward compatibility - these will be updated dynamically
BASE_URL = ""
USERNAME = ""
PASSWORD = ""'''
        
        with open('config.py', 'w') as f:
            f.write(new_content)
            
        return jsonify({'success': True, 'message': 'All users cleared successfully'})
            
    except Exception as e:
        logger.error(f"Error clearing all users: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to clear users'})

@app.route('/get_users')
def get_users():
    """Get list of all configured users."""
    users = []
    for user_id, user_data in config.USERS.items():
        users.append({
            'id': user_id,
            'username': user_data.get('username'),
            'server': user_data.get('server'),
            'is_current': user_id == config.CURRENT_USER
        })
    return jsonify({'users': users})

@app.route('/series')
@app.route('/series/page/<int:page>')
def series_index(page=1):
    # Get per_page from query parameter, default to 50
    per_page = request.args.get('per_page', 50, type=int)
    # Validate per_page to be within allowed range
    if per_page not in [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]:
        per_page = 50
    
    categories = get_categories()
    if not categories:
        return render_template('error.html', 
                            message="Unable to fetch categories. Please try again later."), 503
    
    # Calculate pagination
    total_categories = len(categories)
    pages = (total_categories + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    
    category_counts = get_series_count_by_category()

    return render_template('index.html', 
                         categories=categories[start:end],
                         current_page=page,
                         total_pages=pages,
                         total_categories=total_categories,
                         category_counts=category_counts,
                         per_page=per_page)

@app.route('/series/<category_id>')
@app.route('/series/<category_id>/page/<int:page>')
def series(category_id, page=1):
    # Get per_page from query parameter, default to 50
    per_page = request.args.get('per_page', 50, type=int)
    # Validate per_page to be within allowed range
    if per_page not in [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]:
        per_page = 50
    
    series_list = get_series_by_category(category_id)
    
    # Get category name
    categories = get_categories()
    category_name = next((cat['category_name'] for cat in categories if cat['category_id'] == category_id), 'Unknown Category')
    
    # Calculate pagination
    total = len(series_list)
    pages = (total + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    
    return render_template('series.html', 
                         series_list=series_list[start:end],
                         current_page=page,
                         total_pages=pages,
                         category_id=category_id,
                         category_name=category_name,
                         per_page=per_page)

@app.route('/download', methods=['POST'])
def download():
    series_id = request.form.get('series_id')
    referrer = request.form.get('referrer', 'search')  # Default to search if not specified
    search_query = request.form.get('search_query', '')  # Get search query if from search
    content_type = request.form.get('content_type', 'all')  # Get content type filter
    logger.debug(f"Downloading series with ID: {series_id}, referrer: {referrer}")
    
    series_data = get_series_info(series_id)
    if not series_data:
        return render_template('error.html', 
                             message="Could not fetch series information"), 503
    
    # Pass both series_data and the original series_id
    return render_template('download.html', 
                         series=series_data, 
                         series_id=series_id, 
                         referrer=referrer,
                         search_query=search_query,
                         content_type=content_type)

# Update the download_episodes route
@app.route('/download_episodes', methods=['POST'])
def download_episodes():
    series_id = request.form.get('series_id')
    season = request.form.get('season')
    
    logger.debug(f"Download request - Series ID: {series_id}, Season: {season}")
    
    try:
        start_episode = int(request.form.get('start_episode'))
        end_episode = int(request.form.get('end_episode'))
    except (TypeError, ValueError) as e:
        logger.error(f"Invalid episode numbers: {e}")
        return jsonify({'error': 'Invalid episode numbers'}), 400
    
    # Get series data
    series_data = get_series_info(series_id)
    if not series_data:
        logger.error(f"Could not fetch series info for ID: {series_id}")
        return jsonify({'error': 'Could not fetch series information'}), 503
        
    try:
        episodes = series_data['episodes'][season]
        episodes_to_download = episodes[start_episode-1:end_episode]
        
        if not episodes_to_download:
            return jsonify({'error': 'No episodes found in selected range'}), 400
        
        # Create downloads directory if it doesn't exist
        series_dir = os.path.join(DOWNLOADS_DIR, f"{series_data['info']['name']} - S{season}")
        os.makedirs(series_dir, exist_ok=True)
        
        # Start download process in background thread
        def download_worker():
            try:
                total = len(episodes_to_download)
                successful_downloads = 0
                failed_downloads = 0
                overall_start_time = time.time()
                
                # Send initial status
                sse_queue.put({
                    'status': 'starting',
                    'message': f'Starting download of {total} episodes...',
                    'total_episodes': total,
                    'current_episode': 0
                })
                
                for i, episode in enumerate(episodes_to_download, 1):
                    # Send episode start notification
                    sse_queue.put({
                        'status': 'episode_starting',
                        'episode': episode['title'],
                        'episode_num': i,
                        'total_episodes': total,
                        'message': f'Starting episode {i} of {total}: {episode["title"]}'
                    })
                    
                    output_path = os.path.join(series_dir, f"{episode['title']}.{episode['container_extension']}")
                    success = download_episode_file(episode, output_path, i, total)
                    
                    if success:
                        successful_downloads += 1
                    else:
                        failed_downloads += 1
                    
                    # Send overall progress update
                    overall_progress = (i / total) * 100
                    elapsed_time = time.time() - overall_start_time
                    
                    sse_queue.put({
                        'status': 'overall_progress',
                        'overall_progress': overall_progress,
                        'completed_episodes': i,
                        'total_episodes': total,
                        'successful_downloads': successful_downloads,
                        'failed_downloads': failed_downloads,
                        'overall_elapsed': elapsed_time,
                        'formatted_overall_elapsed': format_time(elapsed_time),
                        'message': f'Completed {i} of {total} episodes'
                    })
                
                # Send final completion message
                total_time = time.time() - overall_start_time
                completion_message = f'Download completed! {successful_downloads} successful, {failed_downloads} failed in {format_time(total_time)}'
                
                sse_queue.put({
                    'progress': 100,
                    'overall_progress': 100,
                    'status': 'complete',
                    'message': completion_message,
                    'successful_downloads': successful_downloads,
                    'failed_downloads': failed_downloads,
                    'total_time': total_time,
                    'formatted_total_time': format_time(total_time)
                })
                # Send sentinel to close connection
                sse_queue.put(None)
            except Exception as e:
                logger.error(f"Download worker error: {str(e)}")
                sse_queue.put({
                    'status': 'error',
                    'error': str(e),
                    'message': f'Download process failed: {str(e)}'
                })
                sse_queue.put(None)
        
        thread = threading.Thread(target=download_worker)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': f'Download started for {len(episodes_to_download)} episodes'
        })
        
    except KeyError as e:
        logger.error(f"Invalid season or episode data: {e}")
        return jsonify({'error': 'Invalid season or episode data'}), 400
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Add SSE route for progress updates
sse_queue = Queue()

@app.route('/progress')
def progress():
    def generate():
        try:
            while True:
                # Add timeout to prevent infinite blocking
                try:
                    progress = sse_queue.get(timeout=30)
                    if progress is None:  # Use None as sentinel to stop
                        break
                    yield f"data: {json.dumps(progress)}\n\n"
                except Queue.Empty:
                    # Send keep-alive message every 30 seconds
                    yield ": keep-alive\n\n"
        except GeneratorExit:
            # Client disconnected, cleanup
            logger.debug("Client disconnected from progress stream")
        except Exception as e:
            logger.error(f"Error in progress stream: {str(e)}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )

@app.route('/test_base_html')
def test_base_html():
    return render_template('base.html')

@app.route('/search')
def search():
    query = request.args.get('query')
    content_type = request.args.get('content_type', 'all')  # 'series', 'movies', or 'all'
    
    results = []
    series_last_fetch_date = None
    movies_last_fetch_date = None

    # Get cached data dates
    series_cached_data = get_cached_data('series')
    movies_cached_data = get_cached_data('movies')
    
    if series_cached_data:
        series_last_fetch_date = series_cached_data.get("last_fetch_date")
    if movies_cached_data:
        movies_last_fetch_date = movies_cached_data.get("last_fetch_date")

    if query:
        if content_type == 'series':
            results, _ = search_series(query)
        elif content_type == 'movies':
            results, _ = search_movies(query)
        else:  # 'all'
            results, _ = search_all_content(query)

    return render_template('search.html', 
                         query=query, 
                         results=results, 
                         content_type=content_type,
                         series_last_fetch_date=series_last_fetch_date,
                         movies_last_fetch_date=movies_last_fetch_date)

@app.route('/cache_progress')
def cache_progress():
    def generate():
        while True:
            try:
                progress_data = sse_queue.get(timeout=1) # Short timeout to keep connection alive
                if progress_data is None: # Sentinel to close connection
                    break
                yield f"data: {json.dumps(progress_data)}\n\n"
            except Empty:
                yield ": keep-alive\n\n" # Send keep-alive to prevent timeout
            except GeneratorExit:
                logger.debug("Client disconnected from cache progress stream")
                break
            except Exception as e:
                logger.error(f"Error in cache progress stream: {str(e)}")
                yield f"data: {json.dumps({'status': 'error', 'message': str(e)})}\n\n"

    return Response(stream_with_context(generate()), mimetype='text/event-stream')

def format_cache_time(seconds):
    """Format time for cache progress display"""
    if seconds < 0 or seconds == float('inf'):
        return "∞"
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"

@app.route('/cache_data')
def cache_data():
    """Endpoint to trigger the caching of data in a background thread."""
    cache_type = request.args.get('cache_type', 'both')  # 'series', 'movies', or 'both'
    
    def caching_worker(app_context):
        with app_context:
            try:
                def progress_callback(progress, message, status, details=None):
                    progress_data = {
                        'progress': progress,
                        'message': message,
                        'status': status,
                        'cache_type': cache_type
                    }
                    
                    # Add detailed information if available
                    if details:
                        # Handle both series and movies data
                        progress_data.update({
                            'total_categories': details.get('total_categories', 0),
                            'processed_categories': details.get('processed_categories', 0),
                            'current_category': details.get('current_category', ''),
                            'category_series_count': details.get('category_series_count', 0),
                            'category_movies_count': details.get('category_movies_count', 0),
                            'total_series': details.get('total_series', 0),
                            'processed_series': details.get('processed_series', 0),
                            'failed_series': details.get('failed_series', 0),
                            'total_movies': details.get('total_movies', 0),
                            'processed_movies': details.get('processed_movies', 0),
                            'failed_movies': details.get('failed_movies', 0),
                            'elapsed_time': details.get('elapsed_time', 0),
                            'eta_seconds': details.get('eta_seconds', 0),
                            'formatted_elapsed': format_cache_time(details.get('elapsed_time', 0)),
                            'formatted_eta': format_cache_time(details.get('eta_seconds', 0)) if details.get('eta_seconds', 0) > 0 else '--:--',
                            'avg_time_per_category': details.get('avg_time_per_category', 0)
                        })
                        
                        # Calculate processing rate
                        if details.get('elapsed_time', 0) > 0:
                            categories_per_minute = (details.get('processed_categories', 0) / details.get('elapsed_time', 1)) * 60
                            if details.get('processed_series', 0) > 0:
                                series_per_minute = (details.get('processed_series', 0) / details.get('elapsed_time', 1)) * 60
                                progress_data['series_per_minute'] = round(series_per_minute, 1)
                            if details.get('processed_movies', 0) > 0:
                                movies_per_minute = (details.get('processed_movies', 0) / details.get('elapsed_time', 1)) * 60
                                progress_data['movies_per_minute'] = round(movies_per_minute, 1)
                            progress_data['categories_per_minute'] = round(categories_per_minute, 1)
                    
                    sse_queue.put(progress_data)
                
                # Cache based on type
                if cache_type == 'series':
                    process_and_cache_series_data(get_categories, get_series_by_category, progress_callback)
                elif cache_type == 'movies':
                    process_and_cache_movies_data(get_movie_categories, get_movies_by_category, progress_callback)
                else:  # 'both'
                    # Cache series first
                    sse_queue.put({
                        'status': 'starting',
                        'message': 'Starting series caching...',
                        'cache_type': 'series'
                    })
                    process_and_cache_series_data(get_categories, get_series_by_category, progress_callback)
                    
                    # Then cache movies
                    sse_queue.put({
                        'status': 'starting',
                        'message': 'Starting movies caching...',
                        'cache_type': 'movies'
                    })
                    process_and_cache_movies_data(get_movie_categories, get_movies_by_category, progress_callback)
                
            except Exception as e:
                logger.error(f"Error during caching process: {str(e)}")
                sse_queue.put({
                    'status': 'error',
                    'message': f'Caching failed: {str(e)}'
                })
            finally:
                sse_queue.put(None) # Sentinel to close the SSE connection

    # Start the caching process in a new thread
    app_context = app.app_context()
    thread = threading.Thread(target=caching_worker, args=(app_context,))
    thread.daemon = True
    thread.start()

    return jsonify({"status": "success", "message": "Caching process initiated in background."})

# Streaming routes
@app.route('/watch/movie/<vod_id>')
def watch_movie(vod_id):
    """Render streaming page for movies"""
    referrer = request.args.get('referrer', 'search')
    search_query = request.args.get('search_query', '')
    content_type = request.args.get('content_type', 'all')
    
    movie_data = get_movie_info(vod_id)
    if not movie_data:
        return render_template('error.html', 
                             message="Could not fetch movie information"), 503
    
    # Get movie info for stream URL
    movie_info = movie_data.get('movie_data', {})
    stream_id = movie_info.get('stream_id', vod_id)
    container_extension = movie_info.get('container_extension', 'mp4')
    
    # Construct stream URL using current user
    user = get_current_user()
    if not user:
        return render_template('error.html', 
                             message="No user configured"), 503
    
    base_url = user['server'].rstrip('/')
    stream_url = f"{base_url}/movie/{user['username']}/{user['password']}/{stream_id}.{container_extension}"
    
    return render_template('watch_movie.html', 
                         movie=movie_data, 
                         vod_id=vod_id,
                         stream_url=stream_url,
                         referrer=referrer,
                         search_query=search_query,
                         content_type=content_type)

@app.route('/watch/series/<series_id>/<episode_id>')
def watch_series(series_id, episode_id):
    """Render streaming page for series episodes"""
    referrer = request.args.get('referrer', 'search')
    search_query = request.args.get('search_query', '')
    content_type = request.args.get('content_type', 'all')
    season = request.args.get('season', '1')
    
    series_data = get_series_info(series_id)
    if not series_data:
        return render_template('error.html', 
                             message="Could not fetch series information"), 503
    
    # Find the episode info
    episode_info = None
    current_season = None
    episode_list = []
    
    for season_num, episodes in series_data.get('episodes', {}).items():
        for episode in episodes:
            if str(episode.get('id')) == str(episode_id):
                episode_info = episode
                current_season = season_num
                episode_list = episodes
                break
        if episode_info:
            break
    
    if not episode_info:
        return render_template('error.html', 
                             message="Episode not found"), 404
    
    # Construct stream URL using current user
    user = get_current_user()
    if not user:
        return render_template('error.html', 
                             message="No user configured"), 503
    
    base_url = user['server'].rstrip('/')
    container_extension = episode_info.get('container_extension', 'mp4')
    stream_url = f"{base_url}/series/{user['username']}/{user['password']}/{episode_id}.{container_extension}"
    
    return render_template('watch_series.html', 
                         series=series_data,
                         series_id=series_id,
                         episode=episode_info,
                         episode_id=episode_id,
                         current_season=current_season,
                         episode_list=episode_list,
                         stream_url=stream_url,
                         referrer=referrer,
                         search_query=search_query,
                         content_type=content_type)

@app.route('/stream_proxy')
def stream_proxy():
    """Proxy streaming requests to handle CORS and authentication"""
    stream_url = request.args.get('url')
    if not stream_url:
        return "No stream URL provided", 400
    
    try:
        # Add range support for video seeking
        range_header = request.headers.get('Range')
        headers = {}
        if range_header:
            headers['Range'] = range_header
        
        response = session.get(stream_url, stream=True, headers=headers)
        
        def generate():
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk
        
        return Response(
            generate(),
            status=response.status_code,
            content_type=response.headers.get('content-type', 'video/mp4'),
            headers={
                'Accept-Ranges': 'bytes',
                'Content-Length': response.headers.get('content-length', ''),
                'Content-Range': response.headers.get('content-range', ''),
                'Cache-Control': 'no-cache',
            }
        )
    except Exception as e:
        logger.error(f"Streaming proxy error: {str(e)}")
        return f"Streaming error: {str(e)}", 500

# Main selection page
@app.route('/main')
def main():
    # Check if user is authenticated
    if not get_current_user():
        return redirect(url_for('setup'))
    
    # Get cached data statistics
    series_stats = {'categories': 0, 'total_items': 0, 'last_cached': None}
    movies_stats = {'categories': 0, 'total_items': 0, 'last_cached': None}
    
    # Get series statistics
    series_cached_data = get_cached_data('series')
    if series_cached_data:
        series_stats['last_cached'] = series_cached_data.get('last_fetch_date')
        series_stats['total_items'] = len(series_cached_data.get('series', {}))
        
        # Count unique categories
        series_categories = set()
        for series_data in series_cached_data.get('series', {}).values():
            category_id = series_data.get('category_ID')
            if category_id:
                series_categories.add(category_id)
        series_stats['categories'] = len(series_categories)
    
    # Get movies statistics  
    movies_cached_data = get_cached_data('movies')
    if movies_cached_data:
        movies_stats['last_cached'] = movies_cached_data.get('last_fetch_date')
        movies_stats['total_items'] = len(movies_cached_data.get('movies', {}))
        
        # Count unique categories
        movies_categories = set()
        for movie_data in movies_cached_data.get('movies', {}).values():
            category_id = movie_data.get('category_ID')
            if category_id:
                movies_categories.add(category_id)
        movies_stats['categories'] = len(movies_categories)
    
    return render_template('main.html', series_stats=series_stats, movies_stats=movies_stats)

# Movie routes
@app.route('/movies')
@app.route('/movies/page/<int:page>')
def movies_index(page=1):
    # Get per_page from query parameter, default to 50
    per_page = request.args.get('per_page', 50, type=int)
    # Validate per_page to be within allowed range
    if per_page not in [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]:
        per_page = 50
    
    categories = get_movie_categories()
    if not categories:
        return render_template('error.html', 
                            message="Unable to fetch movie categories. Please try again later."), 503
    
    # Calculate pagination
    total_categories = len(categories)
    pages = (total_categories + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    
    # Get movie counts by category
    category_counts = get_movies_count_by_category()

    return render_template('movies_index.html', 
                         categories=categories[start:end],
                         current_page=page,
                         total_pages=pages,
                         total_categories=total_categories,
                         category_counts=category_counts,
                         per_page=per_page)

@app.route('/movies/<category_id>')
@app.route('/movies/<category_id>/page/<int:page>')
def movies(category_id, page=1):
    # Get per_page from query parameter, default to 50
    per_page = request.args.get('per_page', 50, type=int)
    # Validate per_page to be within allowed range
    if per_page not in [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]:
        per_page = 50
    
    movies_list = get_movies_by_category(category_id)
    
    # Get category name
    categories = get_movie_categories()
    category_name = next((cat['category_name'] for cat in categories if cat['category_id'] == category_id), 'Unknown Category')
    
    # Calculate pagination
    total = len(movies_list)
    pages = (total + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    
    return render_template('movies.html', 
                         movies_list=movies_list[start:end],
                         current_page=page,
                         total_pages=pages,
                         category_id=category_id,
                         category_name=category_name,
                         per_page=per_page)

@app.route('/movie_download', methods=['POST'])
def movie_download():
    vod_id = request.form.get('vod_id')
    referrer = request.form.get('referrer', 'search')  # Default to search if not specified
    search_query = request.form.get('search_query', '')  # Get search query if from search
    content_type = request.form.get('content_type', 'all')  # Get content type filter
    logger.debug(f"Downloading movie with VOD ID: {vod_id}, referrer: {referrer}")
    
    movie_data = get_movie_info(vod_id)
    if not movie_data:
        return render_template('error.html', 
                             message="Could not fetch movie information"), 503
    
    return render_template('movie_download.html', 
                         movie=movie_data, 
                         vod_id=vod_id, 
                         referrer=referrer,
                         search_query=search_query,
                         content_type=content_type)

@app.route('/download_movie', methods=['POST'])
def download_movie():
    vod_id = request.form.get('vod_id')
    
    logger.debug(f"Download request - Movie VOD ID: {vod_id}")
    
    # Get movie data
    movie_data = get_movie_info(vod_id)
    if not movie_data:
        logger.error(f"Could not fetch movie info for VOD ID: {vod_id}")
        return jsonify({'error': 'Could not fetch movie information'}), 503
        
    try:
        # Create downloads directory if it doesn't exist
        movie_dir = os.path.join(DOWNLOADS_DIR, "Movies")
        os.makedirs(movie_dir, exist_ok=True)
        
        # Start download process in background thread
        def download_worker():
            try:
                # Debug: Log the movie data structure
                logger.debug(f"Movie data structure: {movie_data}")
                
                movie_info = movie_data.get('info', {})
                movie_data_info = movie_data.get('movie_data', {})
                logger.debug(f"Movie info structure: {movie_info}")
                logger.debug(f"Movie data info structure: {movie_data_info}")
                
                # Try to get stream_id from different possible locations
                stream_id = (movie_data_info.get('stream_id') or 
                           movie_info.get('stream_id') or 
                           movie_info.get('id') or 
                           movie_data.get('stream_id') or 
                           movie_data.get('id') or
                           vod_id)  # Use the original vod_id as fallback
                
                logger.debug(f"Resolved stream_id: {stream_id}")
                
                # Get movie name from movie_data section first, then fallback to info
                movie_name = (movie_data_info.get('name') or 
                            movie_info.get('name') or 
                            'Unknown Movie')
                
                # Get container extension from movie_data section first
                container_extension = (movie_data_info.get('container_extension') or 
                                     movie_info.get('container_extension') or 
                                     'mp4')
                
                # Send starting status
                sse_queue.put({
                    'status': 'starting',
                    'message': f'Starting download of {movie_name}...'
                })
                
                # Create a combined info object with all the data
                combined_movie_info = {
                    'name': movie_name,
                    'container_extension': container_extension,
                    'stream_id': stream_id,
                    **movie_info,  # Include all info data
                    **movie_data_info  # Include all movie_data, overriding info if conflicts
                }
                
                output_path = os.path.join(movie_dir, f"{movie_name}.{container_extension}")
                success = download_movie_file(combined_movie_info, output_path, stream_id)
                
                if success:
                    # Send completion message
                    sse_queue.put({
                        'progress': 100,
                        'status': 'complete',
                        'message': 'Movie download completed successfully!'
                    })
                else:
                    sse_queue.put({
                        'status': 'error',
                        'error': 'Movie download failed'
                    })
                
                # Send sentinel to close connection
                sse_queue.put(None)
                
            except Exception as e:
                logger.error(f"Download worker error: {str(e)}")
                sse_queue.put({
                    'status': 'error',
                    'error': str(e),
                    'message': f'Movie download failed: {str(e)}'
                })
                sse_queue.put(None)
        
        thread = threading.Thread(target=download_worker)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Movie download started'
        })
        
    except Exception as e:
        logger.error(f"Movie download error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    if not os.path.exists(DOWNLOADS_DIR):
        os.makedirs(DOWNLOADS_DIR)
    # Add host parameter to make it accessible from other devices on the network
    app.run(debug=True, host='0.0.0.0', port=5000)