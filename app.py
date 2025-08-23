from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import json
import logging
from datetime import datetime
import traceback
import os

# Import audit modules
from audit_engine.security_analyzer import SecurityAnalyzer
from audit_engine.performance_analyzer import PerformanceAnalyzer
from audit_engine.seo_analyzer import SEOAnalyzer
from audit_engine.accessibility_analyzer import AccessibilityAnalyzer
from audit_engine.report_generator import ReportGenerator
from audit_engine.screenshot_service import ScreenshotService
from audit_engine.config import config

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Configure logging with the new audit engine config
logging.basicConfig(
    level=getattr(logging, config.log_level),
    format=config.log_format
)
logger = logging.getLogger(__name__)

# Initialize screenshot service
screenshot_service = ScreenshotService()

# Log audit engine configuration
logger.info("SitePulse Audit Engine v2.0 initialized")
logger.info(f"Lighthouse API: {config.lighthouse_base_url}")
logger.info(f"Performance thresholds: {config.get_performance_thresholds()}")
logger.info(f"Core Web Vitals thresholds: {config.get_core_web_vitals_thresholds()}")
logger.info("Screenshot service initialized")

# WebSocket event handlers
@socketio.on('connect')
def handle_connect():
    logger.info("WebSocket client connected")
    emit('connected', {'status': 'connected', 'message': 'Connected to SitePulse Audit Engine'})

@socketio.on('disconnect')
def handle_disconnect():
    logger.info("WebSocket client disconnected")

@socketio.on('audit_progress')
def handle_audit_progress(data):
    """Handle audit progress updates"""
    logger.info(f"Audit progress update: {data}")
    emit('audit_progress_update', data)

@socketio.on('request_audit_status')
def handle_audit_status_request(data):
    """Handle requests for current audit status"""
    logger.info(f"Audit status request: {data}")
    emit('audit_status_response', {
        'status': 'ready',
        'message': 'Audit engine ready for new requests',
        'timestamp': datetime.now().isoformat()
    })

@socketio.on('subscribe_to_audit')
def handle_audit_subscription(data):
    """Handle subscription to audit updates"""
    logger.info(f"Audit subscription request: {data}")
    emit('audit_subscription_confirmed', {
        'status': 'subscribed',
        'message': 'Subscribed to audit updates',
        'subscription_id': f"audit_{datetime.now().timestamp()}",
        'timestamp': datetime.now().isoformat()
    })

