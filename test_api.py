#!/usr/bin/env python3
"""
Test script to test the screenshot API endpoint
"""
import requests
import json

def test_screenshot_api():
    url = "http://localhost:5000/api/screenshot"
    data = {
        "url": "https://example.com",
        "width": 1920,
        "height": 1080
    }
    
    try:
        print("Testing screenshot API endpoint...")
        print(f"URL: {url}")
        print(f"Data: {json.dumps(data, indent=2)}")
        
        response = requests.post(url, json=data, timeout=30)
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Success! Response: {json.dumps(result, indent=2)}")
            
            if result.get('success'):
                print(f"📸 Screenshot captured: {result.get('filename')}")
                print(f"📏 Dimensions: {result.get('dimensions')}")
                print(f"💾 File size: {result.get('file_size')} bytes")
                print(f"🔧 Method: {result.get('method')}")
            else:
                print(f"❌ Screenshot failed: {result.get('error')}")
        else:
            print(f"\n❌ Error! Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Could not connect to the Flask app")
        print("Make sure the Flask app is running on http://localhost:5000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_screenshot_api()
