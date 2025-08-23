from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

class ReportGenerator:
    def __init__(self):
        pass
    
    def generate_report(self, audit_results):
        """
        Generate comprehensive audit report with actionable recommendations
        """
        try:
            # Calculate overall scores and metrics
            overall_metrics = self._calculate_overall_metrics(audit_results)
            
            # Prioritize issues and recommendations
            prioritized_issues = self._prioritize_issues(audit_results)
            
            # Generate executive summary
            executive_summary = self._generate_executive_summary(audit_results, overall_metrics)
            
            # Generate detailed recommendations
            detailed_recommendations = self._generate_detailed_recommendations(audit_results)
            
            # Create final report structure
            final_report = {
                "metadata": {
                    "url": audit_results.get("url", ""),
                    "timestamp": audit_results.get("timestamp", datetime.now().isoformat()),
                    "audit_types": list(audit_results.get("results", {}).keys()),
                    "report_version": "1.0.0"
                },
                "executive_summary": executive_summary,
                "overall_metrics": overall_metrics,
                "prioritized_issues": prioritized_issues,
                "detailed_results": audit_results.get("results", {}),
                "recommendations": detailed_recommendations,
                "next_steps": self._generate_next_steps(prioritized_issues),
                "resources": self._get_helpful_resources()
            }
            
            return final_report
            
        except Exception as e:
            logger.error(f"Report generation error: {str(e)}")
            return {
                "error": "Failed to generate report",
                "details": str(e),
                "raw_results": audit_results
            }
    
    def _calculate_overall_metrics(self, audit_results):
        """Calculate overall metrics across all audit types"""
        metrics = {
            "overall_score": 0,
            "category_scores": {},
            "total_issues": 0,
            "critical_issues": 0,
            "high_issues": 0,
            "medium_issues": 0,
            "low_issues": 0,
            "total_recommendations": 0,
            "grade": "F"
        }
        
        try:
            results = audit_results.get("results", {})
            category_scores = []
            
            # Calculate scores for each category
            for category, category_results in results.items():
                score = category_results.get("score", 0)
                metrics["category_scores"][category] = {
                    "score": score,
                    "grade": self._score_to_grade(score)
                }
                category_scores.append(score)
                
                # Count issues by severity
                issues = category_results.get("issues", [])
                warnings = category_results.get("warnings", [])
                recommendations = category_results.get("recommendations", [])
                
                for issue in issues:
                    severity = issue.get("severity", "medium").lower()
                    if severity == "critical":
                        metrics["critical_issues"] += 1
                    elif severity == "high":
                        metrics["high_issues"] += 1
                    elif severity == "medium":
                        metrics["medium_issues"] += 1
                    else:
                        metrics["low_issues"] += 1
                
                for warning in warnings:
                    severity = warning.get("severity", "medium").lower()
                    if severity == "high":
                        metrics["high_issues"] += 1
                    elif severity == "medium":
                        metrics["medium_issues"] += 1
                    else:
                        metrics["low_issues"] += 1
                
                metrics["total_recommendations"] += len(recommendations)
            
            # Calculate overall score (weighted average)
            if category_scores:
                metrics["overall_score"] = round(sum(category_scores) / len(category_scores), 1)
            
            # Calculate total issues
            metrics["total_issues"] = (metrics["critical_issues"] + metrics["high_issues"] + 
                                    metrics["medium_issues"] + metrics["low_issues"])
            
            # Assign overall grade
            metrics["grade"] = self._score_to_grade(metrics["overall_score"])
            
        except Exception as e:
            logger.error(f"Metrics calculation error: {str(e)}")
        
        return metrics
    
    def _score_to_grade(self, score):
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
    
    def _prioritize_issues(self, audit_results):
        """Prioritize issues across all categories by severity and impact"""
        all_issues = []
        
        try:
            results = audit_results.get("results", {})
            
            for category, category_results in results.items():
                # Add issues
                issues = category_results.get("issues", [])
                for issue in issues:
                    all_issues.append({
                        "category": category,
                        "type": "issue",
                        "severity": issue.get("severity", "medium").lower(),
                        "message": issue.get("message", ""),
                        "recommendation": issue.get("recommendation", ""),
                        "impact": self._calculate_impact(issue.get("severity", "medium"), category)
                    })
                
                # Add warnings
                warnings = category_results.get("warnings", [])
                for warning in warnings:
                    all_issues.append({
                        "category": category,
                        "type": "warning",
                        "severity": warning.get("severity", "medium").lower(),
                        "message": warning.get("message", ""),
                        "recommendation": warning.get("recommendation", ""),
                        "impact": self._calculate_impact(warning.get("severity", "medium"), category)
                    })
            
            # Sort by impact (highest first)
            all_issues.sort(key=lambda x: x["impact"], reverse=True)
            
            # Group by severity
            prioritized = {
                "critical": [issue for issue in all_issues if issue["severity"] == "critical"],
                "high": [issue for issue in all_issues if issue["severity"] == "high"],
                "medium": [issue for issue in all_issues if issue["severity"] == "medium"],
                "low": [issue for issue in all_issues if issue["severity"] == "low"]
            }
            
        except Exception as e:
            logger.error(f"Issue prioritization error: {str(e)}")
            prioritized = {"critical": [], "high": [], "medium": [], "low": []}
        
        return prioritized
    
    def _calculate_impact(self, severity, category):
        """Calculate impact score for prioritization"""
        severity_weights = {
            "critical": 100,
            "high": 75,
            "medium": 50,
            "low": 25
        }
        
        category_weights = {
            "security": 1.5,  # Security issues have higher impact
            "accessibility": 1.3,  # Accessibility is important for compliance
            "seo": 1.2,  # SEO affects visibility
            "performance": 1.1  # Performance affects user experience
        }
        
        base_score = severity_weights.get(severity.lower(), 50)
        category_multiplier = category_weights.get(category.lower(), 1.0)
        
        return base_score * category_multiplier
    
    def _generate_executive_summary(self, audit_results, overall_metrics):
        """Generate executive summary for stakeholders"""
        summary = {
            "website_info": {},
            "overview": "",
            "key_findings": [],
            "immediate_actions": [],
            "business_impact": "",
            "timeline": ""
        }
        
        try:
            url = audit_results.get("url", "your website")
            overall_score = overall_metrics.get("overall_score", 0)
            grade = overall_metrics.get("grade", "F")
            total_issues = overall_metrics.get("total_issues", 0)
            critical_issues = overall_metrics.get("critical_issues", 0)
            
            # Extract website information from SEO results
            results = audit_results.get("results", {})
            seo_results = results.get("seo", {})
            website_info = seo_results.get("website_info", {})
            summary["website_info"] = website_info
            
            # Generate overview with website context
            site_name = website_info.get("company_name") or website_info.get("title", "Your website")
            site_type = website_info.get("website_type", "website")
            site_purpose = website_info.get("estimated_purpose", "")
            site_industry = website_info.get("industry", "")
            
            # Create contextual description
            context_desc = ""
            if site_name and site_name != "Your website":
                context_desc = f"{site_name}"
                if site_industry and site_industry != "General/Other":
                    context_desc += f" ({site_industry})"
                if site_type and site_type != "General Website":
                    context_desc += f" - {site_type}"
            else:
                context_desc = f"This {site_type.lower()}"
            
            if site_purpose:
                context_desc += f" that aims to {site_purpose.lower()}"
            
            if overall_score >= 80:
                summary["overview"] = f"Great news! {context_desc} demonstrates strong digital health with an overall score of {overall_score}/100 (Grade {grade}). The website follows most best practices with only minor improvements needed."
            elif overall_score >= 60:
                summary["overview"] = f"{context_desc} shows moderate digital health with an overall score of {overall_score}/100 (Grade {grade}). There are several areas for improvement that could significantly enhance the website's performance, security, and user experience."
            else:
                summary["overview"] = f"{context_desc} requires immediate attention with an overall score of {overall_score}/100 (Grade {grade}). Critical issues have been identified that could impact the website's security, search rankings, and user accessibility."
            
            # Key findings
            results = audit_results.get("results", {})
            for category, category_results in results.items():
                category_score = category_results.get("score", 0)
                if category_score < 70:
                    summary["key_findings"].append(f"{category.title()}: {category_score}/100 - Needs significant improvement")
                elif category_score < 85:
                    summary["key_findings"].append(f"{category.title()}: {category_score}/100 - Good with room for optimization")
                else:
                    summary["key_findings"].append(f"{category.title()}: {category_score}/100 - Excellent performance")
            
            # Immediate actions
            if critical_issues > 0:
                summary["immediate_actions"].append(f"Address {critical_issues} critical security and accessibility issues immediately")
            
            high_issues = overall_metrics.get("high_issues", 0)
            if high_issues > 0:
                summary["immediate_actions"].append(f"Resolve {high_issues} high-priority issues within 2 weeks")
            
            # Business impact
            impact_areas = []
            if "security" in results and results["security"].get("score", 0) < 70:
                impact_areas.append("security vulnerabilities risk data breaches and customer trust")
            if "seo" in results and results["seo"].get("score", 0) < 70:
                impact_areas.append("SEO issues limit search engine visibility and organic traffic")
            if "performance" in results and results["performance"].get("score", 0) < 70:
                impact_areas.append("performance problems increase bounce rates and reduce conversions")
            if "accessibility" in results and results["accessibility"].get("score", 0) < 70:
                impact_areas.append("accessibility barriers exclude users with disabilities and may violate compliance requirements")
            
            if impact_areas:
                summary["business_impact"] = f"Key business impacts: {'; '.join(impact_areas)}."
            else:
                summary["business_impact"] = "Your website maintains good standards across all areas with minimal business risk."
            
            # Timeline
            if critical_issues > 0:
                summary["timeline"] = "Immediate action required for critical issues (within 24-48 hours), followed by systematic resolution of other issues over 2-4 weeks."
            elif high_issues > 0:
                summary["timeline"] = "High-priority issues should be addressed within 1-2 weeks, with ongoing improvements over the following month."
            else:
                summary["timeline"] = "Continue regular monitoring and implement recommended optimizations over the next month."
        
        except Exception as e:
            logger.error(f"Executive summary generation error: {str(e)}")
            summary["overview"] = "An audit was completed, but there was an error generating the executive summary."
        
        return summary
    
    def _generate_detailed_recommendations(self, audit_results):
        """Generate detailed, actionable recommendations"""
        recommendations = {
            "quick_wins": [],  # Easy fixes with high impact
            "short_term": [],  # 1-2 weeks
            "medium_term": [],  # 1-3 months
            "long_term": [],  # 3+ months
            "by_category": {}
        }
        
        try:
            results = audit_results.get("results", {})
            
            for category, category_results in results.items():
                category_recommendations = []
                
                # Process issues
                issues = category_results.get("issues", [])
                warnings = category_results.get("warnings", [])
                recs = category_results.get("recommendations", [])
                
                all_items = issues + warnings + recs
                
                for item in all_items:
                    rec = {
                        "title": item.get("message", ""),
                        "description": item.get("recommendation", ""),
                        "severity": item.get("severity", "medium"),
                        "effort": self._estimate_effort(item),
                        "impact": self._estimate_business_impact(item, category),
                        "category": category
                    }
                    
                    category_recommendations.append(rec)
                    
                    # Categorize by timeline
                    if rec["effort"] == "low" and rec["impact"] == "high":
                        recommendations["quick_wins"].append(rec)
                    elif rec["severity"] in ["critical", "high"]:
                        recommendations["short_term"].append(rec)
                    elif rec["effort"] in ["medium"]:
                        recommendations["medium_term"].append(rec)
                    else:
                        recommendations["long_term"].append(rec)
                
                recommendations["by_category"][category] = category_recommendations
            
            # Sort each category by impact/effort ratio
            for timeline in ["quick_wins", "short_term", "medium_term", "long_term"]:
                recommendations[timeline].sort(key=lambda x: self._calculate_priority_score(x), reverse=True)
        
        except Exception as e:
            logger.error(f"Detailed recommendations generation error: {str(e)}")
        
        return recommendations
    
    def _estimate_effort(self, item):
        """Estimate implementation effort"""
        message = item.get("message", "").lower()
        recommendation = item.get("recommendation", "").lower()
        
        # Low effort indicators
        low_effort_keywords = ["add", "include", "enable", "set", "meta tag", "alt text", "title", "header"]
        if any(keyword in message or keyword in recommendation for keyword in low_effort_keywords):
            return "low"
        
        # High effort indicators
        high_effort_keywords = ["implement", "redesign", "restructure", "migrate", "rebuild", "comprehensive"]
        if any(keyword in message or keyword in recommendation for keyword in high_effort_keywords):
            return "high"
        
        return "medium"
    
    def _estimate_business_impact(self, item, category):
        """Estimate business impact"""
        severity = item.get("severity", "medium").lower()
        
        # High impact categories and severities
        if category in ["security", "accessibility"] and severity in ["critical", "high"]:
            return "high"
        
        if category == "seo" and any(keyword in item.get("message", "").lower() 
                                   for keyword in ["title", "meta description", "h1", "ssl"]):
            return "high"
        
        if category == "performance" and any(keyword in item.get("message", "").lower()
                                           for keyword in ["load time", "page size", "critical"]):
            return "high"
        
        if severity == "critical":
            return "high"
        elif severity == "high":
            return "medium"
        else:
            return "low"
    
    def _calculate_priority_score(self, recommendation):
        """Calculate priority score for sorting"""
        severity_scores = {"critical": 100, "high": 75, "medium": 50, "low": 25}
        effort_scores = {"low": 3, "medium": 2, "high": 1}
        impact_scores = {"high": 3, "medium": 2, "low": 1}
        
        severity_score = severity_scores.get(recommendation.get("severity", "medium"), 50)
        effort_score = effort_scores.get(recommendation.get("effort", "medium"), 2)
        impact_score = impact_scores.get(recommendation.get("impact", "medium"), 2)
        
        # Priority = (Severity + Impact) / Effort
        return (severity_score + impact_score * 25) / effort_score
    
    def _generate_next_steps(self, prioritized_issues):
        """Generate actionable next steps"""
        next_steps = {
            "immediate": [],
            "week_1": [],
            "week_2_4": [],
            "ongoing": []
        }
        
        try:
            # Immediate actions (critical issues)
            critical_issues = prioritized_issues.get("critical", [])
            for issue in critical_issues[:5]:  # Top 5 critical
                next_steps["immediate"].append({
                    "action": f"Fix: {issue['message']}",
                    "category": issue["category"],
                    "description": issue["recommendation"]
                })
            
            # Week 1 actions (high priority issues)
            high_issues = prioritized_issues.get("high", [])
            for issue in high_issues[:3]:  # Top 3 high priority
                next_steps["week_1"].append({
                    "action": f"Address: {issue['message']}",
                    "category": issue["category"],
                    "description": issue["recommendation"]
                })
            
            # Week 2-4 actions (medium priority)
            medium_issues = prioritized_issues.get("medium", [])
            for issue in medium_issues[:5]:  # Top 5 medium priority
                next_steps["week_2_4"].append({
                    "action": f"Improve: {issue['message']}",
                    "category": issue["category"],
                    "description": issue["recommendation"]
                })
            
            # Ongoing actions
            next_steps["ongoing"] = [
                {
                    "action": "Regular security monitoring",
                    "category": "security",
                    "description": "Set up automated security scanning and monitoring"
                },
                {
                    "action": "Performance monitoring",
                    "category": "performance", 
                    "description": "Implement continuous performance monitoring and alerting"
                },
                {
                    "action": "SEO tracking",
                    "category": "seo",
                    "description": "Monitor search rankings and organic traffic regularly"
                },
                {
                    "action": "Accessibility testing",
                    "category": "accessibility",
                    "description": "Include accessibility testing in your development workflow"
                }
            ]
        
        except Exception as e:
            logger.error(f"Next steps generation error: {str(e)}")
        
        return next_steps
    
    def _get_helpful_resources(self):
        """Provide helpful resources and tools"""
        return {
            "security": {
                "tools": [
                    {"name": "OWASP ZAP", "url": "https://owasp.org/www-project-zap/", "description": "Free security testing tool"},
                    {"name": "SSL Labs", "url": "https://www.ssllabs.com/ssltest/", "description": "SSL configuration test"},
                    {"name": "Security Headers", "url": "https://securityheaders.com/", "description": "HTTP security headers analysis"}
                ],
                "guides": [
                    {"title": "OWASP Top 10", "url": "https://owasp.org/www-project-top-ten/"},
                    {"title": "Web Security Checklist", "url": "https://web.dev/security-checklist/"}
                ]
            },
            "performance": {
                "tools": [
                    {"name": "Google PageSpeed Insights", "url": "https://pagespeed.web.dev/", "description": "Performance analysis tool"},
                    {"name": "WebPageTest", "url": "https://www.webpagetest.org/", "description": "Detailed performance testing"},
                    {"name": "GTmetrix", "url": "https://gtmetrix.com/", "description": "Website speed and performance monitoring"}
                ],
                "guides": [
                    {"title": "Web Vitals", "url": "https://web.dev/vitals/"},
                    {"title": "Performance Best Practices", "url": "https://web.dev/fast/"}
                ]
            },
            "seo": {
                "tools": [
                    {"name": "Google Search Console", "url": "https://search.google.com/search-console/", "description": "Monitor search performance"},
                    {"name": "Structured Data Testing", "url": "https://search.google.com/test/rich-results", "description": "Test structured data markup"},
                    {"name": "Mobile-Friendly Test", "url": "https://search.google.com/test/mobile-friendly", "description": "Check mobile compatibility"}
                ],
                "guides": [
                    {"title": "SEO Starter Guide", "url": "https://developers.google.com/search/docs/beginner/seo-starter-guide"},
                    {"title": "Technical SEO Guide", "url": "https://web.dev/lighthouse-seo/"}
                ]
            },
            "accessibility": {
                "tools": [
                    {"name": "WAVE", "url": "https://wave.webaim.org/", "description": "Web accessibility evaluation tool"},
                    {"name": "axe DevTools", "url": "https://www.deque.com/axe/devtools/", "description": "Browser extension for accessibility testing"},
                    {"name": "Color Contrast Analyzer", "url": "https://www.tpgi.com/color-contrast-checker/", "description": "Check color contrast ratios"}
                ],
                "guides": [
                    {"title": "WCAG Guidelines", "url": "https://www.w3.org/WAI/WCAG21/quickref/"},
                    {"title": "A11y Project Checklist", "url": "https://www.a11yproject.com/checklist/"}
                ]
            },
            "general": {
                "documentation": [
                    {"title": "MDN Web Docs", "url": "https://developer.mozilla.org/", "description": "Comprehensive web development documentation"},
                    {"title": "Web.dev", "url": "https://web.dev/", "description": "Modern web development best practices"}
                ]
            }
        }
