#!/usr/bin/env python3
"""
Test script to debug screenshot service
"""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("Testing screenshot service...")
    
    # Test imports
    print("1. Testing imports...")
    from audit_engine.screenshot_service import ScreenshotService
    print("   ✓ ScreenshotService imported successfully")
    
    # Test PIL
    try:
        from PIL import Image
        print("   ✓ PIL (Pillow) imported successfully")
    except ImportError as e:
        print(f"   ✗ PIL import failed: {e}")
    
    # Test Selenium
    try:
        from selenium import webdriver
        print("   ✓ Selenium imported successfully")
    except ImportError as e:
        print(f"   ✗ Selenium import failed: {e}")
    
    # Test requests
    try:
        import requests
        print("   ✓ Requests imported successfully")
    except ImportError as e:
        print(f"   ✗ Requests import failed: {e}")
    
    # Initialize service
    print("\n2. Initializing screenshot service...")
    try:
        screenshot_service = ScreenshotService()
        print("   ✓ ScreenshotService initialized successfully")
        print(f"   Screenshot directory: {screenshot_service.screenshot_dir}")
    except Exception as e:
        print(f"   ✗ ScreenshotService initialization failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Test screenshot capture
    print("\n3. Testing screenshot capture...")
    test_url = "https://example.com"
    print(f"   Testing with URL: {test_url}")
    
    try:
        result = screenshot_service.capture_screenshot(test_url)
        print(f"   Screenshot result: {result}")
        
        if result.get('success'):
            print("   ✓ Screenshot captured successfully!")
            print(f"   Filename: {result.get('filename')}")
            print(f"   Method: {result.get('method')}")
            print(f"   Dimensions: {result.get('dimensions')}")
        else:
            print(f"   ✗ Screenshot failed: {result.get('error')}")
            
    except Exception as e:
        print(f"   ✗ Screenshot capture failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n4. Testing screenshot directory...")
    try:
        screenshots = screenshot_service.list_screenshots()
        print(f"   Found {len(screenshots)} screenshots in directory")
        for screenshot in screenshots:
            print(f"   - {screenshot.get('filename')} ({screenshot.get('dimensions')})")
    except Exception as e:
        print(f"   ✗ Failed to list screenshots: {e}")
    
    print("\nTest completed!")
    
except Exception as e:
    print(f"Test failed with error: {e}")
    import traceback
    traceback.print_exc()
