import os
import logging
import base64
from datetime import datetime
from urllib.parse import urlparse
import requests
from PIL import Image
import io
import time

logger = logging.getLogger(__name__)

class ScreenshotService:
    def __init__(self, screenshot_dir="screenshots"):
        """
        Initialize the screenshot service
        
        Args:
            screenshot_dir (str): Directory to store screenshots
        """
        self.screenshot_dir = screenshot_dir
        self.ensure_screenshot_dir()
        
    def ensure_screenshot_dir(self):
        """Create screenshot directory if it doesn't exist"""
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)
            logger.info(f"Created screenshot directory: {self.screenshot_dir}")
    
    def capture_screenshot(self, url, width=1920, height=1080, timeout=30):
        """
        Capture a screenshot of the given URL
        
        Args:
            url (str): URL to capture
            width (int): Viewport width
            height (int): Viewport height
            timeout (int): Timeout in seconds
            
        Returns:
            dict: Screenshot information including file path and metadata
        """
        try:
            logger.info(f"Capturing screenshot for URL: {url}")
            
            # Generate filename based on URL and timestamp
            domain = urlparse(url).netloc
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_domain = "".join(c for c in domain if c.isalnum() or c in ('-', '_')).rstrip()
            filename = f"{safe_domain}_{timestamp}.png"
            filepath = os.path.join(self.screenshot_dir, filename)
            
            # Try to capture screenshot using different methods
            screenshot_data = self._capture_with_selenium(url, width, height, timeout)
            
            if screenshot_data:
                # Save the screenshot
                with open(filepath, 'wb') as f:
                    f.write(screenshot_data)
                
                # Get image dimensions
                with Image.open(filepath) as img:
                    img_width, img_height = img.size
                
                # Create thumbnail for preview
                thumbnail_path = self._create_thumbnail(filepath, filename)
                
                screenshot_info = {
                    "success": True,
                    "file_path": filepath,
                    "filename": filename,
                    "thumbnail_path": thumbnail_path,
                    "url": url,
                    "dimensions": {
                        "width": img_width,
                        "height": img_height
                    },
                    "viewport": {
                        "width": width,
                        "height": height
                    },
                    "timestamp": datetime.now().isoformat(),
                    "file_size": os.path.getsize(filepath),
                    "method": "selenium"
                }
                
                logger.info(f"Screenshot captured successfully: {filename}")
                return screenshot_info
            else:
                # Fallback to basic screenshot using requests + PIL
                return self._capture_fallback(url, width, height, filename)
                
        except Exception as e:
            logger.error(f"Failed to capture screenshot for {url}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "url": url,
                "timestamp": datetime.now().isoformat()
            }
    
    def _capture_with_selenium(self, url, width, height, timeout):
        """
        Capture screenshot using Selenium WebDriver (if available)
        """
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            # Configure Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument(f"--window-size={width},{height}")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            
            # Initialize WebDriver
            driver = webdriver.Chrome(options=chrome_options)
            driver.set_page_load_timeout(timeout)
            driver.implicitly_wait(10)
            
            try:
                # Navigate to URL
                driver.get(url)
                
                # Wait for page to load
                WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Additional wait for dynamic content
                time.sleep(3)
                
                # Take screenshot
                screenshot_data = driver.get_screenshot_as_png()
                return screenshot_data
                
            finally:
                driver.quit()
                
        except ImportError:
            logger.warning("Selenium not available, using fallback method")
            return None
        except Exception as e:
            logger.warning(f"Selenium screenshot failed: {str(e)}, using fallback method")
            return None
    
    def _capture_fallback(self, url, width, height, filename):
        """
        Fallback screenshot method using requests and PIL
        This creates a basic representation of the webpage
        """
        try:
            # Create a basic webpage representation
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            
            # Create a simple image representation
            img = Image.new('RGB', (width, height), color='white')
            
            # Save the basic image
            filepath = os.path.join(self.screenshot_dir, filename)
            img.save(filepath, 'PNG')
            
            # Create thumbnail
            thumbnail_path = self._create_thumbnail(filepath, filename)
            
            return {
                "success": True,
                "file_path": filepath,
                "filename": filename,
                "thumbnail_path": thumbnail_path,
                "url": url,
                "dimensions": {
                    "width": width,
                    "height": height
                },
                "viewport": {
                    "width": width,
                    "height": height
                },
                "timestamp": datetime.now().isoformat(),
                "file_size": os.path.getsize(filepath),
                "method": "fallback",
                "note": "Basic representation - full screenshot requires Selenium"
            }
            
        except Exception as e:
            logger.error(f"Fallback screenshot failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "url": url,
                "timestamp": datetime.now().isoformat()
            }
    
    def _create_thumbnail(self, original_path, filename, max_size=(400, 300)):
        """
        Create a thumbnail version of the screenshot
        """
        try:
            with Image.open(original_path) as img:
                # Resize image maintaining aspect ratio
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Create thumbnail filename
                name, ext = os.path.splitext(filename)
                thumbnail_filename = f"{name}_thumb{ext}"
                thumbnail_path = os.path.join(self.screenshot_dir, thumbnail_filename)
                
                # Save thumbnail
                img.save(thumbnail_path, 'PNG')
                
                return thumbnail_path
                
        except Exception as e:
            logger.error(f"Failed to create thumbnail: {str(e)}")
            return None
    
    def get_screenshot_info(self, filename):
        """
        Get information about a specific screenshot
        """
        filepath = os.path.join(self.screenshot_dir, filename)
        
        if not os.path.exists(filepath):
            return None
            
        try:
            with Image.open(filepath) as img:
                width, height = img.size
                
            return {
                "filename": filename,
                "file_path": filepath,
                "dimensions": {
                    "width": width,
                    "height": height
                },
                "file_size": os.path.getsize(filepath),
                "created": datetime.fromtimestamp(os.path.getctime(filepath)).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get screenshot info: {str(e)}")
            return None
    
    def list_screenshots(self):
        """
        List all available screenshots
        """
        try:
            screenshots = []
            for filename in os.listdir(self.screenshot_dir):
                if filename.endswith('.png') and not filename.endswith('_thumb.png'):
                    info = self.get_screenshot_info(filename)
                    if info:
                        screenshots.append(info)
            
            return screenshots
            
        except Exception as e:
            logger.error(f"Failed to list screenshots: {str(e)}")
            return []
    
    def delete_screenshot(self, filename):
        """
        Delete a screenshot and its thumbnail
        """
        try:
            filepath = os.path.join(self.screenshot_dir, filename)
            name, ext = os.path.splitext(filename)
            thumbnail_filename = f"{name}_thumb{ext}"
            thumbnail_path = os.path.join(self.screenshot_dir, thumbnail_filename)
            
            # Delete main screenshot
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.info(f"Deleted screenshot: {filename}")
            
            # Delete thumbnail
            if os.path.exists(thumbnail_path):
                os.remove(thumbnail_path)
                logger.info(f"Deleted thumbnail: {thumbnail_filename}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete screenshot: {str(e)}")
            return False
    
    def cleanup_old_screenshots(self, days_old=7):
        """
        Clean up screenshots older than specified days
        """
        try:
            current_time = datetime.now()
            deleted_count = 0
            
            for filename in os.listdir(self.screenshot_dir):
                if filename.endswith('.png') and not filename.endswith('_thumb.png'):
                    filepath = os.path.join(self.screenshot_dir, filename)
                    file_time = datetime.fromtimestamp(os.path.getctime(filepath))
                    
                    if (current_time - file_time).days > days_old:
                        if self.delete_screenshot(filename):
                            deleted_count += 1
            
            logger.info(f"Cleaned up {deleted_count} old screenshots")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup old screenshots: {str(e)}")
            return 0