@socketio.on('request_audit_data')
def handle_audit_data_request(data):
    """Handle requests for specific audit data"""
    try:
        audit_type = data.get('audit_type')
        url = data.get('url')
        
        if not audit_type or not url:
            emit('audit_data_response', {
                'error': 'Missing audit_type or url',
                'status': 'error'
            })
            return
        
        logger.info(f"Audit data request: {audit_type} for {url}")
        
        # Run the specific audit type
        if audit_type == 'performance':
            try:
                performance_analyzer = PerformanceAnalyzer()
                results = performance_analyzer.analyze(url)
                emit('audit_data_response', {
                    'audit_type': audit_type,
                    'url': url,
                    'results': results,
                    'status': 'success',
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                emit('audit_data_response', {
                    'audit_type': audit_type,
                    'url': url,
                    'error': str(e),
                    'status': 'error',
                    'timestamp': datetime.now().isoformat()
                })
        
        elif audit_type == 'security':
            try:
                security_analyzer = SecurityAnalyzer()
                results = security_analyzer.analyze(url)
                emit('audit_data_response', {
                    'audit_type': audit_type,
                    'url': url,
                    'results': results,
                    'status': 'success',
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                emit('audit_data_response', {
                    'audit_type': audit_type,
                    'url': url,
                    'error': str(e),
                    'status': 'error',
                    'timestamp': datetime.now().isoformat()
                })
        
        elif audit_type == 'seo':
            try:
                seo_analyzer = SEOAnalyzer()
                results = seo_analyzer.analyze(url)
                emit('audit_data_response', {
                    'audit_type': audit_type,
                    'url': url,
                    'results': results,
                    'status': 'success',
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                emit('audit_data_response', {
                    'audit_type': audit_type,
                    'url': url,
                    'error': str(e),
                    'status': 'error',
                    'timestamp': datetime.now().isoformat()
                })
        
        elif audit_type == 'accessibility':
            try:
                accessibility_analyzer = AccessibilityAnalyzer()
                results = accessibility_analyzer.analyze(url)
                emit('audit_data_response', {
                    'audit_type': audit_type,
                    'url': url,
                    'results': results,
                    'status': 'success',
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                emit('audit_data_response', {
                    'audit_type': audit_type,
                    'url': url,
                    'error': str(e),
                    'status': 'error',
                    'timestamp': datetime.now().isoformat()
                })
        
        else:
            emit('audit_data_response', {
                'error': f'Unknown audit type: {audit_type}',
                'status': 'error'
            })
            
    except Exception as e:
        logger.error(f"Error handling audit data request: {str(e)}")
        emit('audit_data_response', {
            'error': f'Request processing error: {str(e)}',
            'status': 'error'
        })

def transform_audit_data_for_frontend(audit_results):
    """
    Transform the audit data to match frontend expectations while preserving real data
    """
    try:
        # Extract real scores from each audit type
        category_scores = {}
        total_score = 0
        score_count = 0
        
        for audit_type, results in audit_results.get("results", {}).items():
            if isinstance(results, dict) and not results.get("error"):
                score = results.get("score", 0)
                if score > 0:
                    category_scores[audit_type] = {
                        "score": score,
                        "grade": get_grade_from_score(score)
                    }
                    total_score += score
                    score_count += 1
        
        # Calculate overall score
        overall_score = round(total_score / score_count) if score_count > 0 else 0
        
        # Return real data with minimal transformation
        transformed_data = {
            "metadata": {
                "url": audit_results.get("url", "Unknown"),
                "timestamp": audit_results.get("timestamp", datetime.now().isoformat()),
                "audit_engine_version": audit_results.get("audit_engine_version", "2.0.0")
            },
            "executive_summary": {
                "overall_score": overall_score,
                "grade": get_grade_from_score(overall_score),
                "key_findings": generate_key_findings(audit_results),
                "timeline": "Immediate action recommended for critical issues, with performance and SEO improvements planned within 2-4 weeks."
            },
            "overall_metrics": {
                "overall_score": overall_score,
                "grade": get_grade_from_score(overall_score),
                "category_scores": category_scores,
                "critical_issues": audit_results.get("summary", {}).get("critical_issues", 0),
                "high_issues": audit_results.get("summary", {}).get("total_issues", 0) - audit_results.get("summary", {}).get("critical_issues", 0),
                "medium_issues": audit_results.get("summary", {}).get("warnings", 0),
                "total_recommendations": audit_results.get("summary", {}).get("recommendations", 0)
            },
            "prioritized_issues": transform_issues_for_frontend(audit_results),
            "detailed_results": audit_results.get("results", {}),  # Keep all real audit data
            "recommendations": audit_results.get("recommendations", []),
            # Add raw audit results for complete transparency
            "raw_audit_results": audit_results,
            "performance_metrics": audit_results.get("performance_metrics", {}),
            "summary": audit_results.get("summary", {}),
            "data_sources": audit_results.get("summary", {}).get("data_sources_used", [])
        }
        
        return transformed_data
        
    except Exception as e:
        logger.error(f"Error transforming audit data: {str(e)}")
        logger.error(f"Audit results structure: {type(audit_results)}")
        if isinstance(audit_results, dict):
            logger.error(f"Audit results keys: {list(audit_results.keys())}")
        
        # Return the raw audit results if transformation fails
        return {
            "error": "Data transformation failed, returning raw results",
            "raw_audit_results": audit_results,
            "metadata": {
                "url": audit_results.get("url", "Unknown") if isinstance(audit_results, dict) else "Unknown",
                "timestamp": audit_results.get("timestamp", datetime.now().isoformat()) if isinstance(audit_results, dict) else datetime.now().isoformat(),
                "audit_engine_version": "2.0.0"
            }
        }

def get_grade_from_score(score):
    """Convert numeric score to letter grade"""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"

def generate_key_findings(audit_results):
    """Generate key findings from audit results"""
    findings = []
    
    try:
        # Performance findings
        if "performance" in audit_results.get("results", {}):
            perf_results = audit_results["results"]["performance"]
            if perf_results.get("score", 0) < 70:
                findings.append("Performance score needs improvement - consider optimizing images and scripts")
            if perf_results.get("details", {}).get("core_web_vitals"):
                findings.append("Core Web Vitals analysis completed with enhanced local data")
        
        # Security findings
        if "security" in audit_results.get("results", {}):
            sec_results = audit_results["results"]["security"]
            if sec_results.get("score", 0) < 80:
                findings.append("Security vulnerabilities detected - immediate attention required")
        
        # SEO findings
        if "seo" in audit_results.get("results", {}):
            seo_results = audit_results["results"]["seo"]
            if seo_results.get("score", 0) < 70:
                findings.append("SEO optimization opportunities identified")
        
        # Accessibility findings
        if "accessibility" in audit_results.get("results", {}):
            acc_results = audit_results["results"]["accessibility"]
            if acc_results.get("score", 0) < 80:
                findings.append("Accessibility improvements needed for better user experience")
        
        # Add data source information
        if audit_results.get("summary", {}).get("data_sources_used"):
            sources = audit_results["summary"]["data_sources_used"]
            if "enhanced_core_web_vitals" in sources:
                findings.append("Core Web Vitals enhanced with local analysis data")
        
        # Add fallback findings if none were generated
        if not findings:
            findings.append("Comprehensive audit completed successfully")
            
    except Exception as e:
        logger.error(f"Error generating key findings: {str(e)}")
        findings = ["Audit completed with some analysis results"]
    
    return findings

def transform_issues_for_frontend(audit_results):
    """Transform issues to frontend format"""
    issues = []
    
    try:
        for audit_type, results in audit_results.get("results", {}).items():
            if isinstance(results, dict) and not results.get("error"):
                # Add issues
                if "issues" in results:
                    for issue in results["issues"]:
                        issues.append({
                            "category": audit_type,
                            "severity": issue.get("severity", "medium"),
                            "title": issue.get("type", "Issue"),
                            "description": issue.get("message", ""),
                            "recommendation": issue.get("recommendation", ""),
                            "priority": get_priority_from_severity(issue.get("severity", "medium"))
                        })
                
                # Add warnings
                if "warnings" in results:
                    for warning in results["warnings"]:
                        issues.append({
                            "category": audit_type,
                            "severity": "medium",
                            "title": warning.get("type", "Warning"),
                            "description": warning.get("message", ""),
                            "recommendation": warning.get("recommendation", ""),
                            "priority": "medium"
                        })
        
        # Sort by priority
        priority_order = {"high": 3, "medium": 2, "low": 1}
        issues.sort(key=lambda x: priority_order.get(x["priority"], 0), reverse=True)
        
    except Exception as e:
        logger.error(f"Error transforming issues for frontend: {str(e)}")
        issues = []
    
    return issues

def get_priority_from_severity(severity):
    """Convert severity to priority"""
    severity_mapping = {
        "high": "high",
        "critical": "high",
        "medium": "medium",
        "low": "low"
    }
    return severity_mapping.get(severity, "medium")

@app.route('/')
def index():
    return jsonify({
        "message": "SitePulse - Website Audit Tool API",
        "version": "2.0.0",
        "audit_engine": "v2.0 - Enhanced with Lighthouse API + Local Analysis",
        "endpoints": {
            "audit": "/api/audit",
            "audit_raw": "/api/audit/raw",
            "health": "/api/health",
            "config": "/api/config"
        },
        "websocket_events": {
            "connect": "Emitted when client connects",
            "audit_progress_update": "Real-time audit progress updates",
            "audit_results_update": "Real-time audit results as they complete",
            "audit_summary_update": "Final summary and metrics",
            "audit_completed": "Complete audit results",
            "audit_error": "Error notifications",
            "audit_data_response": "Response to specific audit data requests"
        },
        "real_time_features": [
            "Live audit progress updates",
            "Real-time audit results streaming",
            "Immediate error notifications",
            "On-demand audit data requests",
            "WebSocket-based communication"
        ],
        "note": "Use WebSocket for real-time data, /api/audit/raw for raw results without transformation"
    })

@app.route('/api/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "audit_engine": "v2.0",
        "features": [
            "Multi-source performance analysis",
            "Lighthouse API with fallback strategies",
            "Local performance analysis",
            "Enhanced Core Web Vitals",
            "Comprehensive resource optimization"
        ]
    })

@app.route('/api/config')
def get_config():
    """Get current audit engine configuration"""
    return jsonify({
        "audit_engine_version": "2.0.0",
        "configuration": config.to_dict(),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/screenshot', methods=['POST'])
def capture_screenshot():
    """Capture a screenshot of the given URL"""
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({
                "error": "URL is required",
                "code": "MISSING_URL"
            }), 400
        
        url = data['url']
        width = data.get('width', 1920)
        height = data.get('height', 1080)
        timeout = data.get('timeout', 30)
        
        logger.info(f"Capturing screenshot for URL: {url}")
        
        # Capture screenshot
        screenshot_info = screenshot_service.capture_screenshot(url, width, height, timeout)
        
        if screenshot_info.get('success'):
            return jsonify({
                "success": True,
                "screenshot": screenshot_info,
                "message": "Screenshot captured successfully"
            })
        else:
            return jsonify({
                "success": False,
                "error": screenshot_info.get('error', 'Failed to capture screenshot'),
                "code": "SCREENSHOT_FAILED"
            }), 500
            
    except Exception as e:
        logger.error(f"Error capturing screenshot: {str(e)}")
        return jsonify({
            "error": "Internal server error during screenshot capture",
            "code": "SCREENSHOT_ERROR",
            "details": str(e)
        }), 500

@app.route('/api/screenshot/<filename>')
def get_screenshot(filename):
    """Serve a screenshot file"""
    try:
        from flask import send_file
        screenshot_path = os.path.join(screenshot_service.screenshot_dir, filename)
        
        if not os.path.exists(screenshot_path):
            return jsonify({
                "error": "Screenshot not found",
                "code": "NOT_FOUND"
            }), 404
        
        return send_file(screenshot_path, mimetype='image/png')
        
    except Exception as e:
        logger.error(f"Error serving screenshot: {str(e)}")
        return jsonify({
            "error": "Internal server error serving screenshot",
            "code": "SERVE_ERROR"
        }), 500

@app.route('/api/screenshots')
def list_screenshots():
    """List all available screenshots"""
    try:
        screenshots = screenshot_service.list_screenshots()
        return jsonify({
            "success": True,
            "screenshots": screenshots,
            "count": len(screenshots)
        })
        
    except Exception as e:
        logger.error(f"Error listing screenshots: {str(e)}")
        return jsonify({
            "error": "Internal server error listing screenshots",
            "code": "LIST_ERROR"
        }), 500

@app.route('/api/audit', methods=['POST'])
def audit_website():
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({
                "error": "URL is required",
                "code": "MISSING_URL"
            }), 400
        
        url = data['url']
        audit_types = data.get('audit_types', ['security', 'performance', 'seo', 'accessibility'])
        
        logger.info(f"Starting comprehensive audit for URL: {url}")
        logger.info(f"Audit types requested: {audit_types}")
        
        # Emit WebSocket progress update
        socketio.emit('audit_progress_update', {
            'status': 'started',
            'message': f'Starting audit for {url}',
            'progress': 0,
            'url': url,
            'audit_types': audit_types
        })
        
        # Capture screenshot first
        logger.info("Capturing webpage screenshot...")
        socketio.emit('audit_progress_update', {
            'status': 'running',
            'message': 'Capturing webpage screenshot...',
            'progress': 5,
            'current_audit': 'screenshot'
        })
        
        screenshot_info = screenshot_service.capture_screenshot(url)
        
        # Initialize audit results with enhanced structure
        audit_results = {
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "audit_engine_version": "2.0.0",
            "screenshot": screenshot_info,
            "results": {},
            "summary": {
                "total_issues": 0,
                "critical_issues": 0,
                "warnings": 0,
                "recommendations": 0,
                "data_sources_used": []
            },
            "performance_metrics": {
                "overall_score": 0,
                "lighthouse_score": 0,
                "local_score": 0
            }
        }
        
        # Run security analysis
        if 'security' in audit_types:
            logger.info("Running security analysis...")
            socketio.emit('audit_progress_update', {
                'status': 'running',
                'message': 'Running security analysis...',
                'progress': 25,
                'current_audit': 'security'
            })
            try:
                security_analyzer = SecurityAnalyzer()
                security_results = security_analyzer.analyze(url)
                audit_results["results"]["security"] = security_results
                
                # Emit real security results in real-time
                socketio.emit('audit_results_update', {
                    'audit_type': 'security',
                    'results': security_results,
                    'progress': 25,
                    'url': url
                })
                
                logger.info("Security analysis completed successfully")
            except Exception as e:
                logger.error(f"Security analysis failed: {str(e)}")
                error_result = {
                    "error": f"Security analysis failed: {str(e)}",
                    "status": "failed"
                }
                audit_results["results"]["security"] = error_result
                
                # Emit error results in real-time
                socketio.emit('audit_results_update', {
                    'audit_type': 'security',
                    'results': error_result,
                    'progress': 25,
                    'url': url,
                    'error': True
                })
        
        # Run performance analysis (Enhanced v2.0)
        if 'performance' in audit_types:
            logger.info("Running enhanced performance analysis (v2.0)...")
            socketio.emit('audit_progress_update', {
                'status': 'running',
                'message': 'Running enhanced performance analysis...',
                'progress': 50,
                'current_audit': 'performance'
            })
            try:
                performance_analyzer = PerformanceAnalyzer()
                performance_results = performance_analyzer.analyze(url)
                audit_results["results"]["performance"] = performance_results
                
                # Extract performance metrics for summary
                if performance_results.get("score"):
                    audit_results["performance_metrics"]["overall_score"] = performance_results["score"]
                
                # Track data sources used
                if performance_results.get("details", {}).get("data_sources"):
                    audit_results["summary"]["data_sources_used"].extend(
                        performance_results["details"]["data_sources"]
                    )
                
                # Emit real performance results in real-time
                socketio.emit('audit_results_update', {
                    'audit_type': 'performance',
                    'results': performance_results,
                    'progress': 50,
                    'url': url,
                    'score': performance_results.get('score', 0),
                    'data_sources': performance_results.get('details', {}).get('data_sources', [])
                })
                
                logger.info(f"Performance analysis completed. Score: {performance_results.get('score', 'N/A')}")
                logger.info(f"Data sources: {performance_results.get('details', {}).get('data_sources', [])}")
                
            except Exception as e:
                logger.error(f"Performance analysis failed: {str(e)}")
                error_result = {
                    "error": f"Performance analysis failed: {str(e)}",
                    "status": "failed"
                }
                audit_results["results"]["performance"] = error_result
                
                # Emit error results in real-time
                socketio.emit('audit_results_update', {
                    'audit_type': 'performance',
                    'results': error_result,
                    'progress': 50,
                    'url': url,
                    'error': True
                })
        
        # Run SEO analysis
        if 'seo' in audit_types:
            logger.info("Running SEO analysis...")
            socketio.emit('audit_progress_update', {
                'status': 'running',
                'message': 'Running SEO analysis...',
                'progress': 75,
                'current_audit': 'seo'
            })
            try:
                seo_analyzer = SEOAnalyzer()
                seo_results = seo_analyzer.analyze(url)
                audit_results["results"]["seo"] = seo_results
                
                # Emit real SEO results in real-time
                socketio.emit('audit_results_update', {
                    'audit_type': 'seo',
                    'results': seo_results,
                    'progress': 75,
                    'url': url,
                    'score': seo_results.get('score', 0)
                })
                
                logger.info("SEO analysis completed successfully")
            except Exception as e:
                logger.error(f"SEO analysis failed: {str(e)}")
                error_result = {
                    "error": f"SEO analysis failed: {str(e)}",
                    "status": "failed"
                }
                audit_results["results"]["seo"] = error_result
                
                # Emit error results in real-time
                socketio.emit('audit_results_update', {
                    'audit_type': 'seo',
                    'results': error_result,
                    'progress': 75,
                    'url': url,
                    'error': True
                })
        
        # Run accessibility analysis
        if 'accessibility' in audit_types:
            logger.info("Running accessibility analysis...")
            socketio.emit('audit_progress_update', {
                'status': 'running',
                'message': 'Running accessibility analysis...',
                'progress': 90,
                'current_audit': 'accessibility'
            })
            try:
                accessibility_analyzer = AccessibilityAnalyzer()
                accessibility_results = accessibility_analyzer.analyze(url)
                audit_results["results"]["accessibility"] = accessibility_results
                
                # Emit real accessibility results in real-time
                socketio.emit('audit_results_update', {
                    'audit_type': 'accessibility',
                    'results': accessibility_results,
                    'progress': 90,
                    'url': url,
                    'score': accessibility_results.get('score', 0)
                })
                
                logger.info("Accessibility analysis completed successfully")
            except Exception as e:
                logger.error(f"Accessibility analysis failed: {str(e)}")
                error_result = {
                    "error": f"Accessibility analysis failed: {str(e)}",
                    "status": "failed"
                }
                audit_results["results"]["accessibility"] = error_result
                
                # Emit error results in real-time
                socketio.emit('audit_results_update', {
                    'audit_type': 'accessibility',
                    'results': error_result,
                    'progress': 90,
                    'url': url,
                    'error': True
                })
        
        # Calculate summary statistics
        try:
            for audit_type, results in audit_results["results"].items():
                if isinstance(results, dict) and not results.get("error"):
                    # Count issues
                    if "issues" in results:
                        audit_results["summary"]["total_issues"] += len(results["issues"])
                        audit_results["summary"]["critical_issues"] += len([
                            issue for issue in results["issues"] 
                            if issue.get("severity") == "high"
                        ])
                    
                    # Count warnings
                    if "warnings" in results:
                        audit_results["summary"]["warnings"] += len(results["warnings"])
                    
                    # Count recommendations
                    if "recommendations" in results:
                        audit_results["summary"]["recommendations"] += len(results["recommendations"])
        except Exception as e:
            logger.error(f"Error calculating summary statistics: {str(e)}")
            # Set safe defaults
            audit_results["summary"]["total_issues"] = 0
            audit_results["summary"]["critical_issues"] = 0
            audit_results["summary"]["warnings"] = 0
            audit_results["summary"]["recommendations"] = 0
        
        # Emit final summary in real-time
        socketio.emit('audit_summary_update', {
            'summary': audit_results["summary"],
            'performance_metrics': audit_results["performance_metrics"],
            'progress': 95,
            'url': url
        })
        
        # Emit completion WebSocket update with raw results
        socketio.emit('audit_completed', {
            'status': 'completed',
            'message': 'Audit completed successfully!',
            'progress': 100,
            'url': url,
            'raw_audit_results': audit_results,
            'summary': audit_results["summary"]
        })
        
        logger.info(f"Comprehensive audit completed for URL: {url}")
        logger.info(f"Summary: {audit_results['summary']['total_issues']} issues, "
                   f"{audit_results['summary']['warnings']} warnings, "
                   f"{audit_results['summary']['recommendations']} recommendations")
        
        # Return the raw audit results directly for maximum transparency
        return jsonify({
            "success": True,
            "message": "Audit completed successfully - check WebSocket for real-time results",
            "raw_audit_results": audit_results,
            "audit_engine_version": "2.0.0",
            "timestamp": datetime.now().isoformat(),
            "note": "Real-time results were sent via WebSocket during the audit process"
        })
    
    except Exception as e:
        logger.error(f"Critical error during audit: {str(e)}")
        logger.error(traceback.format_exc())
        
        # Emit error WebSocket update
        socketio.emit('audit_error', {
            'status': 'error',
            'message': f'Audit failed: {str(e)}',
            'progress': 0,
            'error_details': str(e)
        })
        
        return jsonify({
            "error": "Internal server error during audit",
            "code": "AUDIT_ERROR",
            "details": str(e),
            "audit_engine_version": "2.0.0",
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/audit/raw', methods=['POST'])
def audit_website_raw():
    """Get raw audit results without transformation"""
    try:
        data = request.get_json()
        
        if not data or 'url' not in data:
            return jsonify({
                "error": "URL is required",
                "code": "MISSING_URL"
            }), 400
        
        url = data['url']
        audit_types = data.get('audit_types', ['security', 'performance', 'seo', 'accessibility'])
        
        logger.info(f"Starting raw audit for URL: {url}")
        logger.info(f"Audit types requested: {audit_types}")
        
        # Capture screenshot first
        logger.info("Capturing webpage screenshot...")
        screenshot_info = screenshot_service.capture_screenshot(url)
        
        # Initialize audit results with enhanced structure
        audit_results = {
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "audit_engine_version": "2.0.0",
            "screenshot": screenshot_info,
            "results": {},
            "summary": {
                "total_issues": 0,
                "critical_issues": 0,
                "warnings": 0,
                "recommendations": 0,
                "data_sources_used": []
            },
            "performance_metrics": {
                "overall_score": 0,
                "lighthouse_score": 0,
                "local_score": 0
            }
        }
        
        # Run security analysis
        if 'security' in audit_types:
            logger.info("Running security analysis...")
            try:
                security_analyzer = SecurityAnalyzer()
                security_results = security_analyzer.analyze(url)
                audit_results["results"]["security"] = security_results
                logger.info("Security analysis completed successfully")
            except Exception as e:
                logger.error(f"Security analysis failed: {str(e)}")
                audit_results["results"]["security"] = {
                    "error": f"Security analysis failed: {str(e)}",
                    "status": "failed"
                }
        
        # Run performance analysis (Enhanced v2.0)
        if 'performance' in audit_types:
            logger.info("Running enhanced performance analysis (v2.0)...")
            try:
                performance_analyzer = PerformanceAnalyzer()
                performance_results = performance_analyzer.analyze(url)
                audit_results["results"]["performance"] = performance_results
                
                # Extract performance metrics for summary
                if performance_results.get("score"):
                    audit_results["performance_metrics"]["overall_score"] = performance_results["score"]
                
                # Track data sources used
                if performance_results.get("details", {}).get("data_sources"):
                    audit_results["summary"]["data_sources_used"].extend(
                        performance_results["details"]["data_sources"]
                    )
                
                logger.info(f"Performance analysis completed. Score: {performance_results.get('score', 'N/A')}")
                logger.info(f"Data sources: {performance_results.get('details', {}).get('data_sources', [])}")
                
            except Exception as e:
                logger.error(f"Performance analysis failed: {str(e)}")
                audit_results["results"]["performance"] = {
                    "error": f"Performance analysis failed: {str(e)}",
                    "status": "failed"
                }
        
        # Run SEO analysis
        if 'seo' in audit_types:
            logger.info("Running SEO analysis...")
            try:
                seo_analyzer = SEOAnalyzer()
                seo_results = seo_analyzer.analyze(url)
                audit_results["results"]["seo"] = seo_results
                logger.info("SEO analysis completed successfully")
            except Exception as e:
                logger.error(f"SEO analysis failed: {str(e)}")
                audit_results["results"]["seo"] = {
                    "error": f"SEO analysis failed: {str(e)}",
                    "status": "failed"
                }
        
        # Run accessibility analysis
        if 'accessibility' in audit_types:
            logger.info("Running accessibility analysis...")
            try:
                accessibility_analyzer = AccessibilityAnalyzer()
                accessibility_results = accessibility_analyzer.analyze(url)
                audit_results["results"]["accessibility"] = accessibility_results
                logger.info("Accessibility analysis completed successfully")
            except Exception as e:
                logger.error(f"Accessibility analysis failed: {str(e)}")
                audit_results["results"]["accessibility"] = {
                    "error": f"Accessibility analysis failed: {str(e)}",
                    "status": "failed"
                }
        
        # Calculate summary statistics
        try:
            for audit_type, results in audit_results["results"].items():
                if isinstance(results, dict) and not results.get("error"):
                    # Count issues
                    if "issues" in results:
                        audit_results["summary"]["total_issues"] += len(results["issues"])
                        audit_results["summary"]["critical_issues"] += len([
                            issue for issue in results["issues"] 
                            if issue.get("severity") == "high"
                        ])
                    
                    # Count warnings
                    if "warnings" in results:
                        audit_results["summary"]["warnings"] += len(results["warnings"])
                    
                    # Count recommendations
                    if "recommendations" in results:
                        audit_results["summary"]["recommendations"] += len(results["recommendations"])
        except Exception as e:
            logger.error(f"Error calculating summary statistics: {str(e)}")
            # Set safe defaults
            audit_results["summary"]["total_issues"] = 0
            audit_results["summary"]["critical_issues"] = 0
            audit_results["summary"]["warnings"] = 0
            audit_results["summary"]["recommendations"] = 0
        
        logger.info(f"Raw audit completed for URL: {url}")
        logger.info(f"Summary: {audit_results['summary']['total_issues']} issues, "
                   f"{audit_results['summary']['warnings']} warnings, "
                   f"{audit_results['summary']['recommendations']} recommendations")
        
        # Return raw audit results directly
        return jsonify({
            "success": True,
            "message": "Raw audit completed successfully",
            "audit_results": audit_results,
            "audit_engine_version": "2.0.0",
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Critical error during raw audit: {str(e)}")
        logger.error(traceback.format_exc())
        
        return jsonify({
            "error": "Internal server error during audit",
            "code": "AUDIT_ERROR",
            "details": str(e),
            "audit_engine_version": "2.0.0",
            "timestamp": datetime.now().isoformat()
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint not found",
        "code": "NOT_FOUND",
        "audit_engine_version": "2.0.0"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal server error",
        "code": "INTERNAL_ERROR",
        "audit_engine_version": "2.0.0"
    }), 500

if __name__ == '__main__':
    logger.info("Starting SitePulse Audit Tool API v2.0...")
    logger.info(f"Server will run on: http://0.0.0.0:5000")
    logger.info("Use Python 3.11 to run: C:\\Users\\Dell\\AppData\\Local\\Programs\\Python\\Python311\\python.exe app.py")
    logger.info("WebSocket support enabled for real-time updates")
    
    # Use socketio.run instead of app.run for WebSocket support
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
