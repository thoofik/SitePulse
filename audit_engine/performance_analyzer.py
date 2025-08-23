import requests
import time
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import logging
from .lighthouse_api import LighthouseAPI

logger = logging.getLogger(__name__)

class PerformanceAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SitePulse-PerformanceAnalyzer/2.0'
        })
        self.lighthouse = LighthouseAPI()
    
    def analyze(self, url):
        """
        Comprehensive performance analysis with multiple data sources
        """
        results = {
            "score": 0,
            "issues": [],
            "warnings": [],
            "recommendations": [],
            "metrics": {
                "load_time": 0,
                "page_size": 0,
                "requests_count": 0
            },
            "details": {
                "page_load": {},
                "resource_analysis": {},
                "core_web_vitals": {},
                "lighthouse": {},
                "data_sources": []
            }
        }
        
        try:
            data_sources = []
            
            # Run Lighthouse Analysis
            logger.info("Running Lighthouse performance analysis...")
            lighthouse_results = self.lighthouse.analyze_url(url, categories=['performance'], strategy='desktop')
            results["details"]["lighthouse"] = lighthouse_results
            data_sources.append(f"lighthouse_{lighthouse_results.get('data_source', 'unknown')}")
            
            # Extract Lighthouse metrics
            if not lighthouse_results.get("error"):
                results["details"]["core_web_vitals"] = lighthouse_results.get("core_web_vitals", {})
                results["metrics"]["lighthouse_score"] = lighthouse_results.get("categories", {}).get("performance", {}).get("score", 0)
                logger.info(f"Lighthouse analysis successful for {url}")
            else:
                logger.warning(f"Lighthouse analysis failed for {url}: {lighthouse_results.get('error')}")
            
            # Run local analysis
            logger.info("Running local performance analysis...")
            
            # Page Load Analysis
            load_results = self._analyze_page_load(url)
            results["details"]["page_load"] = load_results
            results["metrics"]["load_time"] = load_results.get("total_time", 0)
            data_sources.append("local_page_load")
            
            # Resource Analysis
            resource_results = self._analyze_resources(url)
            results["details"]["resource_analysis"] = resource_results
            results["metrics"]["page_size"] = resource_results.get("total_size", 0)
            results["metrics"]["requests_count"] = resource_results.get("total_requests", 0)
            data_sources.append("local_resource_analysis")
            
            # Enhance Core Web Vitals if Lighthouse failed
            if lighthouse_results.get("error") or not lighthouse_results.get("core_web_vitals"):
                logger.info("Enhancing Core Web Vitals with local analysis data")
                enhanced_vitals = self._enhance_core_web_vitals_with_local_data(results["details"])
                results["details"]["core_web_vitals"] = enhanced_vitals
                data_sources.append("enhanced_core_web_vitals")
            
            # Calculate performance score
            results["score"] = self._calculate_performance_score(results["details"], results["metrics"], lighthouse_results)
            
            # Generate recommendations
            self._generate_recommendations(results, lighthouse_results)
            
            # Record data sources
            results["details"]["data_sources"] = data_sources
            
        except Exception as e:
            logger.error(f"Performance analysis error: {str(e)}")
            results["issues"].append({
                "type": "error",
                "severity": "high",
                "message": f"Performance analysis failed: {str(e)}",
                "recommendation": "Please check if the URL is accessible and try again."
            })
        
        return results
    
    def _analyze_page_load(self, url):
        """Analyze page load performance"""
        load_results = {
            "total_time": 0,
            "status_code": 0,
            "redirects": 0,
            "issues": [],
            "headers": {}
        }
        
        try:
            start_time = time.time()
            response = self.session.get(url, timeout=30, allow_redirects=True)
            end_time = time.time()
            
            load_results["total_time"] = round((end_time - start_time) * 1000, 2)
            load_results["status_code"] = response.status_code
            load_results["redirects"] = len(response.history)
            load_results["headers"] = dict(response.headers)
            
            # Check for issues
            if load_results["total_time"] > 3000:
                load_results["issues"].append({
                    "type": "slow_load",
                    "severity": "medium",
                    "message": f"Page load time exceeds 3 seconds: {load_results['total_time']}ms",
                    "recommendation": "Optimize server response time, enable compression, and use CDN"
                })
            
            if load_results["redirects"] > 2:
                load_results["issues"].append({
                    "type": "too_many_redirects",
                    "severity": "medium",
                    "message": f"Too many redirects: {load_results['redirects']}",
                    "recommendation": "Minimize redirects to improve performance"
                })
            
            if response.status_code != 200:
                load_results["issues"].append({
                    "type": "non_200_status",
                    "severity": "high",
                    "message": f"Non-200 status code: {response.status_code}",
                    "recommendation": "Check server configuration and fix HTTP errors"
                })
            
            if 'content-encoding' not in response.headers:
                load_results["issues"].append({
                    "type": "no_compression",
                    "severity": "medium",
                    "message": "Text compression not enabled",
                    "recommendation": "Enable gzip compression for text-based resources"
                })
            
        except Exception as e:
            load_results["issues"].append({
                "type": "analysis_error",
                "severity": "high",
                "message": f"Page load analysis failed: {str(e)}",
                "recommendation": "Check URL accessibility and network connectivity"
            })
        
        return load_results
    
    def _analyze_resources(self, url):
        """Analyze page resources"""
        resource_results = {
            "total_size": 0,
            "total_requests": 0,
            "resources": {
                "images": {"count": 0, "size": 0, "issues": []},
                "scripts": {"count": 0, "size": 0, "issues": []},
                "stylesheets": {"count": 0, "size": 0, "issues": []}
            }
        }
        
        try:
            response = self.session.get(url, timeout=15)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Main page
            resource_results["total_size"] += len(response.content)
            resource_results["total_requests"] += 1
            
            # Analyze images
            images = soup.find_all('img')
            for img in images:
                src = img.get('src')
                if src:
                    img_analysis = self._analyze_image_resource(url, src)
                    resource_results["resources"]["images"]["count"] += 1
                    resource_results["resources"]["images"]["size"] += img_analysis.get("size", 0)
                    resource_results["total_size"] += img_analysis.get("size", 0)
                    resource_results["total_requests"] += 1
                    
                    if img_analysis.get("issues"):
                        resource_results["resources"]["images"]["issues"].extend(img_analysis["issues"])
            
            # Analyze scripts
            scripts = soup.find_all('script')
            for script in scripts:
                src = script.get('src')
                if src:
                    script_analysis = self._analyze_script_resource(url, src)
                    resource_results["resources"]["scripts"]["count"] += 1
                    resource_results["resources"]["scripts"]["size"] += script_analysis.get("size", 0)
                    resource_results["total_size"] += script_analysis.get("size", 0)
                    resource_results["total_requests"] += 1
                    
                    if script_analysis.get("issues"):
                        resource_results["resources"]["scripts"]["issues"].extend(script_analysis["issues"])
            
            # Analyze stylesheets
            stylesheets = soup.find_all('link', rel='stylesheet')
            for stylesheet in stylesheets:
                href = stylesheet.get('href')
                if href:
                    css_analysis = self._analyze_css_resource(url, href)
                    resource_results["resources"]["stylesheets"]["count"] += 1
                    resource_results["resources"]["stylesheets"]["size"] += css_analysis.get("size", 0)
                    resource_results["total_size"] += css_analysis.get("size", 0)
                    resource_results["total_requests"] += 1
                    
                    if css_analysis.get("issues"):
                        resource_results["resources"]["stylesheets"]["issues"].extend(css_analysis["issues"])
            
        except Exception as e:
            logger.error(f"Resource analysis error: {str(e)}")
        
        return resource_results
    
    def _analyze_image_resource(self, base_url, src):
        """Analyze individual image resource"""
        analysis = {"size": 0, "issues": []}
        
        try:
            img_url = urljoin(base_url, src)
            response = self.session.head(img_url, timeout=10)
            
            if response.status_code == 200:
                size = response.headers.get('content-length')
                if size:
                    analysis["size"] = int(size)
                    
                    if analysis["size"] > 500000:  # 500KB
                        analysis["issues"].append({
                            "type": "large_image",
                            "severity": "medium",
                            "message": f"Large image file: {src} ({analysis['size']} bytes)",
                            "recommendation": "Compress image and consider using WebP format"
                        })
                
                content_type = response.headers.get('content-type', '')
                if 'image/jpeg' in content_type or 'image/png' in content_type:
                    analysis["issues"].append({
                        "type": "modern_format",
                        "severity": "low",
                        "message": f"Consider using WebP format for: {src}",
                        "recommendation": "Convert to WebP for better compression"
                    })
        
        except Exception as e:
            analysis["issues"].append({
                "type": "analysis_error",
                "severity": "low",
                "message": f"Failed to analyze image {src}: {str(e)}",
                "recommendation": "Check image accessibility and format"
            })
        
        return analysis
    
    def _analyze_script_resource(self, base_url, src):
        """Analyze individual script resource"""
        analysis = {"size": 0, "issues": []}
        
        try:
            script_url = urljoin(base_url, src)
            response = self.session.head(script_url, timeout=10)
            
            if response.status_code == 200:
                size = response.headers.get('content-length')
                if size:
                    analysis["size"] = int(size)
                    
                    if analysis["size"] > 100000:  # 100KB
                        analysis["issues"].append({
                            "type": "large_script",
                            "severity": "medium",
                            "message": f"Large script file: {src} ({analysis['size']} bytes)",
                            "recommendation": "Consider code splitting and lazy loading"
                        })
                
                if not any(indicator in src for indicator in ['.min.', '-min.', '.minified.']):
                    analysis["issues"].append({
                        "type": "minification",
                        "severity": "low",
                        "message": f"Script may not be minified: {src}",
                        "recommendation": "Minify JavaScript files for production"
                    })
        
        except Exception as e:
            analysis["issues"].append({
                "type": "analysis_error",
                "severity": "low",
                "message": f"Failed to analyze script {src}: {str(e)}",
                "recommendation": "Check script accessibility and loading"
            })
        
        return analysis
    
    def _analyze_css_resource(self, base_url, href):
        """Analyze individual CSS resource"""
        analysis = {"size": 0, "issues": []}
        
        try:
            css_url = urljoin(base_url, href)
            response = self.session.head(css_url, timeout=10)
            
            if response.status_code == 200:
                size = response.headers.get('content-length')
                if size:
                    analysis["size"] = int(size)
                    
                    if analysis["size"] > 50000:  # 50KB
                        analysis["issues"].append({
                            "type": "large_css",
                            "severity": "medium",
                            "message": f"Large CSS file: {href} ({analysis['size']} bytes)",
                            "recommendation": "Split CSS into critical and non-critical paths"
                        })
                
                if not any(indicator in href for indicator in ['.min.', '-min.', '.minified.']):
                    analysis["issues"].append({
                        "type": "minification",
                        "severity": "low",
                        "message": f"CSS may not be minified: {href}",
                        "recommendation": "Minify CSS files for production"
                    })
        
        except Exception as e:
            analysis["issues"].append({
                "type": "analysis_error",
                "severity": "low",
                "message": f"Failed to analyze CSS {href}: {str(e)}",
                "recommendation": "Check CSS accessibility and optimization"
            })
        
        return analysis
    
    def _enhance_core_web_vitals_with_local_data(self, details):
        """Enhance Core Web Vitals with local analysis data"""
        vitals = {
            "lcp": {"value": 0, "rating": "good", "note": "Enhanced with local data"},
            "fid": {"value": 0, "rating": "good", "note": "Enhanced with local data"},
            "cls": {"value": 0, "rating": "good", "note": "Enhanced with local data"},
            "fcp": {"value": 0, "rating": "good", "note": "Enhanced with local data"},
            "enhanced": True
        }
        
        try:
            load_time = details.get("page_load", {}).get("total_time", 0)
            total_size = details.get("resource_analysis", {}).get("total_size", 0)
            resource_count = details.get("resource_analysis", {}).get("total_requests", 0)
            
            # Enhanced LCP estimation
            estimated_lcp = load_time + (total_size / 100000) * 30 + (resource_count * 10)
            vitals["lcp"]["value"] = round(estimated_lcp, 2)
            vitals["lcp"]["rating"] = self._get_lcp_rating(estimated_lcp)
            
            # Enhanced FID estimation
            estimated_fid = min(load_time * 0.15 + (resource_count * 5), 250)
            vitals["fid"]["value"] = round(estimated_fid, 2)
            vitals["fid"]["rating"] = self._get_fid_rating(estimated_fid)
            
            # Enhanced CLS estimation
            estimated_cls = min((total_size / 10000000) + (resource_count * 0.001), 0.3)
            vitals["cls"]["value"] = round(estimated_cls, 3)
            vitals["cls"]["rating"] = self._get_cls_rating(estimated_cls)
            
            # Enhanced FCP estimation
            estimated_fcp = load_time * 0.6
            vitals["fcp"]["value"] = round(estimated_fcp, 2)
            vitals["fcp"]["rating"] = self._get_fcp_rating(estimated_fcp)
        
        except Exception as e:
            logger.error(f"Core Web Vitals enhancement error: {str(e)}")
        
        return vitals
    
    def _calculate_performance_score(self, details, metrics, lighthouse_results):
        """Calculate performance score using multiple data sources"""
        
        if not lighthouse_results.get("error") and lighthouse_results.get("categories", {}).get("performance"):
            lighthouse_score = lighthouse_results["categories"]["performance"]["score"]
            local_score = self._calculate_local_performance_score(details, metrics)
            final_score = (lighthouse_score * 0.7) + (local_score * 0.3)
            return round(final_score, 1)
        else:
            return self._calculate_local_performance_score(details, metrics)
    
    def _calculate_local_performance_score(self, details, metrics):
        """Calculate performance score based on local metrics"""
        score = 100
        
        # Load time scoring
        load_time = metrics.get("load_time", 0)
        if load_time > 5000:
            score -= 40
        elif load_time > 3000:
            score -= 25
        elif load_time > 1000:
            score -= 15
        
        # Page size scoring
        page_size = metrics.get("page_size", 0)
        if page_size > 5000000:  # 5MB
            score -= 30
        elif page_size > 2000000:  # 2MB
            score -= 20
        elif page_size > 1000000:  # 1MB
            score -= 10
        
        # Request count scoring
        requests = metrics.get("requests_count", 0)
        if requests > 100:
            score -= 20
        elif requests > 50:
            score -= 10
        
        # Core Web Vitals scoring
        vitals = details.get("core_web_vitals", {})
        if vitals.get("lcp", {}).get("rating") == "poor":
            score -= 15
        if vitals.get("fid", {}).get("rating") == "poor":
            score -= 15
        if vitals.get("cls", {}).get("rating") == "poor":
            score -= 10
        
        return max(0, min(100, score))
    
    def _generate_recommendations(self, results, lighthouse_results):
        """Generate performance recommendations"""
        
        # Add Lighthouse recommendations
        if not lighthouse_results.get("error"):
            self._add_lighthouse_recommendations(results, lighthouse_results)
        
        # Add local analysis recommendations
        self._generate_local_recommendations(results)
        
        # Add resource-specific recommendations
        self._generate_resource_recommendations(results)
    
    def _add_lighthouse_recommendations(self, results, lighthouse_results):
        """Add recommendations based on Lighthouse data"""
        
        opportunities = lighthouse_results.get("opportunities", [])
        for opportunity in opportunities:
            if opportunity.get("score", 1) < 0.9:
                results["recommendations"].append({
                    "type": "lighthouse-opportunity",
                    "category": "performance",
                    "title": opportunity.get("title", ""),
                    "message": opportunity.get("description", ""),
                    "recommendation": self._get_lighthouse_opportunity_fix(opportunity),
                    "potential_savings": opportunity.get("displayValue", ""),
                    "severity": "high" if opportunity.get("score", 1) < 0.5 else "medium"
                })
        
        # Core Web Vitals recommendations
        core_vitals = lighthouse_results.get("core_web_vitals", {})
        
        if core_vitals.get("lcp", {}).get("rating") in ["needs-improvement", "poor"]:
            lcp_value = core_vitals["lcp"].get("value", 0)
            results["warnings"].append({
                "type": "core-web-vitals",
                "severity": "high" if core_vitals["lcp"]["rating"] == "poor" else "medium",
                "message": f"Largest Contentful Paint is {core_vitals['lcp']['rating']}: {core_vitals['lcp'].get('displayValue', f'{lcp_value}ms')}",
                "recommendation": "Optimize server response times, preload key resources, and optimize images above the fold."
            })
        
        if core_vitals.get("cls", {}).get("rating") in ["needs-improvement", "poor"]:
            cls_value = core_vitals["cls"].get("value", 0)
            results["warnings"].append({
                "type": "core-web-vitals",
                "severity": "high" if core_vitals["cls"]["rating"] == "poor" else "medium",
                "message": f"Cumulative Layout Shift is {core_vitals['cls']['rating']}: {cls_value:.3f}",
                "recommendation": "Set explicit dimensions for images and videos, avoid inserting content above existing content."
            })
    
    def _generate_local_recommendations(self, results):
        """Generate recommendations based on local analysis"""
        details = results["details"]
        metrics = results["metrics"]
        
        # Load time recommendations
        load_time = metrics.get("load_time", 0)
        if load_time > 3000:
            results["issues"].append({
                "type": "performance",
                "severity": "high",
                "message": f"Slow page load time: {load_time}ms",
                "recommendation": "Optimize images, minify CSS/JS, enable compression, and consider using a CDN."
            })
        
        # Page size recommendations
        page_size = metrics.get("page_size", 0)
        if page_size > 2000000:  # 2MB
            results["warnings"].append({
                "type": "performance",
                "severity": "medium",
                "message": f"Large page size: {round(page_size/1024/1024, 2)}MB",
                "recommendation": "Compress images, minify resources, and remove unused code to reduce page size."
            })
    
    def _generate_resource_recommendations(self, results):
        """Generate resource-specific recommendations"""
        resource_analysis = results["details"].get("resource_analysis", {})
        
        # Image recommendations
        image_issues = resource_analysis.get("resources", {}).get("images", {}).get("issues", [])
        for issue in image_issues:
            results["recommendations"].append({
                "type": "optimization",
                "category": "images",
                "message": issue.get("message", ""),
                "recommendation": issue.get("recommendation", "Optimize images by compressing them and using modern formats like WebP.")
            })
        
        # Script recommendations
        script_issues = resource_analysis.get("resources", {}).get("scripts", {}).get("issues", [])
        for issue in script_issues:
            results["recommendations"].append({
                "type": "optimization",
                "category": "scripts",
                "message": issue.get("message", ""),
                "recommendation": issue.get("recommendation", "Minify JavaScript files and consider code splitting for better performance.")
            })
    
    def _get_lighthouse_opportunity_fix(self, opportunity):
        """Get specific fix recommendations for Lighthouse opportunities"""
        
        opportunity_id = opportunity.get("id", "")
        
        fixes = {
            "unused-css-rules": "Remove unused CSS rules to reduce bundle size. Use tools like PurgeCSS or analyze coverage in DevTools.",
            "unused-javascript": "Remove unused JavaScript code. Use tree-shaking with modern bundlers like Webpack or Rollup.",
            "modern-image-formats": "Serve images in modern formats like WebP or AVIF for better compression and quality.",
            "offscreen-images": "Implement lazy loading for images below the fold using loading='lazy' or Intersection Observer API.",
            "render-blocking-resources": "Eliminate render-blocking CSS and JavaScript. Inline critical CSS and defer non-critical resources.",
            "unminified-css": "Minify CSS files to reduce file size. Use build tools like cssnano or clean-css.",
            "unminified-javascript": "Minify JavaScript files using tools like Terser or UglifyJS.",
            "efficient-animated-content": "Use efficient formats for animated content like WebP instead of GIF.",
            "duplicated-javascript": "Remove duplicate JavaScript modules and consolidate similar functionality.",
            "legacy-javascript": "Avoid serving legacy JavaScript to modern browsers. Use differential serving."
        }
        
        return fixes.get(opportunity_id, f"Address the {opportunity.get('title', 'performance issue')} identified by Lighthouse.")
    
    # Rating methods for Core Web Vitals
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
