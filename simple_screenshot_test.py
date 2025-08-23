#!/usr/bin/env python3
"""
Simple test to verify screenshot service
"""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("Testing screenshot service...")
    
    # Test imports
    from audit_engine.screenshot_service import ScreenshotService
    print("✓ ScreenshotService imported successfully")
    
    # Initialize service
    screenshot_service = ScreenshotService()
    print("✓ ScreenshotService initialized successfully")
    print(f"  Screenshot directory: {screenshot_service.screenshot_dir}")
    
    # Test screenshot capture
    test_url = "https://example.com"
    print(f"\nTesting screenshot capture for: {test_url}")
    
    result = screenshot_service.capture_screenshot(test_url)
    print(f"Result: {result}")
    
    if result.get('success'):
        print("✓ Screenshot captured successfully!")
        print(f"  Filename: {result.get('filename')}")
        print(f"  Method: {result.get('method')}")
        print(f"  Dimensions: {result.get('dimensions')}")
        print(f"  File size: {result.get('file_size')} bytes")
        
        # Check if file exists
        if os.path.exists(result.get('file_path')):
            print("✓ Screenshot file exists on disk")
        else:
            print("✗ Screenshot file not found on disk")
    else:
        print(f"✗ Screenshot failed: {result.get('error')}")
    
    # List existing screenshots
    print(f"\nExisting screenshots in directory:")
    screenshots = screenshot_service.list_screenshots()
    for screenshot in screenshots:
        print(f"  - {screenshot.get('filename')} ({screenshot.get('dimensions')})")
    
    print("\nTest completed!")
    
except Exception as e:
    print(f"Test failed with error: {e}")
    import traceback
    traceback.print_exc()
