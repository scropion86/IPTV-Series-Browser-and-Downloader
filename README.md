# IPTV Series Downloader

This project is a web-based application built with Flask that allows you to browse, search, and download series from an IPTV provider. It features a user-friendly interface for navigating categories, viewing series details, and managing downloads.

## Purpose

The main purpose of this application is to provide a convenient way to access and download series content from an IPTV service, offering features such as:

-   **Category Browsing**: Easily navigate through different series categories.
-   **Series Information**: View detailed information about each series, including plot and cast.
-   **Episode Selection**: Select specific seasons and episodes for download.
-   **Background Caching**: Cache series data to improve performance and reduce API calls.
-   **Real-time Progress**: Monitor download and caching progress with real-time updates.
-   **Search Functionality**: Search for series by name, actors, or plot.

## Requirements

To run this application, you will need:

-   Python 3.x
-   `pip` (Python package installer)
-   An IPTV provider API (configured in `config.py`)

### Python Packages

The following Python packages are required. You can install them using `pip`:

-   `Flask`
-   `requests`
-   `urllib3`
-   `tqdm`
-   `aiohttp`

You can install all required packages by running:

```bash
pip install Flask requests urllib3 tqdm aiohttp
```

## How to Use

Follow these steps to set up and run the application:

### 1. Configuration

Before running the application, you need to configure your IPTV provider's API details in `config.py`.

Open `config.py` and update the following variables with your IPTV credentials:

```python:config.py
BASE_URL = "YOUR_IPTV_API_BASE_URL" # e.g.,
USERNAME = "YOUR_USERNAME"
PASSWORD = "YOUR_PASSWORD"
```

### 2. Run the Application

Navigate to the project's root directory in your terminal and run the `app.py` file:

```bash
python app.py
```

Alternatively, you can use the provided `run_app.bat` (for Windows) to start the application:

```bash
run_app.bat
```

### 3. Access the Web Interface

Once the application is running, open your web browser and go to `http://127.0.0.1:5000/` (or the address displayed in your terminal).

### 4. Caching Data

For optimal performance, it is recommended to cache the series data. On the search page, click the "Process and Cache Data" button to initiate the caching process. This will fetch all series information from your IPTV provider and store it locally.

### 5. Browsing and Downloading

-   **Browse Categories**: On the main page, click on any category to view the series within it.
-   **Search Series**: Use the search bar on the search page to find specific series.
-   **Download Episodes**: From a series detail page, select the season and episode range you wish to download. The download progress will be displayed in real-time.

## Project Structure

-   `app.py`: The main Flask application, handling routes, API interactions, and rendering templates.
-   `cache_manager.py`: Manages caching of series data, including fetching, saving, and searching cached content.
-   `config.py`: Stores sensitive configuration details like API credentials.
-   `static/`: Contains static files like CSS (`style.css`).
-   `templates/`: Stores HTML templates (`index.html`, `search.html`, `download.html`, etc.).
-   `downloads/`: Directory where downloaded series episodes are saved.