import json
import os
import time
from datetime import datetime

# Assuming these functions are available from app.py or a shared utility
# For now, we'll assume they are passed in or imported from a common source.
# In the final implementation, we'll ensure proper import paths.

SERIES_CACHE_FILE = 'cached_series_data.json'
MOVIES_CACHE_FILE = 'cached_movies_data.json'

def get_cached_data(content_type='series'):
    """Loads cached data from a JSON file."""
    cache_file = SERIES_CACHE_FILE if content_type == 'series' else MOVIES_CACHE_FILE
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: Cache file {cache_file} is empty or contains invalid JSON. Returning None.")
            return None
    return None

def save_cached_data(data, content_type='series'):
    """Saves data to a JSON file."""
    cache_file = SERIES_CACHE_FILE if content_type == 'series' else MOVIES_CACHE_FILE
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def process_and_cache_series_data(get_categories_func, get_series_by_category_func, progress_callback=None):
    """Fetches, processes, and caches series data with detailed progress tracking."""
    print("Starting series data caching process...")
    start_time = time.time()
    
    cached_data = {
        "last_fetch_date": datetime.now().isoformat(),
        "categories": [],
        "series": {}
    }

    # Initial progress update
    if progress_callback:
        progress_callback(0, "Initializing caching process...", "starting", {
            'total_categories': 0,
            'processed_categories': 0,
            'total_series': 0,
            'processed_series': 0,
            'failed_series': 0,
            'start_time': start_time
        })

    categories = get_categories_func()
    if not categories:
        print("No categories found to cache.")
        if progress_callback:
            progress_callback(100, "No categories found.", "error", {})
        return False

    total_categories = len(categories)
    total_series_processed = 0
    failed_series_count = 0
    processed_categories = 0

    # Send initial category count
    if progress_callback:
        progress_callback(0, f"Found {total_categories} categories to process", "in_progress", {
            'total_categories': total_categories,
            'processed_categories': 0,
            'total_series': 0,
            'processed_series': 0,
            'failed_series': 0,
            'start_time': start_time
        })

    for i, category in enumerate(categories):
        category_id = category.get("category_id")
        category_name = category.get("category_name")
        
        current_time = time.time()
        elapsed_time = current_time - start_time
        
        if category_id and category_name:
            print(f"Processing category: {category_name} (ID: {category_id})")
            
            # Update progress before processing category
            if progress_callback:
                progress = int((i / total_categories) * 100)
                progress_callback(progress, f"Processing category: {category_name}", "in_progress", {
                    'total_categories': total_categories,
                    'processed_categories': processed_categories,
                    'current_category': category_name,
                    'total_series': total_series_processed,
                    'processed_series': total_series_processed,
                    'failed_series': failed_series_count,
                    'elapsed_time': elapsed_time,
                    'start_time': start_time
                })
            
            series_list = get_series_by_category_func(category_id)
            category_series_count = 0
            
            if series_list:
                for series in series_list:
                    series_id = series.get("series_id")
                    series_name = series.get("name")
                    actors = series.get("cast")
                    plot = series.get("plot")
                    cover_url = series.get("cover")
                    
                    if series_id and series_name:
                        cached_data["series"][str(series_id)] = {
                            "series_name": series_name,
                            "category_ID": category_id,
                            "actors": actors.split(', ') if actors else [],
                            "plot": plot if plot else "",
                            "cover_url": cover_url if cover_url else ""
                        }
                        total_series_processed += 1
                        category_series_count += 1
                        print(f"  Cached series: {series_name} (Total processed: {total_series_processed})")
                    else:
                        failed_series_count += 1
                        print(f"  Skipping series due to missing ID or name: {series} (Failed: {failed_series_count})")
            else:
                print(f"  No series found for category: {category_name}")
            
            processed_categories += 1
            
            # Update progress after processing category
            if progress_callback:
                progress = int(((i + 1) / total_categories) * 100)
                elapsed_time = time.time() - start_time
                avg_time_per_category = elapsed_time / (i + 1) if i > 0 else 0
                eta_seconds = avg_time_per_category * (total_categories - (i + 1))
                
                progress_callback(progress, f"Completed category: {category_name} ({category_series_count} series)", "in_progress", {
                    'total_categories': total_categories,
                    'processed_categories': processed_categories,
                    'current_category': category_name,
                    'category_series_count': category_series_count,
                    'total_series': total_series_processed,
                    'processed_series': total_series_processed,
                    'failed_series': failed_series_count,
                    'elapsed_time': elapsed_time,
                    'eta_seconds': eta_seconds,
                    'avg_time_per_category': avg_time_per_category,
                    'start_time': start_time
                })
        else:
            failed_series_count += 1
            print(f"Skipping category due to missing ID or name: {category}")

    # Save the cached data
    save_cached_data(cached_data)
    
    total_time = time.time() - start_time
    print(f"Caching process completed. Total series processed: {total_series_processed}, Failed series: {failed_series_count}.")
    
    if progress_callback:
        progress_callback(100, f"Caching completed! Processed {total_series_processed} series from {processed_categories} categories", "complete", {
            'total_categories': total_categories,
            'processed_categories': processed_categories,
            'total_series': total_series_processed,
            'processed_series': total_series_processed,
            'failed_series': failed_series_count,
            'total_time': total_time,
            'start_time': start_time
        })
    
    return True

