import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useAudit } from '../contexts/AuditContext';
import { 
  ArrowLeft, 
  Download, 
  Share2, 
  Shield, 
  Zap, 
  Search, 
  Eye,
  AlertTriangle,
  CheckCircle,
  XCircle,
  TrendingUp,
  Clock,
  Lightbulb,
  Target,
  RefreshCw,
  Printer
} from 'lucide-react';
import ScoreCard from '../components/ScoreCard';
import IssuesList from '../components/IssuesList';
import RecommendationsList from '../components/RecommendationsList';
import MetricsChart from '../components/MetricsChart';
import ScreenshotViewer from '../components/ScreenshotViewer';

const ReportPage = () => {
  const { reportId } = useParams();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  
  // Use the real-time audit context
  const { auditResults, auditSummary, auditData } = useAudit();

  useEffect(() => {
    // First try to load from localStorage (for existing reports)
    const reportData = localStorage.getItem(`report_${reportId}`);
    if (reportData) {
      try {
        const parsedData = JSON.parse(reportData);
        
        // Validate the data structure
        if (parsedData.results && Object.keys(parsedData.results).length > 0) {
        setReport(parsedData);
        } else {
          // If localStorage data is incomplete, try context
          if (Object.keys(auditResults).length > 0) {
            const realTimeReport = {
              url: parsedData.url || 'Current Audit',
              timestamp: parsedData.timestamp || new Date().toISOString(),
              results: auditResults,
              summary: auditSummary,
              audit_types: Object.keys(auditResults)
            };
            setReport(realTimeReport);
          } else {
            setReport(null);
          }
        }
      } catch (error) {
        setReport(null);
      }
    } else {
      // If no localStorage data, try to use current real-time data
      if (Object.keys(auditResults).length > 0) {
        const realTimeReport = {
          url: 'Current Audit',
          timestamp: new Date().toISOString(),
          results: auditResults,
          summary: auditSummary,
          audit_types: Object.keys(auditResults)
        };
        setReport(realTimeReport);
      } else {
        // Try to find any recent report data
        const keys = Object.keys(localStorage);
        const reportKeys = keys.filter(key => key.startsWith('report_'));
        if (reportKeys.length > 0) {
          // Try the most recent report
          const mostRecentKey = reportKeys.sort().pop();
          const recentData = localStorage.getItem(mostRecentKey);
          if (recentData) {
            try {
              const parsedRecent = JSON.parse(recentData);
              setReport(parsedRecent);
            } catch (e) {
              setReport(null);
            }
          }
        } else {
          setReport(null);
        }
      }
    }
    setLoading(false);
  }, [reportId, auditResults, auditSummary]);

  // Transform audit results to the format expected by components
  const transformAuditData = (results) => {
    if (!results || typeof results !== 'object') {
      return {};
    }
    
    const categoryScores = {};
    
    Object.entries(results).forEach(([category, data]) => {
      if (data && !data.error) {
        const score = data.score || 0;
        const grade = score >= 90 ? 'A' : score >= 80 ? 'B' : score >= 70 ? 'C' : score >= 60 ? 'D' : 'F';
        
        categoryScores[category] = {
          score: score,
          grade: grade,
          issues: data.issues || [],
          recommendations: data.recommendations || []
        };
      }
    });
    
    return categoryScores;
  };

  // Calculate overall metrics from audit results
  const calculateOverallMetrics = (results) => {
    if (!results || typeof results !== 'object') {
      return {
        overall_score: 0,
        grade: 'F',
        critical_issues: 0,
        high_issues: 0,
        medium_issues: 0,
        total_recommendations: 0,
        category_scores: {}
      };
    }
    
    const categoryScores = transformAuditData(results);
    const scores = Object.values(categoryScores).map(cat => cat.score);
    const overallScore = scores.length > 0 ? Math.round(scores.reduce((a, b) => a + b, 0) / scores.length) : 0;
    const overallGrade = overallScore >= 90 ? 'A' : overallScore >= 80 ? 'B' : overallScore >= 70 ? 'C' : overallScore >= 60 ? 'D' : 'F';
    
    // Count issues by priority
    let criticalIssues = 0;
    let highIssues = 0;
    let mediumIssues = 0;
    let totalRecommendations = 0;
    
    Object.values(results).forEach(category => {
      if (category && !category.error) {
        if (category.issues && Array.isArray(category.issues)) {
          category.issues.forEach(issue => {
            if (issue.priority === 'critical') criticalIssues++;
            else if (issue.priority === 'high') highIssues++;
            else if (issue.priority === 'medium') mediumIssues++;
          });
        }
        if (category.recommendations && Array.isArray(category.recommendations)) {
          totalRecommendations += category.recommendations.length;
        }
      }
    });
    
    return {
      overall_score: overallScore,
      grade: overallGrade,
      critical_issues: criticalIssues,
      high_issues: highIssues,
      medium_issues: mediumIssues,
      total_recommendations: totalRecommendations,
      category_scores: categoryScores
    };
  };

  // Extract all issues from audit results
  const extractAllIssues = (results) => {
    if (!results || typeof results !== 'object') {
      return [];
    }
    
    const allIssues = [];
    
    // Debug: Log the structure of results
    console.log('Extracting issues from results:', results);
    
    Object.entries(results).forEach(([category, data]) => {
      console.log(`Processing category: ${category}`, data);
      
      if (data && !data.error) {
        // Check for issues array
        if (data.issues && Array.isArray(data.issues)) {
          data.issues.forEach(issue => {
            allIssues.push({
              ...issue,
              category: category,
              priority: issue.priority || 'medium',
              title: issue.title || issue.message || `Issue in ${category}`,
              description: issue.description || issue.message || 'No description available.',
              impact: issue.impact || 'Medium',
              suggestion: issue.suggestion || 'Review and address this issue.'
            });
          });
        }
        
        // Check for problems array (alternative structure)
        if (data.problems && Array.isArray(data.problems)) {
          data.problems.forEach(problem => {
            allIssues.push({
              ...problem,
              category: category,
              priority: problem.priority || 'medium',
              title: problem.title || problem.message || `Problem in ${category}`,
              description: problem.description || problem.message || 'No description available.',
              impact: problem.impact || 'Medium',
              suggestion: problem.suggestion || 'Review and address this problem.'
            });
          });
        }
        
        // Check for vulnerabilities array (security specific)
        if (data.vulnerabilities && Array.isArray(data.vulnerabilities)) {
          data.vulnerabilities.forEach(vuln => {
            allIssues.push({
              ...vuln,
              category: category,
              priority: 'critical',
              title: vuln.title || vuln.name || `Vulnerability in ${category}`,
              description: vuln.description || vuln.details || 'Security vulnerability detected.',
              impact: 'High',
              suggestion: vuln.recommendation || 'Address this security vulnerability immediately.'
            });
          });
        }
        
        // Check for warnings array
        if (data.warnings && Array.isArray(data.warnings)) {
          data.warnings.forEach(warning => {
            allIssues.push({
              ...warning,
              category: category,
              priority: 'medium',
              title: warning.title || warning.message || `Warning in ${category}`,
              description: warning.description || warning.message || 'Warning detected.',
              impact: 'Medium',
              suggestion: warning.recommendation || 'Review and consider addressing this warning.'
            });
          });
        }
        
        // If no structured issues found, create issues from score and general data
        if (data.score !== undefined && data.score < 90) {
          const score = data.score;
          let priority = 'medium';
          let impact = 'Medium';
          
          if (score < 60) {
            priority = 'critical';
            impact = 'High';
          } else if (score < 80) {
            priority = 'high';
            impact = 'Medium';
          }
          
          // Create user-friendly issue descriptions based on category and score
          let issueTitle = '';
          let issueDescription = '';
          let issueSuggestion = '';
          
          switch (category) {
            case 'performance':
              issueTitle = `Website Speed Needs Improvement (${score}/100)`;
              issueDescription = `Your website is loading slower than ideal, which can frustrate visitors and hurt your search engine rankings.`;
              issueSuggestion = `Focus on optimizing images, enabling compression, and reducing unnecessary code to improve loading speed.`;
              break;
            case 'seo':
              issueTitle = `Search Engine Optimization Score: ${score}/100`;
              issueDescription = `Your website could be better optimized for search engines, which means fewer people might find you online.`;
              issueSuggestion = `Add page descriptions, improve content structure, and ensure all pages have proper titles and meta information.`;
              break;
            case 'accessibility':
              issueTitle = `Accessibility Score: ${score}/100`;
              issueDescription = `Your website may not be fully accessible to all users, including those with disabilities.`;
              issueSuggestion = `Add image descriptions, improve keyboard navigation, and ensure proper color contrast for better accessibility.`;
              break;
            case 'security':
              issueTitle = `Security Score: ${score}/100`;
              issueDescription = `Your website has security vulnerabilities that could put your users and data at risk.`;
              issueSuggestion = `Update security certificates, fix vulnerabilities, and ensure all security best practices are followed.`;
              break;
            default:
              issueTitle = `${category.charAt(0).toUpperCase() + category.slice(1)} Score: ${score}/100`;
              issueDescription = `The ${category} audit shows a score of ${score}/100, which indicates areas for improvement.`;
              issueSuggestion = `Review the detailed ${category} analysis and implement the recommended improvements to raise your score.`;
          }
          
          allIssues.push({
            category: category,
            priority: priority,
            title: issueTitle,
            description: issueDescription,
            impact: impact,
            suggestion: issueSuggestion
          });
        }
      }
    });
    
    console.log('Extracted issues:', allIssues);
    return allIssues;
  };

  // Helper function to make technical recommendations more user-friendly
  const makeRecommendationUserFriendly = (title, description, category) => {
    // Common technical terms and their user-friendly translations
    const technicalTranslations = {
      'schema markup': 'structured data for search engines',
      'structured data': 'organized information for search engines',
      'meta tags': 'page description tags',
      'meta description': 'page summary for search results',
      'title tag': 'page title for search results',
      'alt text': 'image descriptions for accessibility',
      'alt attributes': 'image descriptions for accessibility',
      'gzip compression': 'file compression to speed up loading',
      'browser caching': 'storing files locally for faster loading',
      'minification': 'removing unnecessary code to speed up loading',
      'lazy loading': 'loading images only when needed',
      'CDN': 'content delivery network for faster loading',
      'SSL certificate': 'security certificate for your website',
      'HTTPS': 'secure version of your website',
      'mobile responsive': 'mobile-friendly design',
      'responsive design': 'design that works on all devices',
      'core web vitals': 'website performance metrics',
      'LCP': 'how fast your main content loads',
      'FID': 'how quickly your site responds to clicks',
      'CLS': 'how stable your page layout is',
      'accessibility': 'making your site usable for everyone',
      'ARIA labels': 'accessibility labels for screen readers',
      'semantic HTML': 'meaningful HTML structure',
      'breadcrumbs': 'navigation path for users',
      'sitemap': 'list of all your website pages',
      'robots.txt': 'instructions for search engine crawlers',
      'canonical URL': 'preferred version of a page',
      '301 redirect': 'permanent page redirect',
      '404 error': 'page not found error',
      'broken links': 'links that don\'t work',
      'internal linking': 'links between your own pages',
      'external linking': 'links to other websites',
      'backlinks': 'links from other websites to yours',
      'page speed': 'how fast your pages load',
      'load time': 'time it takes for pages to load',
      'server response time': 'how quickly your server responds',
      'database optimization': 'making your database faster',
      'query optimization': 'making database searches faster',
      'indexing': 'how search engines organize your content',
      'crawling': 'how search engines explore your site',
      'SEO': 'search engine optimization',
      'keywords': 'words people search for',
      'meta keywords': 'search terms for your page',
      'social media tags': 'tags for social media sharing',
      'Open Graph': 'social media preview tags',
      'Twitter Cards': 'Twitter preview tags',
      'favicon': 'small icon for your website',
      'manifest file': 'app-like settings for your website',
      'service worker': 'background script for offline functionality',
      'PWA': 'progressive web app features',
      'offline functionality': 'website working without internet',
      'push notifications': 'website notifications to users',
      'install prompt': 'option to install website as app'
    };

    // Translate technical terms in title and description
    let friendlyTitle = title;
    let friendlyDescription = description;

    Object.entries(technicalTranslations).forEach(([technical, friendly]) => {
      const regex = new RegExp(technical, 'gi');
      friendlyTitle = friendlyTitle.replace(regex, friendly);
      friendlyDescription = friendlyDescription.replace(regex, friendly);
    });

    // Add category-specific context
    let categoryContext = '';
    switch (category) {
      case 'seo':
        categoryContext = 'This will help search engines better understand and display your content.';
        break;
      case 'performance':
        categoryContext = 'This will make your website load faster and provide a better user experience.';
        break;
      case 'accessibility':
        categoryContext = 'This will make your website more usable for people with disabilities.';
        break;
      case 'security':
        categoryContext = 'This will protect your website and users from security threats.';
        break;
      default:
        categoryContext = 'This will improve your website\'s overall quality and user experience.';
    }

    // Make the description more actionable
    if (friendlyDescription.toLowerCase().includes('consider adding') || 
        friendlyDescription.toLowerCase().includes('should add') ||
        friendlyDescription.toLowerCase().includes('missing')) {
      friendlyDescription = friendlyDescription.replace(
        /(consider adding|should add|missing)/gi,
        'Add'
      );
      friendlyDescription += ` ${categoryContext}`;
    }

    // Make it more conversational
    if (friendlyDescription.toLowerCase().includes('no structured data found')) {
      friendlyTitle = 'Add Structured Data for Better Search Results';
      friendlyDescription = `Help search engines understand your content better by adding structured data. This will make your website appear more prominently in search results with rich snippets, ratings, and other enhanced information. ${categoryContext}`;
    }

    if (friendlyDescription.toLowerCase().includes('missing meta description')) {
      friendlyTitle = 'Add Page Descriptions for Search Results';
      friendlyDescription = `Each page should have a clear description that appears in search results. This helps users understand what your page is about before they click on it. ${categoryContext}`;
    }

    if (friendlyDescription.toLowerCase().includes('missing title tag')) {
      friendlyTitle = 'Add Clear Page Titles';
      friendlyDescription = `Every page needs a descriptive title that appears in browser tabs and search results. This helps users and search engines understand what your page contains. ${categoryContext}`;
    }

    return {
      title: friendlyTitle,
      description: friendlyDescription
    };
  };

  // Extract all recommendations from audit results
  const extractAllRecommendations = (results) => {
    if (!results || typeof results !== 'object') {
      return {
        quick_wins: [],
        short_term: [],
        medium_term: [],
        long_term: []
      };
    }
    
    const allRecommendations = {
      quick_wins: [],
      short_term: [],
      medium_term: [],
      long_term: []
    };
    
    Object.entries(results).forEach(([category, data]) => {
      if (data && !data.error && data.recommendations && Array.isArray(data.recommendations)) {
        data.recommendations.forEach(rec => {
          // Make the recommendation user-friendly
          const friendlyRec = makeRecommendationUserFriendly(
            rec.title || rec.message || `Recommendation for ${category}`,
            rec.description || rec.message || 'No description available.',
            category
          );

          const recommendation = {
            title: friendlyRec.title,
            description: friendlyRec.description,
            effort: rec.effort || 'Medium',
            impact: rec.impact || 'Medium',
            timeline: rec.timeline || 'short_term',
            category: category
          };
          
          // Categorize by timeline/effort
          if (recommendation.timeline === 'quick' || recommendation.effort === 'Low') {
            allRecommendations.quick_wins.push(recommendation);
          } else if (recommendation.timeline === 'short' || recommendation.effort === 'Medium') {
            allRecommendations.short_term.push(recommendation);
          } else if (recommendation.timeline === 'medium' || recommendation.effort === 'High') {
            allRecommendations.medium_term.push(recommendation);
          } else {
            allRecommendations.long_term.push(recommendation);
          }
        });
      }
    });
    
    // If no recommendations found, add some fallback ones
    if (Object.values(allRecommendations).every(arr => arr.length === 0)) {
      allRecommendations.quick_wins.push({
        title: 'Optimize Images for Faster Loading',
        description: 'Compress and resize images to make your website load faster. Large images slow down page loading and frustrate users.',
        effort: 'Low',
        impact: 'High',
        timeline: 'quick',
        category: 'performance'
      });
      allRecommendations.short_term.push({
        title: 'Enable File Compression',
        description: 'Turn on server-side compression to make your website files smaller and load faster. This is a simple setting that can significantly improve speed.',
        effort: 'Medium',
        impact: 'High',
        timeline: 'short',
        category: 'performance'
      });
      allRecommendations.short_term.push({
        title: 'Add Page Descriptions',
        description: 'Create clear descriptions for each page that explain what visitors will find. These descriptions appear in search results and help users decide whether to visit your page.',
        effort: 'Low',
        impact: 'Medium',
        timeline: 'short',
        category: 'seo'
      });
    }
    
    return allRecommendations;
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-lg text-gray-600">Loading report...</p>
        </div>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md mx-auto">
            <XCircle className="h-16 w-16 text-red-500 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-red-800 mb-2">Report Not Found</h2>
            <p className="text-red-600 mb-4">
              Unable to load the report data. This could be due to:
            </p>
            <ul className="text-sm text-red-600 text-left mb-4 space-y-1">
              <li>• Report data was not saved properly</li>
              <li>• Report ID is invalid or expired</li>
              <li>• Local storage is full or corrupted</li>
            </ul>
            <div className="flex space-x-2 justify-center">
              <Link to="/audit" className="btn btn-primary">
                Start New Audit
              </Link>
              <button 
                onClick={() => window.location.reload()} 
                className="btn btn-secondary"
              >
                Reload Page
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Use real-time data if available, otherwise fall back to report data
  const currentResults = Object.keys(auditResults).length > 0 ? auditResults : (report?.results || {});
  const currentSummary = Object.keys(auditSummary).length > 0 ? auditSummary : (report?.summary || {});
  
  // Extract all issues and recommendations from current results
  const allIssues = extractAllIssues(currentResults);
  const allRecommendations = extractAllRecommendations(currentResults);
  
  // Ensure we have valid data before processing
  if (!currentResults || Object.keys(currentResults).length === 0) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 max-w-md mx-auto">
            <AlertTriangle className="h-16 w-16 text-yellow-500 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-yellow-800 mb-2">No Audit Data Available</h2>
            <p className="text-yellow-600 mb-4">
              The report page loaded but no audit data was found. This could happen if:
            </p>
            <ul className="text-sm text-yellow-600 text-left mb-4 space-y-1">
              <li>• The audit was interrupted</li>
              <li>• Data wasn't saved properly</li>
              <li>• The page was refreshed before data loaded</li>
            </ul>
            <div className="flex space-x-2 justify-center">
          <Link to="/audit" className="btn btn-primary">
            Start New Audit
          </Link>
              <button 
                onClick={() => window.location.reload()} 
                className="btn btn-secondary"
              >
                Reload Page
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Safely calculate metrics with fallbacks
  const overallMetrics = calculateOverallMetrics(currentResults || {});
  const categoryScores = overallMetrics?.category_scores || {};
  
  // Helper functions to extract data from audit results
  // const allIssues = extractAllIssues(currentResults || {}); // Moved outside
  // const allRecommendations = extractAllRecommendations(currentResults || {}); // Moved outside

  const categoryIcons = {
    security: Shield,
    performance: Zap,
    seo: Search,
    accessibility: Eye
  };

  // Helper function to get icon with fallback
  const getCategoryIcon = (category) => {
    return categoryIcons[category] || Shield;
  };

  const categoryColors = {
    security: { color: 'text-red-500', bg: 'bg-red-50' },
    performance: { color: 'text-yellow-500', bg: 'bg-yellow-50' },
    seo: { color: 'text-blue-500', bg: 'bg-blue-50' },
    accessibility: { color: 'text-green-500', bg: 'bg-green-50' }
  };

  // Helper function to get colors with fallback
  const getCategoryColors = (category) => {
    return categoryColors[category] || { color: 'text-gray-500', bg: 'bg-gray-50' };
  };

  const getGradeColor = (grade) => {
    const colors = {
      'A': 'text-green-600 bg-green-100',
      'B': 'text-blue-600 bg-blue-100',
      'C': 'text-yellow-600 bg-yellow-100',
      'D': 'text-orange-600 bg-orange-100',
      'F': 'text-red-600 bg-red-100'
    };
    return colors[grade] || 'text-gray-600 bg-gray-100';
  };

  const tabs = [
    { id: 'overview', label: 'Overview', icon: TrendingUp },
    { id: 'issues', label: 'Issues', icon: AlertTriangle },
    { id: 'recommendations', label: 'Recommendations', icon: CheckCircle },
    { id: 'details', label: 'Detailed Results', icon: Search }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Enhanced Header with Better Visual Hierarchy */}
      <div className="bg-white shadow-sm border-b">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link to="/audit" className="btn btn-outline hover:bg-gray-50 transition-all duration-200 hover:scale-105">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Audit
            </Link>
              <div className="animate-fade-in">
                <h1 className="text-2xl font-bold text-gray-900">Audit Report</h1>
                <p className="text-gray-600">
                  {report?.url || 'Current Audit'} • {report?.timestamp ? new Date(report.timestamp).toLocaleString() : 'Recent'}
                </p>
                    </div>
                  </div>
            <div className="text-right animate-fade-in-delay">
              <div className="text-sm text-gray-500">Report Generated</div>
              <div className="text-sm font-medium text-gray-900">
                {report?.timestamp ? new Date(report.timestamp).toLocaleDateString() : 'Recently'}
                </div>
              </div>
            </div>
          </div>
        </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Enhanced Executive Summary with Better Visual Design */}
        <div className="card mb-8 overflow-hidden animate-slide-up">
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 border-b border-gray-200">
            <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold text-gray-900">Executive Summary</h2>
            <div className="flex items-center space-x-4">
                <div className="text-center transform hover:scale-110 transition-transform duration-200">
                  <div className={`text-4xl font-bold px-6 py-3 rounded-xl shadow-sm ${getGradeColor(overallMetrics.grade || 'N')}`}>
                    {overallMetrics.grade || 'N'}
                  </div>
                  <p className="text-sm text-gray-600 mt-2 font-medium">Overall Grade</p>
                </div>
                <div className="text-center transform hover:scale-110 transition-transform duration-200">
                  <div className="text-4xl font-bold text-gray-900 bg-white px-6 py-3 rounded-xl shadow-sm">
                    {overallMetrics.overall_score || 0}
              </div>
                  <p className="text-sm text-gray-600 mt-2 font-medium">Score</p>
                </div>
              </div>
            </div>
            
            <p className="text-gray-700 mb-6 leading-relaxed text-lg">
              {currentSummary.overview || 'Comprehensive website audit completed successfully. Review the detailed analysis below for actionable insights and recommendations.'}
            </p>
          </div>
          
          {/* Enhanced Key Metrics with Better Visual Design */}
          <div className="p-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              <div className="text-center p-6 bg-red-50 rounded-xl border border-red-200 hover:bg-red-100 hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1">
                <div className="text-3xl font-bold text-red-600 mb-2">{overallMetrics.critical_issues || 0}</div>
                <p className="text-sm text-red-700 font-medium">Critical Issues</p>
                <p className="text-xs text-red-600 mt-1">High Priority</p>
            </div>
              <div className="text-center p-6 bg-orange-50 rounded-xl border border-orange-200 hover:bg-orange-100 hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1">
                <div className="text-3xl font-bold text-orange-600 mb-2">{overallMetrics.high_issues || 0}</div>
                <p className="text-sm text-orange-700 font-medium">High Priority</p>
                <p className="text-xs text-orange-600 mt-1">Medium Priority</p>
            </div>
              <div className="text-center p-6 bg-yellow-50 rounded-xl border border-yellow-200 hover:bg-yellow-100 hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1">
                <div className="text-3xl font-bold text-yellow-600 mb-2">{overallMetrics.medium_issues || 0}</div>
                <p className="text-sm text-yellow-700 font-medium">Medium Priority</p>
                <p className="text-xs text-yellow-600 mt-1">Low Priority</p>
            </div>
              <div className="text-center p-6 bg-blue-50 rounded-xl border border-blue-200 hover:bg-blue-100 hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1">
                <div className="text-3xl font-bold text-blue-600 mb-2">{overallMetrics.total_recommendations || 0}</div>
                <p className="text-sm text-blue-700 font-medium">Recommendations</p>
                <p className="text-xs text-blue-600 mt-1">Action Items</p>
            </div>
          </div>
          
            {/* Business Impact Section with Enhanced Design */}
            {currentSummary.business_impact && (
              <div className="mt-6 p-6 bg-gradient-to-r from-yellow-50 to-amber-50 border border-yellow-200 rounded-xl hover:shadow-lg transition-shadow duration-300">
                <h3 className="font-semibold text-yellow-800 mb-3 flex items-center">
                  <TrendingUp className="w-5 h-5 mr-2" />
                  Business Impact
                </h3>
                <p className="text-yellow-700 leading-relaxed">{currentSummary.business_impact}</p>
            </div>
          )}
          </div>
        </div>

        {/* Enhanced Category Scores with Interactive Elements */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {(() => {
            if (categoryScores && Object.keys(categoryScores).length > 0) {
              return Object.entries(categoryScores).map(([category, data], index) => {
                const Icon = getCategoryIcon(category);
                const colors = getCategoryColors(category);
            
            return (
                  <div key={category} className="group animate-slide-up-delay" style={{ animationDelay: `${index * 0.1}s` }}>
              <ScoreCard
                title={category.charAt(0).toUpperCase() + category.slice(1)}
                score={data.score}
                grade={data.grade}
                icon={Icon}
                color={colors.color}
                bgColor={colors.bg}
              />
                    {/* Hover Info Panel */}
                    <div className="mt-3 p-4 bg-white rounded-lg border border-gray-200 shadow-sm opacity-0 group-hover:opacity-100 transition-all duration-300 transform translate-y-2 group-hover:translate-y-0">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-gray-700">Issues</span>
                        <span className="text-sm text-gray-500">{data.issues?.length || 0}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-gray-700">Recommendations</span>
                        <span className="text-sm text-gray-500">{data.recommendations?.length || 0}</span>
                      </div>
                    </div>
                  </div>
                );
              });
            } else if (Object.keys(currentResults).length > 0) {
              return Object.entries(currentResults).map(([category, data], index) => {
                const Icon = getCategoryIcon(category);
                const colors = getCategoryColors(category);
                const score = data?.score || 0;
                const grade = score >= 90 ? 'A' : score >= 80 ? 'B' : score >= 70 ? 'C' : score >= 60 ? 'D' : 'F';
                
                return (
                  <div key={category} className="group animate-slide-up-delay" style={{ animationDelay: `${index * 0.1}s` }}>
                    <ScoreCard
                      title={category.charAt(0).toUpperCase() + category.slice(1)}
                      score={score}
                      grade={grade}
                      icon={Icon}
                      color={colors.color}
                      bgColor={colors.bg}
                    />
                    {/* Hover Info Panel */}
                    <div className="mt-3 p-4 bg-white rounded-lg border border-gray-200 shadow-sm opacity-0 group-hover:opacity-100 transition-all duration-300 transform translate-y-2 group-hover:translate-y-0">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-gray-700">Status</span>
                        <span className={`text-sm px-2 py-1 rounded-full ${
                          data.error ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'
                        }`}>
                          {data.error ? 'Error' : 'Complete'}
                        </span>
                      </div>
                      {data.error && (
                        <p className="text-xs text-red-600 mt-1">{data.error}</p>
                      )}
                    </div>
                  </div>
                );
              });
            } else {
              return (
                <div className="col-span-full text-center py-12 animate-bounce-in">
                  <div className="bg-white rounded-xl p-8 border-2 border-dashed border-gray-300">
                    <Search className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No Audit Data Available</h3>
                    <p className="text-gray-500 mb-4">Start an audit to see detailed results and insights</p>
                    <Link to="/audit" className="btn btn-primary">
                      Start New Audit
                    </Link>
                  </div>
                </div>
              );
            }
          })()}
        </div>



        {/* Enhanced Tabs Navigation with Better Visual Feedback */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 mb-8 overflow-hidden">
          <nav className="flex space-x-0">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              
              return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                  className={`flex-1 flex items-center justify-center space-x-3 py-4 px-6 font-medium text-sm transition-all duration-200 ${
                    isActive
                      ? 'bg-primary-50 text-primary-700 border-b-2 border-primary-500'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                  }`}
                >
                  <Icon className={`w-5 h-5 ${isActive ? 'text-primary-600' : 'text-gray-400'}`} />
                <span>{tab.label}</span>
                  {isActive && (
                    <div className="w-2 h-2 bg-primary-500 rounded-full animate-pulse"></div>
                  )}
              </button>
              );
            })}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="space-y-8">
          {activeTab === 'overview' && (
            <>
              {/* Enhanced Charts Section */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
                {Object.keys(categoryScores).length > 0 ? (
                  <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                      <TrendingUp className="w-5 h-5 mr-2 text-primary-600" />
                      Performance Overview
                    </h3>
                    <MetricsChart data={categoryScores} />
                  </div>
                ) : Object.keys(currentResults).length > 0 ? (
                  // Enhanced Fallback: Create chart data from raw results
                  (() => {
                    const fallbackChartData = {};
                    Object.entries(currentResults).forEach(([category, data]) => {
                      if (data && !data.error) {
                        const score = data.score || 0;
                        const grade = score >= 90 ? 'A' : score >= 80 ? 'B' : score >= 70 ? 'C' : score >= 60 ? 'D' : 'F';
                        fallbackChartData[category] = { score, grade };
                      }
                    });
                    return Object.keys(fallbackChartData).length > 0 ? (
                      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                          <TrendingUp className="w-5 h-5 mr-2 text-primary-600" />
                          Performance Overview
                        </h3>
                        <MetricsChart data={fallbackChartData} />
                      </div>
                    ) : (
                      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 flex items-center justify-center">
                        <div className="text-center text-gray-500">
                          <Search className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                          <p>No audit data available</p>
                          <p className="text-sm">Start an audit to see results</p>
                        </div>
                      </div>
                    );
                  })()
                ) : (
                  <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 flex items-center justify-center">
                    <div className="text-center text-gray-500">
                      <Search className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                      <p>No audit data available</p>
                      <p className="text-sm">Start an audit to see results</p>
                    </div>
                  </div>
                )}
                
                {/* Webpage Screenshot Section */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                    <Eye className="w-5 h-5 mr-2 text-blue-600" />
                    Webpage Screenshot
                  </h3>
                  <p className="text-gray-600 mb-6">
                    Visual proof of the webpage at the time of audit. This screenshot serves as evidence of the current state of the website.
                  </p>
                  
                  {(() => {
                    const screenshot = report?.screenshot || auditData?.screenshot;
                    console.log('Screenshot data:', { 
                      reportScreenshot: report?.screenshot, 
                      auditDataScreenshot: auditData?.screenshot,
                      finalScreenshot: screenshot 
                    });
                    return screenshot ? (
                      <ScreenshotViewer 
                        screenshot={screenshot} 
                        url={report?.url || 'Current Audit'} 
                      />
                    ) : (
                    <div className="text-center py-12 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
                      <Eye className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                      <h4 className="text-lg font-medium text-gray-900 mb-2">Screenshot Not Available</h4>
                      <p className="text-gray-500 mb-4">
                        No screenshot was captured during this audit. Screenshots are automatically captured during audits.
                      </p>
                      <div className="text-sm text-gray-400">
                        <p>• Screenshots provide visual proof of website state</p>
                        <p>• They help verify audit findings and recommendations</p>
                        <p>• Screenshots are captured using Selenium for accurate webpage representation</p>
                      </div>
                    </div>
                  );
                  })()}
                </div>
              </div>

              {/* Enhanced Timeline Section */}
              {currentSummary.timeline && (
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-8">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                    <Clock className="w-5 h-5 mr-2 text-blue-600" />
                    Recommended Timeline
                  </h3>
                  <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                    <p className="text-blue-700 leading-relaxed">{currentSummary.timeline}</p>
                  </div>
                </div>
              )}
            </>
          )}



          {activeTab === 'issues' && (
            <div className="space-y-6">
              {/* Enhanced Issues Overview */}
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-6 flex items-center">
                  <AlertTriangle className="w-5 h-5 mr-2 text-red-600" />
                  Issues & Problems Found
                </h3>
                
                {/* Helpful guidance for users */}
                <div className="mb-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0">
                      <svg className="w-5 h-5 text-blue-400 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div>
                      <h4 className="text-sm font-medium text-blue-800">Understanding Issues</h4>
                      <p className="text-sm text-blue-700 mt-1">
                        Issues are problems found during the audit that need attention. Each issue includes:
                      </p>
                      <ul className="text-xs text-blue-600 mt-2 space-y-1">
                        <li>• <strong>Priority:</strong> Critical (immediate), High (soon), Medium (plan)</li>
                        <li>• <strong>Impact:</strong> How much this affects your website's performance</li>
                        <li>• <strong>Suggested Fix:</strong> Specific steps to resolve the issue</li>
                      </ul>
                    </div>
                  </div>
                </div>
                
                {/* Issues Summary Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                  <div className="p-4 bg-red-50 rounded-lg border border-red-200 text-center">
                    <div className="text-2xl font-bold text-red-600 mb-1">{overallMetrics.critical_issues || 0}</div>
                    <div className="text-sm text-red-700 font-medium">Critical Issues</div>
                    <div className="text-xs text-red-600 mt-1">Immediate Action Required</div>
                  </div>
                  <div className="p-4 bg-orange-50 rounded-lg border border-orange-200 text-center">
                    <div className="text-2xl font-bold text-orange-600 mb-1">{overallMetrics.high_issues || 0}</div>
                    <div className="text-sm text-orange-700 font-medium">High Priority</div>
                    <div className="text-xs text-orange-600 mt-1">Address Soon</div>
                  </div>
                  <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-200 text-center">
                    <div className="text-2xl font-bold text-yellow-600 mb-1">{overallMetrics.medium_issues || 0}</div>
                    <div className="text-sm text-yellow-700 font-medium">Medium Priority</div>
                    <div className="text-xs text-yellow-600 mt-1">Monitor & Plan</div>
                  </div>
                </div>
                
                {/* Summary message */}
                <div className="mb-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-700">
                        <strong>Total Issues Found:</strong> {allIssues.length} 
                        {allIssues.length > 0 && (
                          <span className="ml-2">
                            ({overallMetrics.critical_issues || 0} critical, {overallMetrics.high_issues || 0} high, {overallMetrics.medium_issues || 0} medium)
                          </span>
                        )}
                      </p>
                      {allIssues.length === 0 && (
                        <p className="text-sm text-gray-600 mt-1">
                          Great news! No issues were detected during this audit.
                        </p>
                      )}
                    </div>
                    <div className="flex items-center space-x-3">
                      {allIssues.length > 0 && (
                        <div className="text-right">
                          <p className="text-xs text-gray-500">Priority: Critical &gt; High &gt; Medium</p>
                          <p className="text-xs text-gray-500">Start with critical issues first</p>
                        </div>
                      )}
                      {allIssues.length > 0 && (
                        <button
                          onClick={() => {
                            const issuesText = allIssues.map((issue, index) => 
                              `${index + 1}. ${issue.title}\n   Priority: ${issue.priority}\n   Impact: ${issue.impact}\n   Description: ${issue.description}\n   Suggestion: ${issue.suggestion}\n`
                            ).join('\n');
                            
                            const fullReport = `Issues Report\nGenerated: ${new Date().toLocaleString()}\nTotal Issues: ${allIssues.length}\n\n${issuesText}`;
                            
                            const blob = new Blob([fullReport], { type: 'text/plain' });
                            const url = URL.createObjectURL(blob);
                            const a = document.createElement('a');
                            a.href = url;
                            a.download = `issues-report-${new Date().toISOString().split('T')[0]}.txt`;
                            document.body.appendChild(a);
                            a.click();
                            document.body.removeChild(a);
                            URL.revokeObjectURL(url);
                          }}
                          className="px-3 py-1 text-xs bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors"
                        >
                          Export Issues
                        </button>
                      )}
                    </div>
                  </div>
                </div>
                
                {/* Issues List */}
                {allIssues && allIssues.length > 0 ? (
                  <div className="space-y-4">
                    {allIssues.map((issue, index) => (
                      <div key={index} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex items-center space-x-3">
                            <div className={`w-3 h-3 rounded-full ${
                              issue.priority === 'critical' ? 'bg-red-500' :
                              issue.priority === 'high' ? 'bg-orange-500' :
                              issue.priority === 'medium' ? 'bg-yellow-500' : 'bg-gray-500'
                            }`}></div>
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                              issue.priority === 'critical' ? 'bg-red-100 text-red-700' :
                              issue.priority === 'high' ? 'bg-orange-100 text-orange-700' :
                              issue.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' : 'bg-gray-100 text-gray-700'
                            }`}>
                              {issue.priority?.toUpperCase() || 'UNKNOWN'}
                            </span>
                          </div>
                          <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                            {issue.category || 'General'}
                          </span>
                        </div>
                        
                        <h4 className="font-medium text-gray-900 mb-2">{issue.title || `Issue ${index + 1}`}</h4>
                        <p className="text-gray-700 text-sm leading-relaxed mb-3">
                          {issue.description || issue.message || 'No description available.'}
                        </p>
                        
                        {issue.impact && (
                          <div className="bg-gray-50 rounded p-3 mb-3">
                            <div className="text-xs font-medium text-gray-600 mb-1">Impact:</div>
                            <p className="text-sm text-gray-700">{issue.impact}</p>
                          </div>
                        )}
                        
                        {issue.suggestion && (
                          <div className="bg-blue-50 rounded p-3 border border-blue-200">
                            <div className="text-xs font-medium text-blue-700 mb-1">Suggested Fix:</div>
                            <p className="text-sm text-blue-700">{issue.suggestion}</p>
                          </div>
                        )}
                        
                        {/* Action buttons */}
                        <div className="mt-4 flex space-x-2">
                          <button 
                            className="px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                            onClick={() => {
                              // Copy issue details to clipboard
                              const issueText = `Issue: ${issue.title}\nDescription: ${issue.description}\nSuggestion: ${issue.suggestion}`;
                              navigator.clipboard.writeText(issueText);
                              alert('Issue details copied to clipboard!');
                            }}
                          >
                            Copy Details
                          </button>
                          <button 
                            className="px-3 py-1 text-xs bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
                            onClick={() => {
                              // Mark as resolved (you can implement this functionality)
                              alert('Mark as resolved functionality can be implemented here');
                            }}
                          >
                            Mark Resolved
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <CheckCircle className="w-16 h-16 text-green-300 mx-auto mb-4" />
                    <h4 className="text-lg font-medium text-gray-900 mb-2">No Issues Found!</h4>
                    <p className="text-gray-500">Your website is performing well with no critical issues detected.</p>
                    <p className="text-sm text-gray-400 mt-1">Keep up the good work!</p>
                    
                    {/* Next steps guidance */}
                    <div className="mt-4 p-4 bg-green-50 rounded-lg border border-green-200 max-w-2xl mx-auto">
                      <h5 className="font-medium text-green-800 mb-2">What's Next?</h5>
                      <div className="text-sm text-green-700 space-y-2">
                        <p>• <strong>Check Recommendations:</strong> Even with no issues, there might be optimization opportunities</p>
                        <p>• <strong>Monitor Performance:</strong> Run regular audits to maintain your website's health</p>
                        <p>• <strong>Review Details:</strong> Check the Detailed Results tab for comprehensive insights</p>
                      </div>
                    </div>
                    
                    {/* Debug information */}
                    <div className="mt-6 p-4 bg-gray-50 rounded-lg border border-gray-200 text-left max-w-2xl mx-auto">
                      <h5 className="font-medium text-gray-700 mb-2">Debug Information:</h5>
                      <div className="text-xs text-gray-600 space-y-1">
                        <p>• Audit Results: {Object.keys(currentResults).length} categories</p>
                        <p>• Categories: {Object.keys(currentResults).join(', ') || 'None'}</p>
                        <p>• Current Results Structure: {JSON.stringify(currentResults, null, 2).substring(0, 200)}...</p>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'recommendations' && (
            <div className="space-y-6">
              {/* Enhanced Recommendations Overview */}
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-6 flex items-center">
                  <Lightbulb className="w-5 h-5 mr-2 text-yellow-600" />
                  Actionable Recommendations
                </h3>
                
                {/* Helpful guidance for users */}
                <div className="mb-6 p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0">
                      <svg className="w-5 h-5 text-yellow-400 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div>
                      <h4 className="text-sm font-medium text-yellow-800">Understanding Recommendations</h4>
                      <p className="text-sm text-yellow-700 mt-1">
                        Recommendations are optimization opportunities to improve your website. They're organized by:
                      </p>
                      <ul className="text-xs text-yellow-600 mt-2 space-y-1">
                        <li>• <strong>Quick Wins:</strong> Easy fixes that provide immediate benefits</li>
                        <li>• <strong>Short Term:</strong> Medium effort improvements for the next 1-2 weeks</li>
                        <li>• <strong>Long Term:</strong> Strategic improvements that require planning and resources</li>
                      </ul>
                      
                      {/* Technical Terms Glossary */}
                      <details className="mt-3">
                        <summary className="text-xs text-yellow-700 cursor-pointer hover:text-yellow-800 font-medium">
                          📚 View Technical Terms Glossary
                        </summary>
                        <div className="mt-2 p-3 bg-white rounded border border-yellow-200">
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs">
                            <div>
                              <strong className="text-yellow-800">Performance Terms:</strong>
                              <ul className="text-yellow-700 mt-1 space-y-1">
                                <li>• <strong>LCP:</strong> How fast your main content loads</li>
                                <li>• <strong>FID:</strong> How quickly your site responds to clicks</li>
                                <li>• <strong>CLS:</strong> How stable your page layout is</li>
                                <li>• <strong>CDN:</strong> Network that makes your site load faster</li>
                              </ul>
                            </div>
                            <div>
                              <strong className="text-yellow-800">SEO Terms:</strong>
                              <ul className="text-yellow-700 mt-1 space-y-1">
                                <li>• <strong>Meta tags:</strong> Page description tags for search engines</li>
                                <li>• <strong>Schema markup:</strong> Structured data for rich search results</li>
                                <li>• <strong>Sitemap:</strong> List of all your website pages</li>
                                <li>• <strong>Canonical URL:</strong> Preferred version of a page</li>
                              </ul>
                            </div>
                          </div>
                        </div>
                      </details>
                    </div>
                  </div>
                </div>
                
                {/* Recommendations Summary */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
                  <div className="p-4 bg-green-50 rounded-lg border border-green-200 text-center">
                    <div className="text-2xl font-bold text-green-600 mb-1">{overallMetrics.total_recommendations || 0}</div>
                    <div className="text-sm text-green-700 font-medium">Total Recommendations</div>
                  </div>
                  <div className="p-4 bg-blue-50 rounded-lg border border-blue-200 text-center">
                    <div className="text-2xl font-bold text-blue-600 mb-1">{allRecommendations?.quick_wins?.length || 0}</div>
                    <div className="text-sm text-blue-700 font-medium">Quick Wins</div>
                    <div className="text-xs text-blue-600 mt-1">Easy to implement</div>
                  </div>
                  <div className="p-4 bg-orange-50 rounded-lg border border-orange-200 text-center">
                    <div className="text-2xl font-bold text-orange-600 mb-1">{allRecommendations?.short_term?.length || 0}</div>
                    <div className="text-sm text-orange-700 font-medium">Short Term</div>
                    <div className="text-xs text-orange-600 mt-1">1-2 weeks</div>
                  </div>
                  <div className="p-4 bg-purple-50 rounded-lg border border-purple-200 text-center">
                    <div className="text-2xl font-bold text-purple-600 mb-1">{allRecommendations?.long_term?.length || 0}</div>
                    <div className="text-sm text-purple-700 font-medium">Long Term</div>
                    <div className="text-xs text-purple-600 mt-1">1+ months</div>
                  </div>
                </div>
                
                {/* Recommendations by Category */}
                {allRecommendations && Object.keys(allRecommendations).length > 0 ? (
                  <div className="space-y-6">
                    {/* Quick Wins */}
                    {allRecommendations.quick_wins && allRecommendations.quick_wins.length > 0 && (
                      <div className="border border-green-200 rounded-lg p-6 bg-green-50">
                        <h4 className="text-lg font-semibold text-green-800 mb-4 flex items-center">
                          <Zap className="w-5 h-5 mr-2" />
                          Quick Wins - Easy Improvements
                        </h4>
                        <div className="space-y-4">
                          {allRecommendations.quick_wins.map((rec, index) => (
                            <div key={index} className="bg-white rounded-lg p-4 border border-green-200 hover:shadow-md transition-shadow">
                              <div className="flex items-start justify-between mb-3">
                                <h5 className="font-medium text-green-900">{rec.title || `Quick Win ${index + 1}`}</h5>
                                <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full font-medium">
                                  Quick Win
                                </span>
                              </div>
                              <p className="text-gray-700 text-sm leading-relaxed mb-3">
                                {rec.description || 'No description available.'}
                              </p>
                              <div className="flex items-center justify-between text-xs text-gray-500 mb-3">
                                <span>Impact: {rec.impact || 'Medium'}</span>
                                <span>Effort: {rec.effort || 'Low'}</span>
                              </div>
                              
                              {/* Action buttons */}
                              <div className="flex space-x-2">
                                <button 
                                  className="px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                                  onClick={() => {
                                    const recText = `Recommendation: ${rec.title}\nDescription: ${rec.description}\nImpact: ${rec.impact}\nEffort: ${rec.effort}`;
                                    navigator.clipboard.writeText(recText);
                                    alert('Recommendation details copied to clipboard!');
                                  }}
                                >
                                  Copy Details
                                </button>
                                <button 
                                  className="px-3 py-1 text-xs bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
                                  onClick={() => {
                                    alert('Implementation guide functionality can be added here');
                                  }}
                                >
                                  Implementation Guide
                                </button>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {/* Short Term */}
                    {allRecommendations.short_term && allRecommendations.short_term.length > 0 && (
                      <div className="border border-orange-200 rounded-lg p-6 bg-orange-50">
                        <h4 className="text-lg font-semibold text-orange-800 mb-4 flex items-center">
                          <Clock className="w-5 h-5 mr-2" />
                          Short Term - 1-2 Weeks
                        </h4>
                        <div className="space-y-4">
                          {allRecommendations.short_term.map((rec, index) => (
                            <div key={index} className="bg-white rounded-lg p-4 border border-orange-200 hover:shadow-md transition-shadow">
                              <div className="flex items-start justify-between mb-3">
                                <h5 className="font-medium text-orange-900">{rec.title || `Short Term ${index + 1}`}</h5>
                                <span className="px-2 py-1 bg-orange-100 text-orange-700 text-xs rounded-full font-medium">
                                  Short Term
                                </span>
                              </div>
                              <p className="text-gray-700 text-sm leading-relaxed mb-3">
                                {rec.description || 'No description available.'}
                              </p>
                              <div className="flex items-center justify-between text-xs text-gray-500 mb-3">
                                <span>Impact: {rec.impact || 'Medium'}</span>
                                <span>Effort: {rec.effort || 'Medium'}</span>
                              </div>
                              
                              {/* Action buttons */}
                              <div className="flex space-x-2">
                                <button 
                                  className="px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                                  onClick={() => {
                                    const recText = `Recommendation: ${rec.title}\nDescription: ${rec.description}\nImpact: ${rec.impact}\nEffort: ${rec.effort}`;
                                    navigator.clipboard.writeText(recText);
                                    alert('Recommendation details copied to clipboard!');
                                  }}
                                >
                                  Copy Details
                                </button>
                                <button 
                                  className="px-3 py-1 text-xs bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
                                  onClick={() => {
                                    alert('Implementation guide functionality can be added here');
                                  }}
                                >
                                  Implementation Guide
                                </button>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {/* Long Term */}
                    {allRecommendations.long_term && allRecommendations.long_term.length > 0 && (
                      <div className="border border-purple-200 rounded-lg p-6 bg-purple-50">
                        <h4 className="text-lg font-semibold text-purple-800 mb-4 flex items-center">
                          <Target className="w-5 h-5 mr-2" />
                          Long Term - Strategic Improvements
                        </h4>
                        <div className="space-y-4">
                          {allRecommendations.long_term.map((rec, index) => (
                            <div key={index} className="bg-white rounded-lg p-4 border border-purple-200 hover:shadow-md transition-shadow">
                              <div className="flex items-start justify-between mb-3">
                                <h5 className="font-medium text-purple-900">{rec.title || `Long Term ${index + 1}`}</h5>
                                <span className="px-2 py-1 bg-purple-100 text-purple-700 text-xs rounded-full font-medium">
                                  Long Term
                                </span>
                              </div>
                              <p className="text-gray-700 text-sm leading-relaxed mb-3">
                                {rec.description || 'No description available.'}
                              </p>
                              <div className="flex items-center justify-between text-xs text-gray-500 mb-3">
                                <span>Impact: {rec.impact || 'High'}</span>
                                <span>Effort: {rec.effort || 'High'}</span>
                              </div>
                              
                              {/* Action buttons */}
                              <div className="flex space-x-2">
                                <button 
                                  className="px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                                  onClick={() => {
                                    const recText = `Recommendation: ${rec.title}\nDescription: ${rec.description}\nImpact: ${rec.impact}\nEffort: ${rec.effort}`;
                                    navigator.clipboard.writeText(recText);
                                    alert('Recommendation details copied to clipboard!');
                                  }}
                                >
                                  Copy Details
                                </button>
                                <button 
                                  className="px-3 py-1 text-xs bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
                                  onClick={() => {
                                    alert('Implementation guide functionality can be added here');
                                  }}
                                >
                                  Implementation Guide
                                </button>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <Lightbulb className="w-16 h-16 text-yellow-300 mx-auto mb-4" />
                    <h4 className="text-lg font-medium text-gray-900 mb-2">No Recommendations Available</h4>
                    <p className="text-gray-500">Your website is already optimized! No specific recommendations at this time.</p>
                    <p className="text-sm text-gray-400 mt-1">Consider running a new audit to check for updates.</p>
                    
                    {/* Next steps guidance */}
                    <div className="mt-4 p-4 bg-yellow-50 rounded-lg border border-yellow-200 max-w-2xl mx-auto">
                      <h5 className="font-medium text-yellow-800 mb-2">What's Next?</h5>
                      <div className="text-sm text-yellow-700 space-y-2">
                        <p>• <strong>Check Issues:</strong> Review any issues found during the audit</p>
                        <p>• <strong>Monitor Performance:</strong> Run regular audits to maintain optimization</p>
                        <p>• <strong>Review Details:</strong> Check the Detailed Results tab for comprehensive insights</p>
                      </div>
                    </div>
                  </div>
                )}
                
                {/* Export Recommendations Button */}
                {allRecommendations && Object.keys(allRecommendations).length > 0 && (
                  <div className="mt-6 text-center">
                    <button
                      onClick={() => {
                        const recsText = Object.entries(allRecommendations).map(([timeline, recs]) => {
                          if (recs.length === 0) return '';
                          return `${timeline.replace('_', ' ').toUpperCase()}:\n${recs.map((rec, index) => 
                            `${index + 1}. ${rec.title}\n   Description: ${rec.description}\n   Impact: ${rec.impact}\n   Effort: ${rec.effort}\n`
                          ).join('\n')}`;
                        }).filter(Boolean).join('\n\n');
                        
                        const fullReport = `Recommendations Report\nGenerated: ${new Date().toLocaleString()}\n\n${recsText}`;
                        
                        const blob = new Blob([fullReport], { type: 'text/plain' });
                        const url = URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = `recommendations-report-${new Date().toISOString().split('T')[0]}.txt`;
                        document.body.appendChild(a);
                        a.click();
                        document.body.removeChild(a);
                        URL.revokeObjectURL(url);
                      }}
                      className="px-6 py-3 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors font-medium"
                    >
                      <Download className="w-4 h-4 mr-2 inline" />
                      Export All Recommendations
                    </button>
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === 'details' && (
            <div className="space-y-8">
              {/* Enhanced Detailed Results Content */}
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-6 flex items-center">
                  <Search className="w-5 h-5 mr-2 text-primary-600" />
                  Detailed Analysis Results
                </h3>
                
                {/* Helpful guidance for users */}
                <div className="mb-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
                  <div className="flex items-start space-x-3">
                    <div className="flex-shrink-0">
                      <svg className="w-5 h-5 text-blue-400 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div>
                      <h4 className="text-sm font-medium text-blue-800">Understanding Detailed Results</h4>
                      <p className="text-sm text-blue-700 mt-1">
                        This section provides comprehensive analysis for each audit category. Each category shows:
                      </p>
                      <ul className="text-xs text-blue-600 mt-2 space-y-1">
                        <li>• <strong>Overall Score:</strong> Performance rating from 0-100 with letter grade</li>
                        <li>• <strong>Issues Found:</strong> Problems that need immediate attention</li>
                        <li>• <strong>Recommendations:</strong> Specific actions to improve performance</li>
                        <li>• <strong>Technical Details:</strong> In-depth analysis data for developers</li>
                      </ul>
                    </div>
                  </div>
                </div>
                {/* Summary of all categories */}
                <div className="mb-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-gray-700">
                        <strong>Audit Categories:</strong> {Object.keys(currentResults).length} categories analyzed
                      </p>
                      <p className="text-sm text-gray-600 mt-1">
                        {Object.keys(currentResults).map(cat => cat.charAt(0).toUpperCase() + cat.slice(1)).join(', ')}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-xs text-gray-500">Click on any category to see detailed analysis</p>
                      <p className="text-xs text-gray-500">Use export buttons to save data for reference</p>
                    </div>
                  </div>
                </div>
                
                <div className="space-y-6">
                  {Object.entries(currentResults).map(([category, data]) => (
                    <div key={category} className="border border-gray-200 rounded-xl p-6 hover:shadow-md transition-shadow">
                      <div className="flex items-center justify-between mb-4">
                        <h4 className="text-lg font-semibold text-gray-900 capitalize flex items-center">
                          {getCategoryIcon(category) && React.createElement(getCategoryIcon(category), { 
                            className: `w-5 h-5 mr-2 ${getCategoryColors(category).color}` 
                          })}
                          {category}
                        </h4>
                        {data && !data.error && (
                          <div className="flex items-center space-x-3">
                            <span className="text-sm font-medium text-gray-600">Score:</span>
                            <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getGradeColor(data.grade || 'F')}`}>
                              {data.score || 0}/100 ({data.grade || 'F'})
                            </span>
                          </div>
                        )}
                      </div>
                      
                      {data && !data.error ? (
                        <div className="space-y-4">
                          {/* Score Breakdown */}
                          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div className="p-4 bg-gray-50 rounded-lg">
                              <div className="text-2xl font-bold text-gray-900">{data.score || 0}</div>
                              <div className="text-sm text-gray-600">Overall Score</div>
                              <div className="text-xs text-gray-500 mt-1">
                                {data.score >= 90 ? 'Excellent' : 
                                 data.score >= 80 ? 'Good' : 
                                 data.score >= 70 ? 'Fair' : 
                                 data.score >= 60 ? 'Poor' : 'Very Poor'}
                              </div>
                            </div>
                            <div className="p-4 bg-gray-50 rounded-lg">
                              <div className="text-2xl font-bold text-gray-900">{data.issues?.length || 0}</div>
                              <div className="text-sm text-gray-600">Issues Found</div>
                              <div className="text-xs text-gray-500 mt-1">
                                {data.issues?.length === 0 ? 'No issues' : 
                                 data.issues?.length === 1 ? '1 issue' : 
                                 `${data.issues.length} issues`}
                              </div>
                            </div>
                            <div className="p-4 bg-gray-50 rounded-lg">
                              <div className="text-2xl font-bold text-gray-900">{data.recommendations?.length || 0}</div>
                              <div className="text-sm text-gray-600">Recommendations</div>
                              <div className="text-xs text-gray-500 mt-1">
                                {data.recommendations?.length === 0 ? 'No recommendations' : 
                                 data.recommendations?.length === 1 ? '1 recommendation' : 
                                 `${data.recommendations.length} recommendations`}
                              </div>
                            </div>
                          </div>
                    
                          {/* Detailed Information */}
                          {data.details && (
                            <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                              <div className="flex items-center justify-between mb-3">
                                <h5 className="font-medium text-blue-900 flex items-center">
                                  <Search className="w-4 h-4 mr-2" />
                                  Technical Details
                                </h5>
                                <button
                                  onClick={() => {
                                    const detailsText = `Technical Details for ${category}:\n${JSON.stringify(data.details, null, 2)}`;
                                    navigator.clipboard.writeText(detailsText);
                                    alert('Technical details copied to clipboard!');
                                  }}
                                  className="px-2 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
                                >
                                  Copy
                                </button>
                              </div>
                              <div className="bg-white p-3 rounded border overflow-auto max-h-40">
                                <pre className="text-xs text-gray-700 whitespace-pre-wrap">
                                  {JSON.stringify(data.details, null, 2)}
                                </pre>
                              </div>
                              <p className="text-xs text-blue-600 mt-2">
                                💡 This data is useful for developers and technical teams implementing fixes
                              </p>
                            </div>
                          )}
                          
                          {/* Issues and Recommendations Summary */}
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {data.issues && data.issues.length > 0 && (
                              <div className="p-4 bg-red-50 rounded-lg border border-red-200">
                                <div className="flex items-center justify-between mb-2">
                                  <h6 className="font-medium text-red-800">Issues ({data.issues.length})</h6>
                                  <button
                                    onClick={() => {
                                      const issuesText = data.issues.map((issue, idx) => 
                                        `${idx + 1}. ${issue.message || issue.title || `Issue ${idx + 1}`}`
                                      ).join('\n');
                                      navigator.clipboard.writeText(issuesText);
                                      alert('Issues copied to clipboard!');
                                    }}
                                    className="px-2 py-1 text-xs bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
                                  >
                                    Copy All
                                  </button>
                                </div>
                                <div className="space-y-2">
                                  {data.issues.slice(0, 3).map((issue, idx) => (
                                    <div key={idx} className="text-sm text-red-700 bg-white p-2 rounded border">
                                      {issue.message || issue.title || `Issue ${idx + 1}`}
                                    </div>
                                  ))}
                                  {data.issues.length > 3 && (
                                    <p className="text-xs text-red-600">+{data.issues.length - 3} more issues</p>
                                  )}
                                </div>
                                <p className="text-xs text-red-600 mt-2">
                                  ⚠️ These issues need immediate attention to improve your score
                                </p>
                              </div>
                            )}
                            
                            {data.recommendations && data.recommendations.length > 0 && (
                              <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                                <div className="flex items-center justify-between mb-2">
                                  <h6 className="font-medium text-green-800">Recommendations ({data.recommendations.length})</h6>
                                  <button
                                    onClick={() => {
                                      const recsText = data.recommendations.map((rec, idx) => 
                                        `${idx + 1}. ${rec.title || rec.message || `Recommendation ${idx + 1}`}`
                                      ).join('\n');
                                      navigator.clipboard.writeText(recsText);
                                      alert('Recommendations copied to clipboard!');
                                    }}
                                    className="px-2 py-1 text-xs bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
                                  >
                                    Copy All
                                  </button>
                                </div>
                                <div className="space-y-2">
                                  {data.recommendations.slice(0, 3).map((rec, idx) => (
                                    <div key={idx} className="text-sm text-green-700 bg-white p-2 rounded border">
                                      {rec.title || rec.message || `Recommendation ${idx + 1}`}
                                    </div>
                                  ))}
                                  {data.recommendations.length > 3 && (
                                    <p className="text-xs text-green-600">+{data.recommendations.length - 3} more recommendations</p>
                                  )}
                                </div>
                                <p className="text-xs text-green-600 mt-2">
                                  💡 Implement these recommendations to boost your performance score
                                </p>
                              </div>
                            )}
                          </div>
                        </div>
                      ) : (
                        <div className="text-center py-8">
                          <AlertTriangle className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                          <p className="text-gray-500">No data available for this category</p>
                          {data?.error && (
                            <p className="text-sm text-red-500 mt-2">{data.error}</p>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
                
                {/* Export Detailed Results Button */}
                {Object.keys(currentResults).length > 0 && (
                  <div className="mt-8 text-center">
                    <button
                      onClick={() => {
                        const resultsText = Object.entries(currentResults).map(([category, data]) => {
                          if (!data || data.error) return `${category}: No data available`;
                          
                          let categoryText = `${category.toUpperCase()}:\n`;
                          categoryText += `Score: ${data.score || 0}/100 (${data.grade || 'F'})\n`;
                          categoryText += `Issues: ${data.issues?.length || 0}\n`;
                          categoryText += `Recommendations: ${data.recommendations?.length || 0}\n`;
                          
                          if (data.issues && data.issues.length > 0) {
                            categoryText += '\nIssues:\n';
                            data.issues.forEach((issue, idx) => {
                              categoryText += `${idx + 1}. ${issue.message || issue.title || `Issue ${idx + 1}`}\n`;
                            });
                          }
                          
                          if (data.recommendations && data.recommendations.length > 0) {
                            categoryText += '\nRecommendations:\n';
                            data.recommendations.forEach((rec, idx) => {
                              categoryText += `${idx + 1}. ${rec.title || rec.message || `Recommendation ${idx + 1}`}\n`;
                            });
                          }
                          
                          return categoryText;
                        }).join('\n\n');
                        
                        const fullReport = `Detailed Results Report\nGenerated: ${new Date().toLocaleString()}\n\n${resultsText}`;
                        
                        const blob = new Blob([fullReport], { type: 'text/plain' });
                        const url = URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = `detailed-results-report-${new Date().toISOString().split('T')[0]}.txt`;
                        document.body.appendChild(a);
                        a.click();
                        document.body.removeChild(a);
                        URL.revokeObjectURL(url);
                      }}
                      className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
                    >
                      <Download className="w-4 h-4 mr-2 inline" />
                      Export Detailed Results
                    </button>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
      
      {/* Quick Re-audit Section */}
      {report?.url && (
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-6 mb-8">
          <div className="text-center">
            <h3 className="text-lg font-semibold text-blue-900 mb-3 flex items-center justify-center">
              <RefreshCw className="w-5 h-5 mr-2" />
              Quick Re-audit
            </h3>
            <p className="text-blue-700 mb-4">
              Want to check if your website has improved? Re-audit the same URL to see progress.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center space-y-3 sm:space-y-0 sm:space-x-4">
              <div className="text-sm text-blue-600 bg-white px-3 py-2 rounded-lg border border-blue-200">
                <span className="font-medium">URL:</span> {report.url}
              </div>
              <button
                onClick={() => {
                  // Store the current URL and audit types for quick start
                  localStorage.setItem('last_audit_url', report.url);
                  if (report?.audit_types && Array.isArray(report.audit_types)) {
                    localStorage.setItem('last_audit_types', JSON.stringify(report.audit_types));
                  }
                  
                  // Navigate to audit page
                  window.location.href = '/audit';
                }}
                className="btn btn-primary px-6 py-3 hover:bg-blue-700 transition-colors"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Re-audit This URL
              </button>
            </div>
          </div>
        </div>
      )}
      
      {/* Enhanced Footer with Action Buttons */}
      <div className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex flex-col md:flex-row items-center justify-between space-y-4 md:space-y-0">
            <div className="text-center md:text-left">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Ready to Improve Your Website?</h3>
              <p className="text-gray-600">Get actionable insights and recommendations to optimize your site's performance.</p>
            </div>
            <div className="flex flex-col sm:flex-row space-y-3 sm:space-y-0 sm:space-x-3">
              <button 
                onClick={() => {
                  // Clear any existing audit data from context
                  if (window.auditContext && window.auditContext.resetAudit) {
                    window.auditContext.resetAudit();
                  }
                  
                  // Store the current URL for pre-filling the new audit
                  if (report?.url) {
                    localStorage.setItem('last_audit_url', report.url);
                    // Also store audit types if available
                    if (report?.audit_types && Array.isArray(report.audit_types)) {
                      localStorage.setItem('last_audit_types', JSON.stringify(report.audit_types));
                    }
                  }
                  
                  // Clear any existing audit progress
                  localStorage.removeItem('current_audit_progress');
                  localStorage.removeItem('current_audit_status');
                  
                  // Navigate to audit page
                  window.location.href = '/audit';
                }} 
                className="btn btn-primary px-6 py-3 hover:bg-primary-700 transition-colors flex items-center justify-center"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Run New Audit
              </button>
              <button 
                onClick={() => window.print()} 
                className="btn btn-outline px-6 py-3"
              >
                <Printer className="w-4 h-4 mr-2" />
                Print Report
              </button>
            </div>
          </div>
          
          {/* Report Metadata */}
          <div className="mt-8 pt-6 border-t border-gray-200">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-sm text-gray-500">
              <div>
                <span className="font-medium text-gray-700">Audit Engine Version:</span>
                <span className="ml-2">{report?.audit_engine_version || '2.0.0'}</span>
              </div>
              <div>
                <span className="font-medium text-gray-700">Data Sources:</span>
                <span className="ml-2">{currentSummary?.data_sources_used?.join(', ') || 'Lighthouse API, Local Analysis'}</span>
              </div>
              <div>
                <span className="font-medium text-gray-700">Report Generated:</span>
                <span className="ml-2">{report?.timestamp ? new Date(report.timestamp).toLocaleString() : 'Recently'}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReportPage;
