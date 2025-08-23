import requests
import json
import logging
import time
from datetime import datetime
from urllib.parse import urlparse
import re

logger = logging.getLogger(__name__)

class LighthouseAPI:
    def __init__(self, api_key=None):
        """
        Initialize Lighthouse API client with multiple fallback strategies
        """
        self.api_key = api_key
        self.base_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SitePulse-Lighthouse/1.0 (https://sitepulse.com)'
        })
        
        # Alternative APIs as fallbacks
        self.fallback_apis = [
            "https://pagespeed.web.dev/api/v5/runPagespeed",
            "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
        ]
        
    def analyze_url(self, url, categories=None, strategy='desktop'):
        """
        Analyze URL using multiple strategies with fallbacks
        """
        if categories is None:
            categories = ['performance', 'accessibility', 'best-practices', 'seo']
        
        results = {
            "url": url,
            "strategy": strategy,
            "timestamp": datetime.now().isoformat(),
            "lighthouse_version": "",
            "categories": {},
            "audits": {},
            "core_web_vitals": {},
            "opportunities": [],
            "diagnostics": [],
            "error": None,
            "data_source": "unknown",
            "fallback_used": False
        }
        
        # Try primary Lighthouse API first
        lighthouse_result = self._try_lighthouse_api(url, categories, strategy)
        if lighthouse_result and not lighthouse_result.get("error"):
            results.update(lighthouse_result)
            results["data_source"] = "lighthouse_api"
            logger.info(f"Lighthouse API analysis successful for {url}")
            return results
        
        # Try fallback APIs
        for i, fallback_url in enumerate(self.fallback_apis):
            logger.info(f"Trying fallback API {i+1} for {url}")
            fallback_result = self._try_fallback_api(fallback_url, url, categories, strategy)
            if fallback_result and not fallback_result.get("error"):
                results.update(fallback_result)
                results["data_source"] = f"fallback_api_{i+1}"
                results["fallback_used"] = True
                logger.info(f"Fallback API {i+1} successful for {url}")
                return results
        
        # If all APIs fail, use local analysis
        logger.warning(f"All Lighthouse APIs failed for {url}, using local analysis")
        local_result = self._perform_local_analysis(url, strategy)
        results.update(local_result)
        results["data_source"] = "local_analysis"
        results["fallback_used"] = True
        
        return results
    
    def _try_lighthouse_api(self, url, categories, strategy):
        """Try the primary Lighthouse API"""
        try:
            params = {
                'url': url,
                'strategy': strategy,
                'category': categories,
                'locale': 'en',
                'utm_source': 'sitepulse'
            }
            
            if self.api_key:
                params['key'] = self.api_key
            
            logger.info(f"Attempting Lighthouse API analysis for {url}")
            response = self.session.get(self.base_url, params=params, timeout=30)
            
            if response.status_code == 200:
                return self._parse_lighthouse_response(response.json(), url)
            elif response.status_code == 429:
                logger.warning(f"Rate limit exceeded for {url}")
                return {"error": "Rate limit exceeded"}
            else:
                logger.error(f"Lighthouse API error for {url}: {response.status_code}")
                return {"error": f"API request failed: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Lighthouse API exception for {url}: {str(e)}")
            return {"error": f"API exception: {str(e)}"}
    
    def _try_fallback_api(self, api_url, url, categories, strategy):
        """Try a fallback API endpoint"""
        try:
            params = {
                'url': url,
                'strategy': strategy,
                'category': categories,
                'locale': 'en'
            }
            
            if self.api_key:
                params['key'] = self.api_key
            
            response = self.session.get(api_url, params=params, timeout=30)
            
            if response.status_code == 200:
                return self._parse_lighthouse_response(response.json(), url)
            else:
                logger.warning(f"Fallback API failed for {url}: {response.status_code}")
                return {"error": f"Fallback API failed: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Fallback API exception for {url}: {str(e)}")
            return {"error": f"Fallback API exception: {str(e)}"}
    
    def _parse_lighthouse_response(self, data, url):
        """Parse Lighthouse API response"""
        try:
            if 'lighthouseResult' not in data:
                return {"error": "No lighthouse result in API response"}
            
            lighthouse_result = data['lighthouseResult']
            parsed_result = {
                "lighthouse_version": lighthouse_result.get('lighthouseVersion', ''),
                "categories": {},
                "core_web_vitals": {},
                "opportunities": [],
                "diagnostics": [],
                "audits": {},
                "error": None
            }
            
            # Extract category scores
            categories_data = lighthouse_result.get('categories', {})
            for category, category_data in categories_data.items():
                parsed_result["categories"][category] = {
                    "score": round(category_data.get('score', 0) * 100),
                    "title": category_data.get('title', ''),
                    "description": category_data.get('description', '')
                }
            
            # Extract Core Web Vitals
            audits = lighthouse_result.get('audits', {})
            parsed_result["core_web_vitals"] = self._extract_core_web_vitals(audits)
            parsed_result["opportunities"] = self._extract_opportunities(audits)
            parsed_result["diagnostics"] = self._extract_diagnostics(audits)
            parsed_result["audits"] = self._extract_key_audits(audits)
            
            return parsed_result
            
        except Exception as e:
            logger.error(f"Error parsing Lighthouse response for {url}: {str(e)}")
            return {"error": f"Response parsing error: {str(e)}"}
    
    def _perform_local_analysis(self, url, strategy):
        """Perform local performance analysis when Lighthouse APIs fail"""
        logger.info(f"Performing local analysis for {url}")
        
        try:
            # Basic page load analysis
            start_time = time.time()
            response = self.session.get(url, timeout=30)
            load_time = (time.time() - start_time) * 1000
            
            # Analyze page content
            content_size = len(response.content)
            html_content = response.text
            
            # Extract basic metrics
            local_result = {
                "lighthouse_version": "local_analysis",
                "categories": {
                    "performance": {
                        "score": self._calculate_local_performance_score(load_time, content_size),
                        "title": "Performance (Local Analysis)",
                        "description": "Performance score calculated from local analysis"
                    }
                },
                "core_web_vitals": self._estimate_core_web_vitals_local(load_time, content_size, html_content),
                "opportunities": self._identify_local_opportunities(html_content, response.headers),
                "diagnostics": self._generate_local_diagnostics(load_time, content_size, response.headers),
                "audits": self._create_local_audits(load_time, content_size, html_content),
                "error": None
            }
            
            return local_result
            
        except Exception as e:
            logger.error(f"Local analysis failed for {url}: {str(e)}")
            return {
                "error": f"Local analysis failed: {str(e)}",
                "categories": {},
                "core_web_vitals": {},
                "opportunities": [],
                "diagnostics": [],
                "audits": {}
            }
    
    def _calculate_local_performance_score(self, load_time, content_size):
        """Calculate performance score based on local metrics"""
        score = 100
        
        # Load time scoring
        if load_time > 5000:
            score -= 40
        elif load_time > 3000:
            score -= 25
        elif load_time > 1000:
            score -= 15
        
        # Content size scoring
        if content_size > 5000000:  # 5MB
            score -= 30
        elif content_size > 2000000:  # 2MB
            score -= 20
        elif content_size > 1000000:  # 1MB
            score -= 10
        
        return max(0, min(100, score))
    
    def _estimate_core_web_vitals_local(self, load_time, content_size, html_content):
        """Estimate Core Web Vitals from local analysis"""
        vitals = {}
        
        # Estimate LCP (Largest Contentful Paint)
        estimated_lcp = load_time + (content_size / 100000) * 50
        vitals["lcp"] = {
            "value": round(estimated_lcp, 2),
            "displayValue": f"{round(estimated_lcp, 0)} ms (estimated)",
            "score": self._get_lcp_score(estimated_lcp),
            "rating": self._get_lcp_rating(estimated_lcp),
            "note": "Estimated from local analysis"
        }
        
        # Estimate FID (First Input Delay) - very rough
        estimated_fid = min(load_time * 0.1, 200)
        vitals["fid"] = {
            "value": round(estimated_fid, 2),
            "displayValue": f"{round(estimated_fid, 0)} ms (estimated)",
            "score": self._get_fid_score(estimated_fid),
            "rating": self._get_fid_rating(estimated_fid),
            "note": "Estimated from local analysis"
        }
        
        # Estimate CLS (Cumulative Layout Shift)
        estimated_cls = min(content_size / 10000000, 0.3)  # Rough estimation
        vitals["cls"] = {
            "value": round(estimated_cls, 3),
            "displayValue": f"{estimated_cls:.3f} (estimated)",
            "score": self._get_cls_score(estimated_cls),
            "rating": self._get_cls_rating(estimated_cls),
            "note": "Estimated from local analysis"
        }
        
        # Estimate FCP (First Contentful Paint)
        estimated_fcp = load_time * 0.7
        vitals["fcp"] = {
            "value": round(estimated_fcp, 2),
            "displayValue": f"{round(estimated_fcp, 0)} ms (estimated)",
            "score": self._get_fcp_score(estimated_fcp),
            "rating": self._get_fcp_rating(estimated_fcp),
            "note": "Estimated from local analysis"
        }
        
        return vitals
    
    def _identify_local_opportunities(self, html_content, headers):
        """Identify optimization opportunities from local analysis"""
        opportunities = []
        
        # Check for compression
        if 'content-encoding' not in headers:
            opportunities.append({
                "id": "enable-compression",
                "title": "Enable text compression",
                "description": "Enable gzip compression for text-based resources",
                "score": 0.5,
                "displayValue": "Potential savings: 20-30%",
                "details": {},
                "numericValue": 0
            })
        
        # Check for large HTML
        if len(html_content) > 100000:  # 100KB
            opportunities.append({
                "id": "reduce-html-size",
                "title": "Reduce HTML size",
                "description": "HTML document is larger than recommended",
                "score": 0.6,
                "displayValue": f"Current size: {len(html_content)} bytes",
                "details": {},
                "numericValue": len(html_content)
            })
        
        # Check for inline styles
        inline_style_count = html_content.count('<style>')
        if inline_style_count > 2:
            opportunities.append({
                "id": "consolidate-inline-styles",
                "title": "Consolidate inline styles",
                "description": "Multiple inline style tags detected",
                "score": 0.7,
                "displayValue": f"Found {inline_style_count} inline style tags",
                "details": {},
                "numericValue": inline_style_count
            })
        
        return opportunities
    
    def _generate_local_diagnostics(self, load_time, content_size, headers):
        """Generate diagnostic information from local analysis"""
        diagnostics = []
        
        # Server response time
        diagnostics.append({
            "id": "server-response-time",
            "title": "Server Response Time",
            "description": "Time taken for server to respond",
            "score": 1.0,
            "displayValue": f"{load_time:.0f} ms",
            "details": {},
            "numericValue": load_time
        })
        
        # Content size
        diagnostics.append({
            "id": "content-size",
            "title": "Content Size",
            "description": "Total size of the HTML document",
            "score": 1.0,
            "displayValue": f"{content_size / 1024:.1f} KB",
            "details": {},
            "numericValue": content_size
        })
        
        # Compression status
        compression_enabled = 'content-encoding' in headers
        diagnostics.append({
            "id": "compression-status",
            "title": "Compression Status",
            "description": "Whether text compression is enabled",
            "score": 1.0 if compression_enabled else 0.5,
            "displayValue": "Enabled" if compression_enabled else "Disabled",
            "details": {},
            "numericValue": 1 if compression_enabled else 0
        })
        
        return diagnostics
    
    def _create_local_audits(self, load_time, content_size, html_content):
        """Create audit results from local analysis"""
        audits = {}
        
        # First Contentful Paint (estimated)
        audits["first-contentful-paint"] = {
            "score": self._get_fcp_score(load_time * 0.7),
            "displayValue": f"{round(load_time * 0.7, 0)} ms (estimated)",
            "numericValue": load_time * 0.7
        }
        
        # Largest Contentful Paint (estimated)
        audits["largest-contentful-paint"] = {
            "score": self._get_lcp_score(load_time + (content_size / 100000) * 50),
            "displayValue": f"{round(load_time + (content_size / 100000) * 50, 0)} ms (estimated)",
            "numericValue": load_time + (content_size / 100000) * 50
        }
        
        # Cumulative Layout Shift (estimated)
        estimated_cls = min(content_size / 10000000, 0.3)
        audits["cumulative-layout-shift"] = {
            "score": self._get_cls_score(estimated_cls),
            "displayValue": f"{estimated_cls:.3f} (estimated)",
            "numericValue": estimated_cls
        }
        
        return audits
    
    def _extract_core_web_vitals(self, audits):
        """Extract Core Web Vitals from Lighthouse audits"""
        core_vitals = {}
        
        # Largest Contentful Paint (LCP)
        if 'largest-contentful-paint' in audits:
            lcp_audit = audits['largest-contentful-paint']
            core_vitals['lcp'] = {
                "value": lcp_audit.get('numericValue', 0),
                "displayValue": lcp_audit.get('displayValue', ''),
                "score": lcp_audit.get('score', 0),
                "rating": self._get_lcp_rating(lcp_audit.get('numericValue', 0))
            }
        
        # First Input Delay (FID) - Note: Lighthouse measures Total Blocking Time as proxy
        if 'total-blocking-time' in audits:
            tbt_audit = audits['total-blocking-time']
            tbt_value = tbt_audit.get('numericValue', 0)
            estimated_fid = min(tbt_value / 5, 300)
            core_vitals['fid'] = {
                "value": estimated_fid,
                "displayValue": f"{estimated_fid:.0f} ms (estimated from TBT)",
                "score": tbt_audit.get('score', 0),
                "rating": self._get_fid_rating(estimated_fid),
                "note": "Estimated from Total Blocking Time"
            }
        
        # Cumulative Layout Shift (CLS)
        if 'cumulative-layout-shift' in audits:
            cls_audit = audits['cumulative-layout-shift']
            core_vitals['cls'] = {
                "value": cls_audit.get('numericValue', 0),
                "displayValue": cls_audit.get('displayValue', ''),
                "score": cls_audit.get('score', 0),
                "rating": self._get_cls_rating(cls_audit.get('numericValue', 0))
            }
        
        # First Contentful Paint (FCP)
        if 'first-contentful-paint' in audits:
            fcp_audit = audits['first-contentful-paint']
            core_vitals['fcp'] = {
                "value": fcp_audit.get('numericValue', 0),
                "displayValue": fcp_audit.get('displayValue', ''),
                "score": fcp_audit.get('score', 0),
                "rating": self._get_fcp_rating(fcp_audit.get('numericValue', 0))
            }
        
        return core_vitals
    
    def _extract_opportunities(self, audits):
        """Extract performance improvement opportunities"""
        opportunities = []
        
        opportunity_audits = [
            'unused-css-rules', 'unused-javascript', 'modern-image-formats',
            'offscreen-images', 'render-blocking-resources', 'unminified-css',
            'unminified-javascript', 'efficient-animated-content',
            'duplicated-javascript', 'legacy-javascript'
        ]
        
        for audit_id in opportunity_audits:
            if audit_id in audits:
                audit = audits[audit_id]
                if audit.get('score', 1) < 1:
                    opportunities.append({
                        "id": audit_id,
                        "title": audit.get('title', ''),
                        "description": audit.get('description', ''),
                        "score": audit.get('score', 0),
                        "displayValue": audit.get('displayValue', ''),
                        "details": audit.get('details', {}),
                        "numericValue": audit.get('numericValue', 0)
                    })
        
        return opportunities
    
    def _extract_diagnostics(self, audits):
        """Extract diagnostic information"""
        diagnostics = []
        
        diagnostic_audits = [
            'server-response-time', 'dom-size', 'critical-request-chains',
            'user-timings', 'bootup-time', 'mainthread-work-breakdown',
            'third-party-summary'
        ]
        
        for audit_id in diagnostic_audits:
            if audit_id in audits:
                audit = audits[audit_id]
                diagnostics.append({
                    "id": audit_id,
                    "title": audit.get('title', ''),
                    "description": audit.get('description', ''),
                    "score": audit.get('score', 1),
                    "displayValue": audit.get('displayValue', ''),
                    "details": audit.get('details', {}),
                    "numericValue": audit.get('numericValue', 0)
                })
        
        return diagnostics
    
    def _extract_key_audits(self, audits):
        """Extract key audit results"""
        key_audits = {}
        
        important_audits = [
            'first-contentful-paint', 'largest-contentful-paint',
            'first-meaningful-paint', 'speed-index', 'total-blocking-time',
            'max-potential-fid', 'cumulative-layout-shift', 'server-response-time',
            'interactive', 'redirects', 'installable-manifest', 'apple-touch-icon',
            'splash-screen', 'themed-omnibox', 'content-width', 'viewport',
            'without-javascript', 'first-cpu-idle', 'consistently-interactive'
        ]
        
        for audit_id in important_audits:
            if audit_id in audits:
                audit = audits[audit_id]
                key_audits[audit_id] = {
                    "score": audit.get('score', 1),
                    "displayValue": audit.get('displayValue', ''),
                    "numericValue": audit.get('numericValue', 0)
                }
        
        return key_audits
    
    # Scoring methods for local analysis
    def _get_lcp_score(self, value_ms):
        if value_ms <= 2500:
            return 1.0
        elif value_ms <= 4000:
            return 0.5
        else:
            return 0.0
    
    def _get_fid_score(self, value_ms):
        if value_ms <= 100:
            return 1.0
        elif value_ms <= 300:
            return 0.5
        else:
            return 0.0
    
    def _get_cls_score(self, value):
        if value <= 0.1:
            return 1.0
        elif value <= 0.25:
            return 0.5
        else:
            return 0.0
    
    def _get_fcp_score(self, value_ms):
        if value_ms <= 1800:
            return 1.0
        elif value_ms <= 3000:
            return 0.5
        else:
            return 0.0
    
    # Rating methods
    def _get_lcp_rating(self, value_ms):
        if value_ms <= 2500:
            return "good"
        elif value_ms <= 4000:
            return "needs-improvement"
        else:
            return "poor"
    
    def _get_fid_rating(self, value_ms):
        if value_ms <= 100:
            return "good"
        elif value_ms <= 300:
            return "needs-improvement"
        else:
            return "poor"
    
    def _get_cls_rating(self, value):
        if value <= 0.1:
            return "good"
        elif value <= 0.25:
            return "needs-improvement"
        else:
            return "poor"
    
    def _get_fcp_rating(self, value_ms):
        if value_ms <= 1800:
            return "good"
        elif value_ms <= 3000:
            return "needs-improvement"
        else:
            return "poor"
