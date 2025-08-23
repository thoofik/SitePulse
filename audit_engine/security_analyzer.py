import requests
import ssl
import socket
import re
import urllib.parse
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import logging
from datetime import datetime, timedelta
import json

logger = logging.getLogger(__name__)

class SecurityAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SitePulse-SecurityAnalyzer/1.0'
        })
    
    def analyze(self, url):
        """
        Comprehensive security analysis of a website
        """
        results = {
            "score": 0,
            "issues": [],
            "warnings": [],
            "recommendations": [],
            "details": {
                "ssl_analysis": {},
                "headers_analysis": {},
                "vulnerability_scan": {},
                "content_security": {}
            }
        }
        
        try:
            # Parse URL
            parsed_url = urlparse(url)
            if not parsed_url.scheme:
                url = 'https://' + url
                parsed_url = urlparse(url)
            
            # SSL/TLS Analysis
            ssl_results = self._analyze_ssl(parsed_url.hostname, parsed_url.port or (443 if parsed_url.scheme == 'https' else 80))
            results["details"]["ssl_analysis"] = ssl_results
            
            # HTTP Headers Analysis
            headers_results = self._analyze_headers(url)
            results["details"]["headers_analysis"] = headers_results
            
            # Vulnerability Scanning
            vuln_results = self._scan_vulnerabilities(url)
            results["details"]["vulnerability_scan"] = vuln_results
            
            # Content Security Analysis
            content_results = self._analyze_content_security(url)
            results["details"]["content_security"] = content_results
            
            # Calculate overall security score
            results["score"] = self._calculate_security_score(results["details"])
            
            # Generate issues and recommendations
            self._generate_security_recommendations(results)
            
        except Exception as e:
            logger.error(f"Security analysis error: {str(e)}")
            results["issues"].append({
                "type": "error",
                "severity": "high",
                "message": f"Security analysis failed: {str(e)}",
                "recommendation": "Please check if the URL is accessible and try again."
            })
        
        return results
    
    def _analyze_ssl(self, hostname, port):
        """Analyze SSL/TLS configuration"""
        ssl_results = {
            "has_ssl": False,
            "certificate_valid": False,
            "certificate_expiry": None,
            "tls_version": None,
            "cipher_suite": None,
            "issues": []
        }
        
        try:
            # Create SSL context
            context = ssl.create_default_context()
            
            # Connect and get certificate info
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    ssl_results["has_ssl"] = True
                    ssl_results["tls_version"] = ssock.version()
                    ssl_results["cipher_suite"] = ssock.cipher()
                    
                    # Get certificate
                    cert = ssock.getpeercert()
                    if cert:
                        ssl_results["certificate_valid"] = True
                        
                        # Check expiry
                        expiry_date = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                        ssl_results["certificate_expiry"] = expiry_date.isoformat()
                        
                        # Check if certificate expires soon
                        if expiry_date < datetime.now() + timedelta(days=30):
                            ssl_results["issues"].append("Certificate expires within 30 days")
                    
        except ssl.SSLError as e:
            ssl_results["issues"].append(f"SSL Error: {str(e)}")
        except Exception as e:
            ssl_results["issues"].append(f"Connection Error: {str(e)}")
        
        return ssl_results
    
    def _analyze_headers(self, url):
        """Analyze HTTP security headers"""
        headers_results = {
            "security_headers": {},
            "missing_headers": [],
            "issues": []
        }
        
        try:
            response = self.session.get(url, timeout=10, allow_redirects=True)
            headers = response.headers
            
            # Check for important security headers
            security_headers = {
                'Strict-Transport-Security': 'HSTS not enabled',
                'Content-Security-Policy': 'CSP not implemented',
                'X-Frame-Options': 'Clickjacking protection missing',
                'X-Content-Type-Options': 'MIME type sniffing protection missing',
                'X-XSS-Protection': 'XSS protection header missing',
                'Referrer-Policy': 'Referrer policy not set'
            }
            
            for header, issue in security_headers.items():
                if header in headers:
                    headers_results["security_headers"][header] = headers[header]
                else:
                    headers_results["missing_headers"].append(header)
                    headers_results["issues"].append(issue)
            
            # Check for information disclosure
            info_headers = ['Server', 'X-Powered-By', 'X-AspNet-Version']
            for header in info_headers:
                if header in headers:
                    headers_results["issues"].append(f"Information disclosure: {header} header present")
            
        except Exception as e:
            headers_results["issues"].append(f"Headers analysis failed: {str(e)}")
        
        return headers_results
    
    def _scan_vulnerabilities(self, url):
        """Scan for common web vulnerabilities"""
        vuln_results = {
            "sql_injection": {"vulnerable": False, "tests": []},
            "xss": {"vulnerable": False, "tests": []},
            "directory_traversal": {"vulnerable": False, "tests": []},
            "open_redirects": {"vulnerable": False, "tests": []},
            "issues": []
        }
        
        try:
            # Get the page content for analysis
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Check for forms (potential injection points)
            forms = soup.find_all('form')
            
            if forms:
                # SQL Injection basic tests
                sql_payloads = ["'", "1' OR '1'='1", "'; DROP TABLE users; --"]
                for payload in sql_payloads:
                    test_result = self._test_sql_injection(url, forms[0], payload)
                    vuln_results["sql_injection"]["tests"].append(test_result)
                    if test_result.get("vulnerable"):
                        vuln_results["sql_injection"]["vulnerable"] = True
                
                # XSS basic tests
                xss_payloads = ["<script>alert('XSS')</script>", "javascript:alert('XSS')", "<img src=x onerror=alert('XSS')>"]
                for payload in xss_payloads:
                    test_result = self._test_xss(url, forms[0], payload)
                    vuln_results["xss"]["tests"].append(test_result)
                    if test_result.get("vulnerable"):
                        vuln_results["xss"]["vulnerable"] = True
            
            # Directory traversal tests
            traversal_paths = ["../../../etc/passwd", "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts"]
            for path in traversal_paths:
                test_result = self._test_directory_traversal(url, path)
                vuln_results["directory_traversal"]["tests"].append(test_result)
                if test_result.get("vulnerable"):
                    vuln_results["directory_traversal"]["vulnerable"] = True
            
        except Exception as e:
            vuln_results["issues"].append(f"Vulnerability scanning failed: {str(e)}")
        
        return vuln_results
    
    def _test_sql_injection(self, url, form, payload):
        """Test for SQL injection vulnerability"""
        try:
            # This is a basic test - in production, use more sophisticated methods
            inputs = form.find_all('input')
            if not inputs:
                return {"payload": payload, "vulnerable": False, "response": "No inputs found"}
            
            data = {}
            for inp in inputs:
                name = inp.get('name')
                if name:
                    data[name] = payload if inp.get('type') != 'hidden' else inp.get('value', '')
            
            action = form.get('action', '')
            form_url = urljoin(url, action)
            
            response = self.session.post(form_url, data=data, timeout=5)
            
            # Look for SQL error patterns
            sql_errors = [
                "SQL syntax", "mysql_fetch", "ORA-", "PostgreSQL", 
                "Warning: mysql", "valid MySQL result", "MySqlClient"
            ]
            
            for error in sql_errors:
                if error.lower() in response.text.lower():
                    return {"payload": payload, "vulnerable": True, "response": "SQL error detected"}
            
            return {"payload": payload, "vulnerable": False, "response": "No SQL errors detected"}
            
        except Exception as e:
            return {"payload": payload, "vulnerable": False, "response": f"Test failed: {str(e)}"}
    
    def _test_xss(self, url, form, payload):
        """Test for XSS vulnerability"""
        try:
            inputs = form.find_all('input')
            if not inputs:
                return {"payload": payload, "vulnerable": False, "response": "No inputs found"}
            
            data = {}
            for inp in inputs:
                name = inp.get('name')
                if name:
                    data[name] = payload if inp.get('type') != 'hidden' else inp.get('value', '')
            
            action = form.get('action', '')
            form_url = urljoin(url, action)
            
            response = self.session.post(form_url, data=data, timeout=5)
            
            # Check if payload is reflected in response
            if payload in response.text:
                return {"payload": payload, "vulnerable": True, "response": "Payload reflected in response"}
            
            return {"payload": payload, "vulnerable": False, "response": "Payload not reflected"}
            
        except Exception as e:
            return {"payload": payload, "vulnerable": False, "response": f"Test failed: {str(e)}"}
    
    def _test_directory_traversal(self, url, path):
        """Test for directory traversal vulnerability"""
        try:
            parsed_url = urlparse(url)
            test_url = f"{parsed_url.scheme}://{parsed_url.netloc}/{path}"
            
            response = self.session.get(test_url, timeout=5)
            
            # Look for system file contents
            if "root:" in response.text or "[drivers]" in response.text:
                return {"path": path, "vulnerable": True, "response": "System file contents detected"}
            
            return {"path": path, "vulnerable": False, "response": "No system files detected"}
            
        except Exception as e:
            return {"path": path, "vulnerable": False, "response": f"Test failed: {str(e)}"}
    
    def _analyze_content_security(self, url):
        """Analyze content security issues"""
        content_results = {
            "mixed_content": [],
            "insecure_links": [],
            "suspicious_scripts": [],
            "issues": []
        }
        
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Check for mixed content (HTTPS page loading HTTP resources)
            if url.startswith('https://'):
                # Check images
                for img in soup.find_all('img'):
                    src = img.get('src')
                    if src and src.startswith('http://'):
                        content_results["mixed_content"].append(f"Insecure image: {src}")
                
                # Check scripts
                for script in soup.find_all('script'):
                    src = script.get('src')
                    if src and src.startswith('http://'):
                        content_results["mixed_content"].append(f"Insecure script: {src}")
                
                # Check stylesheets
                for link in soup.find_all('link', rel='stylesheet'):
                    href = link.get('href')
                    if href and href.startswith('http://'):
                        content_results["mixed_content"].append(f"Insecure stylesheet: {href}")
            
            # Check for suspicious external scripts
            for script in soup.find_all('script'):
                src = script.get('src')
                if src and not any(domain in src for domain in [urlparse(url).netloc, 'cdn.', 'ajax.googleapis.com']):
                    content_results["suspicious_scripts"].append(src)
            
        except Exception as e:
            content_results["issues"].append(f"Content security analysis failed: {str(e)}")
        
        return content_results
    
    def _calculate_security_score(self, details):
        """Calculate overall security score (0-100)"""
        score = 100
        
        # SSL/TLS scoring
        ssl_analysis = details.get("ssl_analysis", {})
        if not ssl_analysis.get("has_ssl"):
            score -= 30
        elif ssl_analysis.get("issues"):
            score -= 10
        
        # Headers scoring
        headers_analysis = details.get("headers_analysis", {})
        missing_headers = len(headers_analysis.get("missing_headers", []))
        score -= missing_headers * 5
        
        # Vulnerability scoring
        vuln_analysis = details.get("vulnerability_scan", {})
        if vuln_analysis.get("sql_injection", {}).get("vulnerable"):
            score -= 25
        if vuln_analysis.get("xss", {}).get("vulnerable"):
            score -= 20
        if vuln_analysis.get("directory_traversal", {}).get("vulnerable"):
            score -= 15
        
        # Content security scoring
        content_analysis = details.get("content_security", {})
        mixed_content_count = len(content_analysis.get("mixed_content", []))
        score -= mixed_content_count * 5
        
        return max(0, min(100, score))
    
    def _generate_security_recommendations(self, results):
        """Generate security recommendations based on analysis"""
        details = results["details"]
        
        # SSL recommendations
        ssl_analysis = details.get("ssl_analysis", {})
        if not ssl_analysis.get("has_ssl"):
            results["issues"].append({
                "type": "ssl",
                "severity": "critical",
                "message": "Website does not use HTTPS",
                "recommendation": "Enable SSL/TLS encryption by obtaining and installing an SSL certificate. Use services like Let's Encrypt for free certificates."
            })
        
        # Headers recommendations
        headers_analysis = details.get("headers_analysis", {})
        for header in headers_analysis.get("missing_headers", []):
            severity = "high" if header in ["Strict-Transport-Security", "Content-Security-Policy"] else "medium"
            results["warnings"].append({
                "type": "headers",
                "severity": severity,
                "message": f"Missing security header: {header}",
                "recommendation": self._get_header_recommendation(header)
            })
        
        # Vulnerability recommendations
        vuln_analysis = details.get("vulnerability_scan", {})
        if vuln_analysis.get("sql_injection", {}).get("vulnerable"):
            results["issues"].append({
                "type": "vulnerability",
                "severity": "critical",
                "message": "Potential SQL injection vulnerability detected",
                "recommendation": "Use parameterized queries and input validation. Never trust user input directly in SQL statements."
            })
        
        if vuln_analysis.get("xss", {}).get("vulnerable"):
            results["issues"].append({
                "type": "vulnerability",
                "severity": "high",
                "message": "Potential XSS vulnerability detected",
                "recommendation": "Implement proper input sanitization and output encoding. Use Content Security Policy headers."
            })
        
        # Content security recommendations
        content_analysis = details.get("content_security", {})
        if content_analysis.get("mixed_content"):
            results["warnings"].append({
                "type": "content",
                "severity": "medium",
                "message": "Mixed content detected (HTTPS page loading HTTP resources)",
                "recommendation": "Update all resource URLs to use HTTPS to prevent mixed content warnings and security issues."
            })
    
    def _get_header_recommendation(self, header):
        """Get specific recommendations for missing headers"""
        recommendations = {
            "Strict-Transport-Security": "Add HSTS header: 'Strict-Transport-Security: max-age=31536000; includeSubDomains'",
            "Content-Security-Policy": "Implement CSP header to prevent XSS attacks: 'Content-Security-Policy: default-src 'self''",
            "X-Frame-Options": "Add X-Frame-Options header: 'X-Frame-Options: DENY' or 'SAMEORIGIN'",
            "X-Content-Type-Options": "Add X-Content-Type-Options header: 'X-Content-Type-Options: nosniff'",
            "X-XSS-Protection": "Add X-XSS-Protection header: 'X-XSS-Protection: 1; mode=block'",
            "Referrer-Policy": "Add Referrer-Policy header: 'Referrer-Policy: strict-origin-when-cross-origin'"
        }
        return recommendations.get(header, f"Implement {header} header for better security")