def process_and_cache_movies_data(get_movie_categories_func, get_movies_by_category_func, progress_callback=None):
    """Fetches, processes, and caches movies data with detailed progress tracking."""
    print("Starting movies data caching process...")
    start_time = time.time()
    
    cached_data = {
        "last_fetch_date": datetime.now().isoformat(),
        "categories": [],
        "movies": {}
    }

    # Initial progress update
    if progress_callback:
        progress_callback(0, "Initializing movies caching process...", "starting", {
            'total_categories': 0,
            'processed_categories': 0,
            'total_movies': 0,
            'processed_movies': 0,
            'failed_movies': 0,
            'start_time': start_time
        })

    categories = get_movie_categories_func()
    if not categories:
        print("No movie categories found to cache.")
        if progress_callback:
            progress_callback(100, "No movie categories found.", "error", {})
        return False

    total_categories = len(categories)
    total_movies_processed = 0
    failed_movies_count = 0
    processed_categories = 0

    # Send initial category count
    if progress_callback:
        progress_callback(0, f"Found {total_categories} movie categories to process", "in_progress", {
            'total_categories': total_categories,
            'processed_categories': 0,
            'total_movies': 0,
            'processed_movies': 0,
            'failed_movies': 0,
            'start_time': start_time
        })

    for i, category in enumerate(categories):
        category_id = category.get("category_id")
        category_name = category.get("category_name")
        
        current_time = time.time()
        elapsed_time = current_time - start_time
        
        if category_id and category_name:
            print(f"Processing movie category: {category_name} (ID: {category_id})")
            
            # Update progress before processing category
            if progress_callback:
                progress = int((i / total_categories) * 100)
                progress_callback(progress, f"Processing movie category: {category_name}", "in_progress", {
                    'total_categories': total_categories,
                    'processed_categories': processed_categories,
                    'current_category': category_name,
                    'total_movies': total_movies_processed,
                    'processed_movies': total_movies_processed,
                    'failed_movies': failed_movies_count,
                    'elapsed_time': elapsed_time,
                    'start_time': start_time
                })
            
            movies_list = get_movies_by_category_func(category_id)
            category_movies_count = 0
            
            if movies_list:
                for movie in movies_list:
                    movie_id = movie.get("stream_id") or movie.get("id")
                    movie_name = movie.get("name")
                    actors = movie.get("cast")
                    plot = movie.get("plot")
                    cover_url = movie.get("stream_icon")
                    genre = movie.get("genre")
                    rating = movie.get("rating")
                    year = movie.get("year")
                    
                    if movie_id and movie_name:
                        cached_data["movies"][str(movie_id)] = {
                            "movie_name": movie_name,
                            "category_ID": category_id,
                            "actors": actors.split(', ') if actors else [],
                            "plot": plot if plot else "",
                            "cover_url": cover_url if cover_url else "",
                            "genre": genre if genre else "",
                            "rating": rating if rating else "",
                            "year": year if year else ""
                        }
                        total_movies_processed += 1
                        category_movies_count += 1
                        print(f"  Cached movie: {movie_name} (Total processed: {total_movies_processed})")
                    else:
                        failed_movies_count += 1
                        print(f"  Skipping movie due to missing ID or name: {movie} (Failed: {failed_movies_count})")
            else:
                print(f"  No movies found for category: {category_name}")
            
            processed_categories += 1
            
            # Update progress after processing category
            if progress_callback:
                progress = int(((i + 1) / total_categories) * 100)
                elapsed_time = time.time() - start_time
                avg_time_per_category = elapsed_time / (i + 1) if i > 0 else 0
                eta_seconds = avg_time_per_category * (total_categories - (i + 1))
                
                progress_callback(progress, f"Completed movie category: {category_name} ({category_movies_count} movies)", "in_progress", {
                    'total_categories': total_categories,
                    'processed_categories': processed_categories,
                    'current_category': category_name,
                    'category_movies_count': category_movies_count,
                    'total_movies': total_movies_processed,
                    'processed_movies': total_movies_processed,
                    'failed_movies': failed_movies_count,
                    'elapsed_time': elapsed_time,
                    'eta_seconds': eta_seconds,
                    'avg_time_per_category': avg_time_per_category,
                    'start_time': start_time
                })
        else:
            failed_movies_count += 1
            print(f"Skipping movie category due to missing ID or name: {category}")

    # Save the cached data
    save_cached_data(cached_data, 'movies')
    
    total_time = time.time() - start_time
    print(f"Movies caching process completed. Total movies processed: {total_movies_processed}, Failed movies: {failed_movies_count}.")
    
    if progress_callback:
        progress_callback(100, f"Movies caching completed! Processed {total_movies_processed} movies from {processed_categories} categories", "complete", {
            'total_categories': total_categories,
            'processed_categories': processed_categories,
            'total_movies': total_movies_processed,
            'processed_movies': total_movies_processed,
            'failed_movies': failed_movies_count,
            'total_time': total_time,
            'start_time': start_time
        })
    
    return True

