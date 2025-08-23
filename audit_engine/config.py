"""
Configuration file for SitePulse Audit Engine
"""

import os
from typing import Dict, Any

class AuditConfig:
    """Configuration class for the audit engine"""
    
    def __init__(self):
        # API Configuration
        self.lighthouse_api_key = os.getenv('LIGHTHOUSE_API_KEY', None)
        self.lighthouse_base_url = os.getenv('LIGHTHOUSE_BASE_URL', 'https://www.googleapis.com/pagespeedonline/v5/runPagespeed')
        
        # Timeout Configuration
        self.request_timeout = int(os.getenv('REQUEST_TIMEOUT', 30))
        self.lighthouse_timeout = int(os.getenv('LIGHTHOUSE_TIMEOUT', 30))
        
        # Rate Limiting
        self.max_requests_per_minute = int(os.getenv('MAX_REQUESTS_PER_MINUTE', 60))
        self.retry_attempts = int(os.getenv('RETRY_ATTEMPTS', 3))
        self.retry_delay = int(os.getenv('RETRY_DELAY', 5))
        
        # Performance Thresholds
        self.slow_load_threshold = int(os.getenv('SLOW_LOAD_THRESHOLD', 3000))  # 3 seconds
        self.large_page_threshold = int(os.getenv('LARGE_PAGE_THRESHOLD', 2000000))  # 2MB
        self.max_requests_threshold = int(os.getenv('MAX_REQUESTS_THRESHOLD', 100))
        
        # Core Web Vitals Thresholds
        self.lcp_good_threshold = int(os.getenv('LCP_GOOD_THRESHOLD', 2500))  # 2.5 seconds
        self.lcp_needs_improvement_threshold = int(os.getenv('LCP_NEEDS_IMPROVEMENT_THRESHOLD', 4000))  # 4 seconds
        
        self.fid_good_threshold = int(os.getenv('FID_GOOD_THRESHOLD', 100))  # 100ms
        self.fid_needs_improvement_threshold = int(os.getenv('FID_NEEDS_IMPROVEMENT_THRESHOLD', 300))  # 300ms
        
        self.cls_good_threshold = float(os.getenv('CLS_GOOD_THRESHOLD', 0.1))
        self.cls_needs_improvement_threshold = float(os.getenv('CLS_NEEDS_IMPROVEMENT_THRESHOLD', 0.25))
        
        self.fcp_good_threshold = int(os.getenv('FCP_GOOD_THRESHOLD', 1800))  # 1.8 seconds
        self.fcp_needs_improvement_threshold = int(os.getenv('FCP_NEEDS_IMPROVEMENT_THRESHOLD', 3000))  # 3 seconds
        
        # Resource Analysis
        self.large_image_threshold = int(os.getenv('LARGE_IMAGE_THRESHOLD', 500000))  # 500KB
        self.large_script_threshold = int(os.getenv('LARGE_SCRIPT_THRESHOLD', 100000))  # 100KB
        self.large_css_threshold = int(os.getenv('LARGE_CSS_THRESHOLD', 50000))  # 50KB
        
        # User Agent
        self.user_agent = os.getenv('USER_AGENT', 'SitePulse-AuditEngine/2.0 (https://sitepulse.com)')
        
        # Logging
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.log_format = os.getenv('LOG_FORMAT', 
                                  '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    def get_lighthouse_config(self) -> Dict[str, Any]:
        """Get Lighthouse-specific configuration"""
        return {
            'api_key': self.lighthouse_api_key,
            'base_url': self.lighthouse_base_url,
            'timeout': self.lighthouse_timeout,
            
            'max_requests_per_minute': self.max_requests_per_minute,
            'retry_attempts': self.retry_attempts,
            'retry_delay': self.retry_delay
        }
    
    def get_performance_thresholds(self) -> Dict[str, Any]:
        """Get performance threshold configuration"""
        return {
            'slow_load_threshold': self.slow_load_threshold,
            'large_page_threshold': self.large_page_threshold,
            'max_requests_threshold': self.max_requests_threshold,
            'large_image_threshold': self.large_image_threshold,
            'large_script_threshold': self.large_script_threshold,
            'large_css_threshold': self.large_css_threshold
        }
    
    def get_core_web_vitals_thresholds(self) -> Dict[str, Any]:
        """Get Core Web Vitals threshold configuration"""
        return {
            'lcp': {
                'good': self.lcp_good_threshold,
                'needs_improvement': self.lcp_needs_improvement_threshold
            },
            'fid': {
                'good': self.fid_good_threshold,
                'needs_improvement': self.fid_needs_improvement_threshold
            },
            'cls': {
                'good': self.cls_good_threshold,
                'needs_improvement': self.cls_needs_improvement_threshold
            },
            'fcp': {
                'good': self.fcp_good_threshold,
                'needs_improvement': self.fcp_needs_improvement_threshold
            }
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'lighthouse': self.get_lighthouse_config(),
            'performance_thresholds': self.get_performance_thresholds(),
            'core_web_vitals_thresholds': self.get_core_web_vitals_thresholds(),
            'request_timeout': self.request_timeout,
            'user_agent': self.user_agent,
            'log_level': self.log_level,
            'log_format': self.log_format
        }

# Global configuration instance
config = AuditConfig()
