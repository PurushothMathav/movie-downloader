#!/usr/bin/env python3

import os
import sys
import subprocess
from playwright.sync_api import sync_playwright

def test_playwright_installation():
    """Test if Playwright is correctly installed and can launch a browser."""
    print("Testing Playwright installation...")
    
    # 1. Check environment variables
    playwright_path = os.environ.get('PLAYWRIGHT_BROWSERS_PATH', 'Not set')
    print(f"PLAYWRIGHT_BROWSERS_PATH: {playwright_path}")
    
    # 2. Check if the directory exists
    if os.path.exists(playwright_path):
        print(f"Directory exists: {playwright_path}")
        try:
            files = os.listdir(playwright_path)
            print(f"Directory contents: {files}")
        except Exception as e:
            print(f"Error listing directory: {e}")
    else:
        print(f"Directory does not exist: {playwright_path}")
    
    # 3. Try to launch browser
    print("Attempting to launch browser...")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--disable-gpu',
                    '--disable-dev-shm-usage',
                    '--disable-setuid-sandbox',
                    '--no-sandbox',
                ]
            )
            print("Browser launched successfully!")
            
            # Test basic page navigation
            page = browser.new_page()
            print("Created new page")
            
            # Test navigating to a simple page
            print("Navigating to example.com...")
            page.goto("https://example.com/")
            print(f"Page title: {page.title()}")
            
            browser.close()
            print("Browser closed successfully")
            return True
    except Exception as e:
        print(f"Error launching browser: {e}")
        return False

if __name__ == "__main__":
    success = test_playwright_installation()
    if success:
        print("Playwright test completed successfully!")
        sys.exit(0)
    else:
        print("Playwright test failed!")
        sys.exit(1)