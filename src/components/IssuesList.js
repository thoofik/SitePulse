import React, { useState } from 'react';
import { AlertTriangle, XCircle, AlertCircle, Info, ChevronDown, ChevronRight } from 'lucide-react';

const IssuesList = ({ issues }) => {
  const [expandedSections, setExpandedSections] = useState({
    critical: true,
    high: true,
    medium: false,
    low: false
  });

  const toggleSection = (severity) => {
    setExpandedSections(prev => ({
      ...prev,
      [severity]: !prev[severity]
    }));
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'critical':
        return XCircle;
      case 'high':
        return AlertTriangle;
      case 'medium':
        return AlertCircle;
      case 'low':
        return Info;
      default:
        return Info;
    }
  };

  const getSeverityColor = (severity) => {
    const colors = {
      critical: {
        bg: 'bg-red-50',
        border: 'border-red-200',
        text: 'text-red-800',
        icon: 'text-red-500',
        badge: 'bg-red-100 text-red-800'
      },
      high: {
        bg: 'bg-orange-50',
        border: 'border-orange-200',
        text: 'text-orange-800',
        icon: 'text-orange-500',
        badge: 'bg-orange-100 text-orange-800'
      },
      medium: {
        bg: 'bg-yellow-50',
        border: 'border-yellow-200',
        text: 'text-yellow-800',
        icon: 'text-yellow-500',
        badge: 'bg-yellow-100 text-yellow-800'
      },
      low: {
        bg: 'bg-gray-50',
        border: 'border-gray-200',
        text: 'text-gray-800',
        icon: 'text-gray-500',
        badge: 'bg-gray-100 text-gray-800'
      }
    };
    return colors[severity] || colors.low;
  };

  const severityLabels = {
    critical: 'Critical Issues',
    high: 'High Priority Issues',
    medium: 'Medium Priority Issues',
    low: 'Low Priority Issues'
  };

  const severityDescriptions = {
    critical: 'These issues require immediate attention and could pose serious security risks or major functionality problems.',
    high: 'Important issues that should be addressed within 1-2 weeks to prevent potential problems.',
    medium: 'Issues that should be fixed to improve overall website quality and user experience.',
    low: 'Minor improvements that can be addressed over time to optimize your website further.'
  };

  if (!issues || Object.keys(issues).length === 0) {
    return (
      <div className="card text-center py-12">
        <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <Info className="w-8 h-8 text-green-600" />
        </div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">No Issues Found</h3>
        <p className="text-gray-600">Great! Your website doesn't have any major issues to address.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {Object.entries(issues).map(([severity, issueList]) => {
        if (!issueList || issueList.length === 0) return null;

        const colors = getSeverityColor(severity);
        const Icon = getSeverityIcon(severity);
        const isExpanded = expandedSections[severity];

        return (
          <div key={severity} className="card">
            <button
              onClick={() => toggleSection(severity)}
              className="w-full flex items-center justify-between p-4 -m-4 hover:bg-gray-50 rounded-lg transition-colors"
            >
              <div className="flex items-center space-x-4">
                <div className={`p-2 ${colors.bg} rounded-lg`}>
                  <Icon className={`w-5 h-5 ${colors.icon}`} />
                </div>
                <div className="text-left">
                  <h3 className="text-lg font-semibold text-gray-900">
                    {severityLabels[severity]}
                  </h3>
                  <p className="text-sm text-gray-600">
                    {severityDescriptions[severity]}
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${colors.badge}`}>
                  {issueList.length} {issueList.length === 1 ? 'issue' : 'issues'}
                </span>
                {isExpanded ? (
                  <ChevronDown className="w-5 h-5 text-gray-400" />
                ) : (
                  <ChevronRight className="w-5 h-5 text-gray-400" />
                )}
              </div>
            </button>

            {isExpanded && (
              <div className="mt-6 space-y-4">
                {issueList.map((issue, index) => (
                  <div
                    key={index}
                    className={`p-4 rounded-lg border ${colors.bg} ${colors.border}`}
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-start space-x-3">
                        <Icon className={`w-4 h-4 mt-0.5 ${colors.icon} flex-shrink-0`} />
                        <div className="flex-1">
                          <h4 className={`font-medium ${colors.text}`}>
                            {issue.message}
                          </h4>
                          <div className="flex items-center space-x-2 mt-1">
                            <span className="text-xs bg-white px-2 py-1 rounded-full text-gray-600 border">
                              {issue.category}
                            </span>
                            <span className="text-xs text-gray-500">
                              {issue.type}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    {issue.recommendation && (
                      <div className="mt-3 p-3 bg-white rounded border">
                        <h5 className="text-sm font-medium text-gray-900 mb-1">
                          Recommended Fix:
                        </h5>
                        <p className="text-sm text-gray-700">
                          {issue.recommendation}
                        </p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};

export default IssuesList;
