#!/usr/bin/env python3
"""
Simple test script for the audit engine components
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if we can import the modules"""
    try:
        print("Testing imports...")
        
        # Test basic imports
        import requests
        print("✓ requests imported successfully")
        
        from bs4 import BeautifulSoup
        print("✓ BeautifulSoup imported successfully")
        
        # Test our modules
        from audit_engine.lighthouse_api import LighthouseAPI
        print("✓ LighthouseAPI imported successfully")
        
        from audit_engine.performance_analyzer import PerformanceAnalyzer
        print("✓ PerformanceAnalyzer imported successfully")
        
        print("\nAll imports successful!")
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def test_lighthouse_creation():
    """Test if we can create Lighthouse API instance"""
    try:
        print("\nTesting Lighthouse API creation...")
        
        from audit_engine.lighthouse_api import LighthouseAPI
        lighthouse = LighthouseAPI()
        print("✓ LighthouseAPI instance created successfully")
        
        # Test basic methods
        methods = [method for method in dir(lighthouse) if not method.startswith('_')]
        print(f"✓ Available methods: {len(methods)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Lighthouse API creation failed: {e}")
        return False

def test_performance_analyzer_creation():
    """Test if we can create Performance Analyzer instance"""
    try:
        print("\nTesting Performance Analyzer creation...")
        
        from audit_engine.performance_analyzer import PerformanceAnalyzer
        analyzer = PerformanceAnalyzer()
        print("✓ PerformanceAnalyzer instance created successfully")
        
        # Test basic methods
        methods = [method for method in dir(analyzer) if not method.startswith('_')]
        print(f"✓ Available methods: {len(methods)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Performance Analyzer creation failed: {e}")
        return False

def main():
    """Main test function"""
    print("SitePulse Audit Engine - Simple Test")
    print("=" * 40)
    
    success = True
    
    # Test 1: Imports
    if not test_imports():
        success = False
    
    # Test 2: Lighthouse API
    if success and not test_lighthouse_creation():
        success = False
    
    # Test 3: Performance Analyzer
    if success and not test_performance_analyzer_creation():
        success = False
    
    print("\n" + "=" * 40)
    if success:
        print("✓ All tests passed! Audit engine is ready.")
    else:
        print("✗ Some tests failed. Check the errors above.")
    
    return success

if __name__ == "__main__":
    main()
