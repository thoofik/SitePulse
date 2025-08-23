#!/usr/bin/env python3
"""
Test script for the new SitePulse audit engine
"""

import logging
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from audit_engine.performance_analyzer import PerformanceAnalyzer
from audit_engine.lighthouse_api import LighthouseAPI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_lighthouse_api():
    """Test the Lighthouse API directly"""
    print("Testing Lighthouse API...")
    
    lighthouse = LighthouseAPI()
    
    # Test with a simple URL
    test_url = "https://example.com"
    
    try:
        results = lighthouse.analyze_url(test_url, categories=['performance'], strategy='desktop')
        
        print(f"Lighthouse analysis completed for {test_url}")
        print(f"Data source: {results.get('data_source', 'unknown')}")
        print(f"Fallback used: {results.get('fallback_used', False)}")
        
        if results.get("error"):
            print(f"Error: {results['error']}")
        else:
            print(f"Performance score: {results.get('categories', {}).get('performance', {}).get('score', 'N/A')}")
            print(f"Core Web Vitals: {len(results.get('core_web_vitals', {}))} metrics found")
            print(f"Opportunities: {len(results.get('opportunities', []))} found")
        
        return results
        
    except Exception as e:
        print(f"Lighthouse API test failed: {str(e)}")
        return None

def test_performance_analyzer():
    """Test the performance analyzer"""
    print("\nTesting Performance Analyzer...")
    
    analyzer = PerformanceAnalyzer()
    
    # Test with a simple URL
    test_url = "https://example.com"
    
    try:
        results = analyzer.analyze(test_url)
        
        print(f"Performance analysis completed for {test_url}")
        print(f"Overall score: {results.get('score', 'N/A')}")
        print(f"Data sources: {results.get('details', {}).get('data_sources', [])}")
        print(f"Issues found: {len(results.get('issues', []))}")
        print(f"Warnings: {len(results.get('warnings', []))}")
        print(f"Recommendations: {len(results.get('recommendations', []))}")
        
        # Show some metrics
        metrics = results.get('metrics', {})
        print(f"Load time: {metrics.get('load_time', 'N/A')}ms")
        print(f"Page size: {metrics.get('page_size', 'N/A')} bytes")
        print(f"Requests: {metrics.get('requests_count', 'N/A')}")
        
        return results
        
    except Exception as e:
        print(f"Performance analyzer test failed: {str(e)}")
        return None

def test_core_web_vitals():
    """Test Core Web Vitals extraction"""
    print("\nTesting Core Web Vitals...")
    
    lighthouse = LighthouseAPI()
    test_url = "https://example.com"
    
    try:
        results = lighthouse.analyze_url(test_url, categories=['performance'], strategy='desktop')
        
        if not results.get("error"):
            core_vitals = results.get("core_web_vitals", {})
            
            print("Core Web Vitals found:")
            for metric, data in core_vitals.items():
                if isinstance(data, dict):
                    value = data.get("value", "N/A")
                    rating = data.get("rating", "N/A")
                    note = data.get("note", "")
                    print(f"  {metric.upper()}: {value} ({rating}) {note}")
                else:
                    print(f"  {metric.upper()}: {data}")
        else:
            print(f"Could not get Core Web Vitals: {results['error']}")
            
    except Exception as e:
        print(f"Core Web Vitals test failed: {str(e)}")

def main():
    """Main test function"""
    print("SitePulse Audit Engine Test")
    print("=" * 40)
    
    # Test 1: Lighthouse API
    lighthouse_results = test_lighthouse_api()
    
    # Test 2: Performance Analyzer
    performance_results = test_performance_analyzer()
    
    # Test 3: Core Web Vitals
    test_core_web_vitals()
    
    print("\n" + "=" * 40)
    print("Test Summary:")
    
    if lighthouse_results and not lighthouse_results.get("error"):
        print("✓ Lighthouse API: Working")
    else:
        print("✗ Lighthouse API: Failed or using fallback")
    
    if performance_results:
        print("✓ Performance Analyzer: Working")
        print(f"  Final score: {performance_results.get('score', 'N/A')}")
    else:
        print("✗ Performance Analyzer: Failed")
    
    print("\nAudit engine test completed!")

if __name__ == "__main__":
    main()