def search_series(query):
    """Searches cached series data for matching series names, actors, or plot."""
    cached_data = get_cached_data('series')
    if not cached_data:
        return [], None

    results = []
    query_lower = query.lower()
    last_fetch_date = cached_data.get("last_fetch_date")

    for series_id, series_data in cached_data.get("series", {}).items():
        series_name_lower = series_data.get('series_name', '').lower()
        actors_lower = ' '.join(series_data.get('actors', [])).lower()
        plot_lower = series_data.get('plot', '').lower()

        if query_lower in series_name_lower or \
           query_lower in actors_lower or \
           query_lower in plot_lower:
            # Add series_id and content_type to the dictionary before appending to results
            series_data['series_id'] = series_id
            series_data['content_type'] = 'series'
            results.append(series_data)
            
    return results, last_fetch_date

def search_movies(query):
    """Searches cached movies data for matching movie names, actors, plot, or genre."""
    cached_data = get_cached_data('movies')
    if not cached_data:
        return [], None

    results = []
    query_lower = query.lower()
    last_fetch_date = cached_data.get("last_fetch_date")

    for movie_id, movie_data in cached_data.get("movies", {}).items():
        movie_name_lower = movie_data.get('movie_name', '').lower()
        actors_lower = ' '.join(movie_data.get('actors', [])).lower()
        plot_lower = movie_data.get('plot', '').lower()
        genre_lower = movie_data.get('genre', '').lower()

        if query_lower in movie_name_lower or \
           query_lower in actors_lower or \
           query_lower in plot_lower or \
           query_lower in genre_lower:
            # Add movie_id and content_type to the dictionary before appending to results
            movie_data['movie_id'] = movie_id
            movie_data['content_type'] = 'movie'
            results.append(movie_data)
            
    return results, last_fetch_date

def search_all_content(query):
    """Searches both series and movies data."""
    series_results, series_date = search_series(query)
    movies_results, movies_date = search_movies(query)
    
    # Combine results
    all_results = series_results + movies_results
    
    # Use the most recent date
    last_fetch_date = None
    if series_date and movies_date:
        last_fetch_date = max(series_date, movies_date)
    elif series_date:
        last_fetch_date = series_date
    elif movies_date:
        last_fetch_date = movies_date
    
    return all_results, last_fetch_date


def get_series_count_by_category():
    """Returns a dictionary mapping category IDs to their series count."""
    cached_data = get_cached_data('series')
    if not cached_data:
        return {}
        
    category_counts = {}
    for series_data in cached_data.get("series", {}).values():
        category_id = series_data.get("category_ID")
        if category_id:
            category_counts[category_id] = category_counts.get(category_id, 0) + 1
            
    return category_counts

def get_movies_count_by_category():
    """Returns a dictionary mapping category IDs to their movies count."""
    cached_data = get_cached_data('movies')
    if not cached_data:
        return {}
        
    category_counts = {}
    for movie_data in cached_data.get("movies", {}).values():
        category_id = movie_data.get("category_ID")
        if category_id:
            category_counts[category_id] = category_counts.get(category_id, 0) + 1
            
    return category_counts