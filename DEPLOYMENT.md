# Deployment Guide for Movie Downloader

This guide provides detailed instructions for deploying the Movie Downloader application on Render.

## Prerequisites

1. GitHub account
2. Render account
3. Your movie database CSV file

## Step 1: Push to GitHub

1. Create a new GitHub repository
2. Initialize your local repository and push to GitHub:

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/movie-downloader.git
git push -u origin main
```

## Step 2: Deploy on Render

### Option 1: Deploy Using render.yaml (Recommended)

1. Log in to your Render account
2. Navigate to the "Blueprints" section
3. Click "New Blueprint Instance"
4. Connect to your GitHub repository
5. Render will automatically detect the render.yaml file and set up the service

### Option 2: Manual Setup

1. Log in to your Render account
2. Click "New" and select "Web Service"
3. Connect to your GitHub repository
4. Configure the following settings:
   - **Name**: movie-downloader
   - **Environment**: Python
   - **Region**: Choose the region closest to your users
   - **Branch**: main
   - **Build Command**: `pip install -r requirements.txt && python -m playwright install chromium --with-deps`
   - **Start Command**: `gunicorn wsgi:app`

5. Add the following environment variables:
   - `SECRET_KEY`: Generate a secure random key
   - `PLAYWRIGHT_BROWSERS_PATH`: `/home/render/.cache/ms-playwright`
   - `PYTHONPATH`: `.`

6. Add a disk:
   - **Name**: movie-data
   - **Mount Path**: `/opt/render/project/src/downloads`
   - **Size**: 10 GB

7. Click "Create Web Service"

## Step 3: Verify Playwright Installation

1. After deployment, navigate to the "Shell" tab in your Render dashboard
2. Run the Playwright test script:

```bash
python test_playwright.py
```

3. If the test is successful, Playwright is properly installed

## Step 4: Upload Movie Database

1. Create the data directory:

```bash
mkdir -p data
```

2. Upload your MovieDB.csv file:

```bash
cd data
# You can use the Render file upload feature or curl to upload your CSV
```

## Troubleshooting

### Issue: "Error fetching MP4 URL"

If you see this error in your logs, try these solutions:

1. Verify Playwright installation:

```bash
python -m playwright install chromium --with-deps
```

2. Check if the browser binary exists:

```bash
ls -la /home/render/.cache/ms-playwright
```

3. Update the Playwright browser path:

```bash
export PLAYWRIGHT_BROWSERS_PATH=/home/render/.cache/ms-playwright
```

4. If problems persist, try deploying the application with the `--force-install-dependencies` flag in your build command:

```
pip install -r requirements.txt && python -m playwright install chromium --with-deps --force-install-dependencies
```

### Issue: "No MP4 link found"

This could be due to one of the following reasons:

1. The website structure changed and the MP4 detection is no longer working
2. The website uses a different video format or delivery method
3. The website has anti-scraping measures in place

Update the fetch_real_mp4_url function in utils.py to adapt to the specific website's structure.

## Maintaining Your Application

1. Regularly update your dependencies:

```bash
pip install --upgrade -r requirements.txt
```

2. Monitor your application logs in the Render dashboard
3. Adjust disk space as needed as your movie collection grows