import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAudit } from '../contexts/AuditContext';
import RealTimeProgress from '../components/RealTimeProgress';
import { 
  Globe, 
  Search, 
  Shield, 
  Zap, 
  Eye, 
  CheckCircle,
  Loader2,
  AlertCircle,
  ArrowRight,
  RefreshCw
} from 'lucide-react';

const AuditPage = () => {
  const [url, setUrl] = useState('');
  const [auditTypes, setAuditTypes] = useState(['security', 'performance', 'seo', 'accessibility']);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  
  // Use the real-time audit context
  const { 
    startAudit, 
    isAuditRunning, 
    isAuditCompleted, 
    auditResults, 
    auditSummary,
    resetAudit,
    auditProgress,
    auditStatus,
    manuallyCompleteAudit
  } = useAudit();

  const auditOptions = [
    {
      id: 'security',
      name: 'Security Analysis',
      description: 'Vulnerability scanning, SSL/TLS check, security headers',
      icon: Shield,
      color: 'text-red-500',
      bgColor: 'bg-red-50',
      borderColor: 'border-red-200'
    },
    {
      id: 'performance',
      name: 'Performance Testing',
      description: 'Page speed, Core Web Vitals, resource optimization',
      icon: Zap,
      color: 'text-yellow-500',
      bgColor: 'bg-yellow-50',
      borderColor: 'border-yellow-200'
    },
    {
      id: 'seo',
      name: 'SEO Optimization',
      description: 'Meta tags, structured data, content analysis',
      icon: Search,
      color: 'text-blue-500',
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200'
    },
    {
      id: 'accessibility',
      name: 'Accessibility Check',
      description: 'WCAG compliance, screen reader compatibility',
      icon: Eye,
      color: 'text-green-500',
      bgColor: 'bg-green-50',
      borderColor: 'border-green-200'
    }
  ];

  const validateUrl = (url) => {
    try {
      const urlPattern = /^https?:\/\/.+/i;
      if (!urlPattern.test(url)) {
        // Add protocol if missing
        url = 'https://' + url.replace(/^(https?:\/\/)?/i, '');
      }
      new URL(url);
      return { isValid: true, url };
    } catch {
      return { isValid: false, url };
    }
  };

  const handleAuditTypeToggle = (type) => {
    setAuditTypes(prev => 
      prev.includes(type) 
        ? prev.filter(t => t !== type)
        : [...prev, type]
    );
  };

  // Auto-fill form with last audited data when page loads
  useEffect(() => {
    // Check if there's a last audited URL to pre-fill
    const lastAuditUrl = localStorage.getItem('last_audit_url');
    if (lastAuditUrl && !url) {
      setUrl(lastAuditUrl);
    }
    
    // Check if there are last audited types to pre-fill
    const lastAuditTypes = localStorage.getItem('last_audit_types');
    if (lastAuditTypes) {
      try {
        const parsedTypes = JSON.parse(lastAuditTypes);
        if (Array.isArray(parsedTypes) && parsedTypes.length > 0) {
          setAuditTypes(parsedTypes);
        }
      } catch (error) {
        console.log('Could not parse last audit types');
      }
    }
    
    // Clear the stored data after pre-filling
    localStorage.removeItem('last_audit_url');
    localStorage.removeItem('last_audit_types');
  }, [url]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!url.trim()) {
      setError('Please enter a website URL');
      return;
    }

    const { isValid, url: validatedUrl } = validateUrl(url.trim());
    if (!isValid) {
      setError('Please enter a valid website URL');
      return;
    }

    if (auditTypes.length === 0) {
      setError('Please select at least one audit type');
      return;
    }

    try {
      // Start the real-time audit
      await startAudit(validatedUrl, auditTypes);
      
      // Reset form
      setUrl('');
      setError('');
      

      
    } catch (err) {
      console.error('Audit error:', err);
      const errorMessage = err.message || 'Failed to start audit. Please try again.';
      setError(errorMessage);

    }
  };

  const handleViewResults = useCallback(() => {
    if (isAuditCompleted && Object.keys(auditResults).length > 0) {
      try {
        // Clean up old reports to free up space
        cleanupOldReports();
        
        // Check current storage usage
        const currentUsage = checkStorageSize();
        
        // Create a compressed version of the report data
        const reportId = Date.now().toString();
        
        // Extract only essential data for storage
        const compressedData = {
          url: url,
          timestamp: new Date().toISOString(),
          audit_types: auditTypes,
          // Store only essential results data
          results: Object.entries(auditResults).reduce((acc, [category, data]) => {
            if (data && !data.error) {
              acc[category] = {
                score: data.score || 0,
                grade: (data.score || 0) >= 90 ? 'A' : (data.score || 0) >= 80 ? 'B' : (data.score || 0) >= 70 ? 'C' : (data.score || 0) >= 60 ? 'D' : 'F',
                // Store only essential details
                details: {
                  core_web_vitals: data.details?.core_web_vitals || {},
                  data_sources: data.details?.data_sources || []
                },
                // Store only essential issues and recommendations
                issues: (data.issues || []).slice(0, 10), // Limit to first 10 issues
                recommendations: (data.recommendations || []).slice(0, 10) // Limit to first 10 recommendations
              };
            }
            return acc;
          }, {}),
          // Store only essential summary
          summary: {
            total_issues: auditSummary.total_issues || 0,
            critical_issues: auditSummary.critical_issues || 0,
            warnings: auditSummary.warnings || 0,
            recommendations: auditSummary.recommendations || 0
          }
        };
        
        // Check data size before storing
        const dataSize = JSON.stringify(compressedData).length;
        const maxSize = 5 * 1024 * 1024; // 5MB limit
        
        if (dataSize > maxSize) {
          // Store even more minimal version
          const minimalData = {
            url: url,
            timestamp: new Date().toISOString(),
            audit_types: auditTypes,
            results: Object.entries(auditResults).reduce((acc, [category, data]) => {
              if (data && !data.error) {
                acc[category] = {
                  score: data.score || 0,
                  grade: (data.score || 0) >= 90 ? 'A' : (data.score || 0) >= 80 ? 'B' : (data.score || 0) >= 70 ? 'C' : (data.score || 0) >= 60 ? 'D' : 'F',
                  issues: data.issues || [],
                  recommendations: data.recommendations || []
                };
              }
              return acc;
            }, {}),
            summary: {
              total_issues: auditSummary.total_issues || 0,
              critical_issues: auditSummary.critical_issues || 0,
              warnings: auditSummary.warnings || 0,
              recommendations: auditSummary.recommendations || 0
            }
          };
          
          localStorage.setItem(`report_${reportId}`, JSON.stringify(minimalData));
        } else {
          localStorage.setItem(`report_${reportId}`, JSON.stringify(compressedData));
        }
        
        // Navigate to report page
        navigate(`/report/${reportId}`);
        
      } catch (error) {
        // Fallback: store minimal data and navigate
        try {
          const reportId = Date.now().toString();
          const fallbackData = {
            url: url,
            timestamp: new Date().toISOString(),
            audit_types: auditTypes,
            results: Object.entries(auditResults).reduce((acc, [category, data]) => {
              if (data && !data.error) {
                acc[category] = {
                  score: data.score || 0,
                  grade: (data.score || 0) >= 90 ? 'A' : (data.score || 0) >= 80 ? 'B' : (data.score || 0) >= 70 ? 'C' : (data.score || 0) >= 60 ? 'D' : 'F',
                  issues: data.issues || [],
                  recommendations: data.recommendations || []
                };
              }
              return acc;
            }, {}),
            summary: {
              total_issues: auditSummary.total_issues || 0,
              critical_issues: auditSummary.critical_issues || 0,
              warnings: auditSummary.warnings || 0,
              recommendations: auditSummary.recommendations || 0
            }
          };
          
          localStorage.setItem(`report_${reportId}`, JSON.stringify(fallbackData));
          navigate(`/report/${reportId}`);
          
        } catch (fallbackError) {

        }
      }
    }
  }, [isAuditCompleted, auditResults, auditSummary, url, auditTypes, navigate]);

  // Auto-redirect to report when audit completes
  useEffect(() => {
    if (isAuditCompleted && Object.keys(auditResults).length > 0) {

      
      // Auto-redirect after a short delay to show completion message
      const timer = setTimeout(() => {
        handleViewResults();
      }, 1000); // Reduced delay for better user experience
      
      // Fallback redirect if the first one doesn't work
      const fallbackTimer = setTimeout(() => {
        if (window.location.pathname === '/audit') {
          // Still on audit page, force redirect
          handleViewResults();
        }
      }, 2000); // Reduced fallback delay
      
      return () => {
        clearTimeout(timer);
        clearTimeout(fallbackTimer);
      };
    }
  }, [isAuditCompleted, auditResults, auditSummary, handleViewResults]);

  const handleNewAudit = () => {
    resetAudit();
    setUrl('');
    setError('');
    setAuditTypes(['security', 'performance', 'seo', 'accessibility']);
  };

  // Clean up old reports to free up localStorage space
  const cleanupOldReports = () => {
    try {
      const keys = Object.keys(localStorage);
      const reportKeys = keys.filter(key => key.startsWith('report_'));
      
      if (reportKeys.length > 5) {
        // Keep only the 5 most recent reports
        const sortedKeys = reportKeys.sort((a, b) => {
          const aTime = parseInt(a.replace('report_', ''));
          const bTime = parseInt(b.replace('report_', ''));
          return bTime - aTime; // Most recent first
        });
        
        // Remove old reports
        sortedKeys.slice(5).forEach(key => {
          localStorage.removeItem(key);
          console.log('Removed old report:', key);
        });
      }
    } catch (error) {
      console.warn('Failed to cleanup old reports:', error);
    }
  };

  // Check localStorage size and provide feedback
  const checkStorageSize = () => {
    try {
      let totalSize = 0;
      const keys = Object.keys(localStorage);
      
      keys.forEach(key => {
        const value = localStorage.getItem(key);
        totalSize += new Blob([value]).size;
      });
      
      const sizeInMB = (totalSize / (1024 * 1024)).toFixed(2);
      console.log(`Current localStorage usage: ${sizeInMB}MB`);
      
      if (totalSize > 4 * 1024 * 1024) { // 4MB

        cleanupOldReports();
      }
      
      return totalSize;
    } catch (error) {
      console.warn('Failed to check storage size:', error);
      return 0;
    }
  };

  return (
    <div className="min-h-screen py-12 bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Website Audit Tool
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Enter your website URL and select the types of analysis you'd like to perform. 
            Our comprehensive audit will identify issues and provide actionable recommendations.
          </p>
        </div>

        {/* Audit Form */}
        <div className="card max-w-2xl mx-auto mb-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* URL Input */}
            <div>
              <label htmlFor="url" className="block text-sm font-medium text-gray-700 mb-2">
                Website URL
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Globe className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type="text"
                  id="url"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="https://example.com"
                  className="block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-lg"
                  disabled={isAuditRunning}
                />
              </div>
              <p className="mt-2 text-sm text-gray-500">
                Enter the full URL including https:// or http://
              </p>
              
              {/* Show when URL is pre-filled from previous audit */}
              {url && localStorage.getItem('last_audit_url') === url && (
                <div className="mt-2 p-2 bg-blue-50 border border-blue-200 rounded-lg">
                  <p className="text-sm text-blue-700 flex items-center">
                    <CheckCircle className="w-4 h-4 mr-2 text-blue-600" />
                    Pre-filled from your last audit. You can use "Quick Start Audit" below!
                  </p>
                </div>
              )}
            </div>

            {/* Error Message */}
            {error && (
              <div className="flex items-center space-x-2 p-3 bg-red-50 border border-red-200 rounded-lg">
                <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
                <span className="text-red-700">{error}</span>
              </div>
            )}

            {/* Audit Types */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-4">
                Select Audit Types
              </label>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {auditOptions.map((option) => (
                  <div
                    key={option.id}
                    className={`relative cursor-pointer ${
                      auditTypes.includes(option.id)
                        ? `${option.bgColor} ${option.borderColor} border-2`
                        : 'bg-white border-2 border-gray-200 hover:border-gray-300'
                    } rounded-lg p-4 transition-all duration-200`}
                    onClick={() => !isAuditRunning && handleAuditTypeToggle(option.id)}
                  >
                    <div className="flex items-start space-x-3">
                      <div className={`flex-shrink-0 ${
                        auditTypes.includes(option.id) ? option.bgColor : 'bg-gray-50'
                      } p-2 rounded-lg`}>
                        <option.icon className={`w-5 h-5 ${
                          auditTypes.includes(option.id) ? option.color : 'text-gray-400'
                        }`} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className={`text-sm font-medium ${
                          auditTypes.includes(option.id) ? 'text-gray-900' : 'text-gray-700'
                        }`}>
                          {option.name}
                        </h3>
                        <p className="text-xs text-gray-500 mt-1">
                          {option.description}
                        </p>
                      </div>
                      {auditTypes.includes(option.id) && (
                        <CheckCircle className={`w-5 h-5 ${option.color} flex-shrink-0`} />
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isAuditRunning || !url.trim() || auditTypes.length === 0}
              className="w-full btn btn-primary text-lg py-4 flex items-center justify-center space-x-2 group disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isAuditRunning ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Audit in Progress...</span>
                </>
              ) : (
                <>
                  <span>Start Comprehensive Audit</span>
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </>
              )}
            </button>
            
            {/* Quick Start Button - Only show if URL is pre-filled */}
            {url.trim() && auditTypes.length > 0 && !isAuditRunning && (
              <button
                type="button"
                onClick={async () => {
                  // Validate URL first
                  const validation = validateUrl(url);
                  if (!validation.isValid) {
                    setError('Please enter a new URL');
                    return;
                  }
                  
                  // Start audit immediately
                  try {
                    await startAudit(validation.url, auditTypes);

                  } catch (error) {
                    setError(error.message);
                  }
                }}
                className="w-full btn btn-secondary text-lg py-4 flex items-center justify-center space-x-2 group mt-3"
              >
                <Zap className="w-5 h-5 group-hover:scale-110 transition-transform" />
                <span>Quick Start Audit</span>
              </button>
            )}
            
            {/* Clear Form Button */}
            {url.trim() && (
              <button
                type="button"
                onClick={() => {
                  setUrl('');
                  setAuditTypes(['security', 'performance', 'seo', 'accessibility']);
                  setError('');
                  // Clear any stored audit data
                  localStorage.removeItem('last_audit_url');
                  localStorage.removeItem('last_audit_types');

                }}
                className="w-full btn btn-outline text-sm py-2 flex items-center justify-center space-x-2 group mt-2"
              >
                <RefreshCw className="w-4 h-4 group-hover:rotate-180 transition-transform" />
                <span>Clear Form & Start Fresh</span>
              </button>
            )}
          </form>
        </div>

        {/* Real-Time Progress Component */}
        {(isAuditRunning || isAuditCompleted) && (
          <RealTimeProgress />
        )}

        {/* Debug Info - Remove this later */}
        {process.env.NODE_ENV === 'development' && (
          <div className="card max-w-2xl mx-auto mb-4 p-4 bg-gray-50 border border-gray-200">
            <h4 className="text-sm font-medium text-gray-700 mb-2">Debug Info:</h4>
            <div className="text-xs text-gray-600 space-y-1">
              <div>Audit Status: {auditStatus}</div>
              <div>Progress: {auditProgress}%</div>
              <div>Is Running: {String(isAuditRunning)}</div>
              <div>Is Completed: {String(isAuditCompleted)}</div>
              <div>Results Count: {Object.keys(auditResults).length}</div>
              <div>Results Keys: {Object.keys(auditResults).join(', ')}</div>
            </div>
            {auditProgress === 100 && Object.keys(auditResults).length >= 4 && !isAuditCompleted && (
              <div className="mt-3 pt-3 border-t border-gray-200">
                <button
                  onClick={manuallyCompleteAudit}
                  className="btn btn-warning px-3 py-2 text-sm"
                >
                  🔧 Force Complete (Progress 100% + 4 Results)
                </button>
              </div>
            )}
          </div>
        )}

        {/* Audit Complete Display */}
        {isAuditCompleted && Object.keys(auditResults).length > 0 && (
          <div className="card max-w-2xl mx-auto text-center">
            <div className="py-6">
              <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Audit Complete! 🎉
              </h3>
              <p className="text-gray-600 mb-6">
                Your comprehensive website audit has been completed. Redirecting to detailed report...
              </p>
              
              <div className="flex space-x-4 justify-center">
                <button
                  onClick={handleNewAudit}
                  className="btn btn-secondary px-6 py-3"
                >
                  Start New Audit
                </button>
                <button
                  onClick={() => {
                    // Test auto-redirect functionality
                    if (Object.keys(auditResults).length > 0) {
                      handleViewResults();
                    } else {

                    }
                  }}
                  className="btn btn-outline px-6 py-3 text-sm"
                >
                  Test Redirect
                </button>
                      </div>
              
              <div className="mt-4 flex items-center justify-center space-x-2 text-blue-600">
                <div className="w-4 h-4 border-2 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
                <span className="text-sm font-medium">Redirecting to report...</span>
                    </div>
              
              <p className="text-sm text-gray-500 mt-4">
                You will be automatically redirected to the detailed report in a few seconds.
              </p>
              
              <div className="mt-2 text-xs text-gray-400">
                If you're not redirected automatically, you can start a new audit above.
              </div>
            </div>
          </div>
        )}

        {/* Info Section */}
        {!isAuditRunning && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">
                What We Check
              </h3>
              <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex items-center space-x-2">
                  <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
                  <span>Security vulnerabilities and SSL configuration</span>
                </li>
                <li className="flex items-center space-x-2">
                  <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
                  <span>Page speed and Core Web Vitals</span>
                </li>
                <li className="flex items-center space-x-2">
                  <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
                  <span>SEO optimization and meta tags</span>
                </li>
                <li className="flex items-center space-x-2">
                  <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
                  <span>Accessibility compliance (WCAG)</span>
                </li>
              </ul>
            </div>

            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">
                What You Get
              </h3>
              <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex items-center space-x-2">
                  <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
                  <span>Detailed analysis with scores for each category</span>
                </li>
                <li className="flex items-center space-x-2">
                  <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
                  <span>Prioritized list of issues to fix</span>
                </li>
                <li className="flex items-center space-x-2">
                  <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
                  <span>Step-by-step recommendations</span>
                </li>
                <li className="flex items-center space-x-2">
                  <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
                  <span>Resources and tools to implement fixes</span>
                </li>
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AuditPage;
