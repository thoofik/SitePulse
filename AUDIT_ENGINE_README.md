# SitePulse Audit Engine v2.0

## Overview

The SitePulse Audit Engine has been completely rebuilt from scratch to provide more robust, reliable, and comprehensive website auditing capabilities. The new engine addresses the previous Lighthouse API failures by implementing multiple fallback strategies and local analysis methods.

## Key Features

### 🚀 **Multi-Source Data Collection**
- **Primary**: Google Lighthouse API via PageSpeed Insights
- **Fallback**: Alternative Lighthouse API endpoints
- **Local Analysis**: Comprehensive local performance analysis when APIs fail
- **Hybrid Scoring**: Combines multiple data sources for accurate results

### 🔧 **Robust Error Handling**
- Graceful degradation when external APIs fail
- Automatic fallback to local analysis methods
- Detailed error logging and reporting
- Rate limit handling and retry mechanisms

### 📊 **Enhanced Core Web Vitals**
- **LCP (Largest Contentful Paint)**: Server response optimization insights
- **FID (First Input Delay)**: Interaction responsiveness metrics
- **CLS (Cumulative Layout Shift)**: Visual stability analysis
- **FCP (First Contentful Paint)**: Initial rendering performance

### 🎯 **Comprehensive Performance Analysis**
- Page load timing and redirect analysis
- Resource size and optimization opportunities
- Image, script, and CSS optimization recommendations
- CDN detection and caching analysis

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Performance  │    │   Lighthouse     │    │   Local        │
│   Analyzer     │◄──►│   API Client     │◄──►│   Analysis     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Core Web     │    │   Fallback       │    │   Resource      │
│   Vitals       │    │   APIs           │    │   Analysis      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Components

### 1. **LighthouseAPI** (`audit_engine/lighthouse_api.py`)
- **Primary API**: Google PageSpeed Insights
- **Fallback APIs**: Multiple alternative endpoints
- **Local Analysis**: Comprehensive fallback when APIs fail
- **Smart Fallback**: Automatic switching between data sources

### 2. **PerformanceAnalyzer** (`audit_engine/performance_analyzer.py`)
- **Multi-Source Integration**: Combines Lighthouse and local data
- **Resource Analysis**: Images, scripts, CSS, fonts
- **Optimization Detection**: Identifies improvement opportunities
- **Hybrid Scoring**: Weighted combination of multiple data sources

### 3. **Configuration** (`audit_engine/config.py`)
- **Environment Variables**: Configurable thresholds and settings
- **API Keys**: Secure credential management
- **Thresholds**: Customizable performance benchmarks
- **Rate Limiting**: Configurable request limits

## Installation

### Prerequisites
```bash
pip install -r requirements.txt
```

### Environment Variables (Optional)
```bash
# Lighthouse API Configuration
export LIGHTHOUSE_API_KEY="your_api_key_here"
export LIGHTHOUSE_BASE_URL="https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

# Performance Thresholds
export SLOW_LOAD_THRESHOLD=3000
export LARGE_PAGE_THRESHOLD=2000000
export MAX_REQUESTS_THRESHOLD=100

# Core Web Vitals Thresholds
export LCP_GOOD_THRESHOLD=2500
export FID_GOOD_THRESHOLD=100
export CLS_GOOD_THRESHOLD=0.1
export FCP_GOOD_THRESHOLD=1800
```

## Usage

### Basic Usage
```python
from audit_engine.performance_analyzer import PerformanceAnalyzer

analyzer = PerformanceAnalyzer()
results = analyzer.analyze("https://example.com")

print(f"Performance Score: {results['score']}")
print(f"Core Web Vitals: {results['details']['core_web_vitals']}")
print(f"Recommendations: {len(results['recommendations'])}")
```

### Direct Lighthouse API Usage
```python
from audit_engine.lighthouse_api import LighthouseAPI

lighthouse = LighthouseAPI()
results = lighthouse.analyze_url("https://example.com", categories=['performance'])

if results.get("error"):
    print(f"Using fallback: {results.get('data_source')}")
else:
    print(f"Lighthouse score: {results['categories']['performance']['score']}")
```

## Testing

Run the test script to verify the audit engine:
```bash
python test_audit_engine.py
```

## Data Sources

