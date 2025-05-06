import csv
import os
import requests
import time
from playwright.sync_api import sync_playwright

def search_movie(movie_name, csv_file='MovieDB.csv'):
    results = []
    try:
        with open(csv_file, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if movie_name.lower() in row['Movie Name'].lower():
                    results.append({
                        'title': row['Movie Name'],
                        'link': row['URL'],
                        'year': row['Release Year'],
                        'quality': row['Resolution'],
                        'type': row['Quality'],
                    })
    except Exception as e:
        print(f"Error reading CSV: {e}")
    return results

def fetch_real_mp4_url(stream_page_url):
    try:
        import os
        print(f"Checking Playwright browser path: {os.environ.get('PLAYWRIGHT_BROWSERS_PATH', 'Not set')}")
        
        # Create a debug log to verify installation
        try:
            import subprocess
            result = subprocess.run(['ls', '-la', '/home/render/.cache/ms-playwright'], capture_output=True, text=True)
            print(f"Browser directory contents: {result.stdout}")
        except Exception as e:
            print(f"Failed to list browser directory: {e}")
        
        with sync_playwright() as p:
            # More explicit browser launch with additional options
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--disable-gpu',
                    '--disable-dev-shm-usage',
                    '--disable-setuid-sandbox',
                    '--no-sandbox',
                ]
            )
            page = browser.new_page()
            mp4_url = None

            def handle_response(response):
                nonlocal mp4_url
                try:
                    if ".mp4" in response.url:
                        mp4_url = response.url
                        print(f"Found MP4 URL: {mp4_url}")
                except Exception as e:
                    print(f"Error in response handler: {e}")

            page.on("response", handle_response)
            print(f"Opening page: {stream_page_url}")
            
            try:
                page.goto(stream_page_url, timeout=60000)
                # Increase timeout to ensure page loads completely
                page.wait_for_timeout(10000)
                
                # Alternative method to find MP4 URLs in case the response handler misses them
                if not mp4_url:
                    print("Trying alternative MP4 detection method...")
                    # Look for video elements or links that might contain MP4 content
                    video_srcs = page.evaluate('''() => {
                        const videoElements = Array.from(document.querySelectorAll('video source'));
                        return videoElements.map(el => el.src).filter(src => src.includes('.mp4'));
                    }''')
                    
                    if video_srcs and len(video_srcs) > 0:
                        mp4_url = video_srcs[0]
                        print(f"Found MP4 URL through DOM: {mp4_url}")
            except Exception as page_error:
                print(f"Page navigation error: {page_error}")
            
            browser.close()
            return mp4_url
    except Exception as e:
        print(f"Error fetching MP4 URL: {e}")
        return None

def download_mp4(mp4_url, filename, retries=3, progress_callback=None):
    if os.path.exists(filename):
        print(f"File already exists. Skipping: {filename}")
        if progress_callback:
            progress_callback(100)
        return True

    os.makedirs(os.path.dirname(filename), exist_ok=True)

    attempt = 0
    while attempt < retries:
        try:
            with requests.get(mp4_url, stream=True, timeout=30) as r:
                if "text/html" in r.headers.get("Content-Type", ""):
                    print("Error: Link returned an HTML page instead of a video file!")
                    return False
                    
                total_length = int(r.headers.get('content-length', 0))
                downloaded = 0

                with open(filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if progress_callback and total_length:
                                progress = min(int(downloaded * 100 / total_length), 100)
                                progress_callback(progress)

            print(f"Download complete: {filename}")
            return True

        except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
            attempt += 1
            print(f"Network error, retrying ({attempt}/{retries})...")
            time.sleep(2)

    print("Failed to download after multiple retries.")
    return False