# Movie Downloader

A web application for searching and downloading movies.

## Features

- Search for movies from a database
- Download movies in different quality formats
- Track download progress
- Responsive web interface

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/movie-downloader.git
   cd movie-downloader
   ```

2. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Install Playwright browsers:
   ```
   python -m playwright install chromium
   ```

4. Place your MovieDB.csv file in the data/ directory.

5. Run the application locally:
   ```
   flask run
   ```

## Data Format

The application expects a CSV file with the following columns:
- Movie Name
- URL
- Release Year
- Resolution
- Quality

## Deployment

This application is configured for deployment on Render. See the render.yaml file for configuration details.

## Environment Variables

- `SECRET_KEY`: Secret key for Flask session
- `PLAYWRIGHT_BROWSERS_PATH`: Path for Playwright browsers

## License

This project is licensed under the MIT License - see the LICENSE file for details.