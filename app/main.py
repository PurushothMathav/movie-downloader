from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import csv
import os
import requests
import time
import uuid
from datetime import datetime
from threading import Thread
from .utils import search_movie, fetch_real_mp4_url, download_mp4

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev_secret_key')

# Track download progress
download_tasks = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    movie_name = request.form.get('movie_name', '')
    if not movie_name:
        return jsonify({'error': 'Movie name is required'}), 400
    
    csv_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'MovieDB.csv')
    results = search_movie(movie_name, csv_file)
    
    return jsonify({'results': results})

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    title = request.form.get('title')
    quality = request.form.get('quality', 'HD')
    
    if not url or not title:
        return jsonify({'error': 'URL and title are required'}), 400
    
    # Generate a unique ID for this download
    download_id = str(uuid.uuid4())
    safe_title = title.replace('/', '_').replace('\\', '_')
    filename = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                           "downloads", f"{safe_title} {quality}.mp4")
    
    # Create downloads directory if it doesn't exist
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Start download in background
    download_tasks[download_id] = {
        'filename': filename,
        'title': title,
        'status': 'fetching',
        'progress': 0,
        'start_time': datetime.now().isoformat()
    }
    
    Thread(target=start_download, args=(download_id, url, filename)).start()
    
    return jsonify({
        'download_id': download_id,
        'message': 'Download started',
        'status': 'fetching'
    })

@app.route('/download-status/<download_id>')
def download_status(download_id):
    if download_id not in download_tasks:
        return jsonify({'error': 'Download not found'}), 404
    
    return jsonify(download_tasks[download_id])

def start_download(download_id, url, filename):
    try:
        download_tasks[download_id]['status'] = 'fetching_mp4'
        real_mp4_url = fetch_real_mp4_url(url)
        
        if not real_mp4_url:
            download_tasks[download_id]['status'] = 'error'
            download_tasks[download_id]['error'] = 'No MP4 link found'
            return
        
        download_tasks[download_id]['status'] = 'downloading'
        download_tasks[download_id]['mp4_url'] = real_mp4_url
        
        # Start actual download
        success = download_mp4(real_mp4_url, filename, progress_callback=lambda progress: update_progress(download_id, progress))
        
        if success:
            download_tasks[download_id]['status'] = 'completed'
            download_tasks[download_id]['progress'] = 100
        else:
            download_tasks[download_id]['status'] = 'error'
            download_tasks[download_id]['error'] = 'Download failed'
    
    except Exception as e:
        download_tasks[download_id]['status'] = 'error'
        download_tasks[download_id]['error'] = str(e)

def update_progress(download_id, progress):
    if download_id in download_tasks:
        download_tasks[download_id]['progress'] = progress

if __name__ == '__main__':
    app.run(debug=True)