### 1. **Lighthouse API (Primary)**
- **Source**: Google PageSpeed Insights
- **Data**: Official Core Web Vitals, opportunities, diagnostics
- **Fallback**: Automatic retry and alternative endpoints

### 2. **Local Analysis (Fallback)**
- **Page Load**: Response time, status codes, redirects
- **Resources**: File sizes, optimization opportunities
- **Core Web Vitals**: Estimated from local metrics
- **Optimization**: Image, script, and CSS analysis

### 3. **Hybrid Scoring**
- **Lighthouse Weight**: 70% when available
- **Local Weight**: 30% as supplement
- **Fallback**: 100% local when APIs fail

## Core Web Vitals

### **LCP (Largest Contentful Paint)**
- **Good**: ≤ 2.5 seconds
- **Needs Improvement**: 2.5 - 4.0 seconds
- **Poor**: > 4.0 seconds

### **FID (First Input Delay)**
- **Good**: ≤ 100ms
- **Needs Improvement**: 100 - 300ms
- **Poor**: > 300ms

### **CLS (Cumulative Layout Shift)**
- **Good**: ≤ 0.1
- **Needs Improvement**: 0.1 - 0.25
- **Poor**: > 0.25

### **FCP (First Contentful Paint)**
- **Good**: ≤ 1.8 seconds
- **Needs Improvement**: 1.8 - 3.0 seconds
- **Poor**: > 3.0 seconds

## Performance Metrics

### **Page Load Analysis**
- Total load time
- DNS resolution time
- Connection establishment
- Server response time
- Content transfer time
- Redirect count

### **Resource Analysis**
- Total page size
- Request count
- Image optimization
- Script optimization
- CSS optimization
- Font optimization

### **Optimization Opportunities**
- Unused CSS/JavaScript
- Large resource files
- Missing compression
- Render-blocking resources
- Image format optimization
- Minification status

## Error Handling

### **API Failures**
- Automatic retry with exponential backoff
- Fallback to alternative endpoints
- Graceful degradation to local analysis
- Detailed error logging and reporting

### **Rate Limiting**
- Configurable request limits
- Automatic throttling
- Queue management for high-volume usage

### **Network Issues**
- Timeout handling
- Connection error recovery
- Partial result processing

## Configuration Options

### **Performance Thresholds**
```python
# Load time thresholds
SLOW_LOAD_THRESHOLD = 3000  # 3 seconds

# Page size thresholds
LARGE_PAGE_THRESHOLD = 2000000  # 2MB

# Resource thresholds
LARGE_IMAGE_THRESHOLD = 500000  # 500KB
LARGE_SCRIPT_THRESHOLD = 100000  # 100KB
LARGE_CSS_THRESHOLD = 50000  # 50KB
```

### **API Configuration**
```python
# Timeout settings
REQUEST_TIMEOUT = 30
LIGHTHOUSE_TIMEOUT = 30

# Rate limiting
MAX_REQUESTS_PER_MINUTE = 60
RETRY_ATTEMPTS = 3
RETRY_DELAY = 5
```

## Troubleshooting

### **Common Issues**

1. **Lighthouse API Failures**
   - Check API key validity
   - Verify rate limits
   - Check network connectivity
   - Review error logs

2. **Local Analysis Issues**
   - Verify URL accessibility
   - Check firewall settings
   - Review timeout configurations

3. **Performance Issues**
   - Monitor resource usage
   - Check rate limiting settings
   - Review timeout values

### **Debug Mode**
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable detailed logging
logger = logging.getLogger('audit_engine')
logger.setLevel(logging.DEBUG)
```

## Migration from v1.0

### **Breaking Changes**
- New class structure and method signatures
- Enhanced error handling and fallback mechanisms
- Improved Core Web Vitals extraction
- Better resource analysis capabilities

### **Upgrade Path**
1. Update import statements
2. Review configuration settings
3. Test with new error handling
4. Update custom implementations

## Contributing

### **Development Setup**
```bash
git clone <repository>
cd sitepulse-audit-engine
pip install -r requirements.txt
python test_audit_engine.py
```

### **Code Standards**
- Follow PEP 8 style guidelines
- Include comprehensive docstrings
- Add unit tests for new features
- Update documentation for changes

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Review the troubleshooting section
- Check the configuration options
- Enable debug logging for detailed information
