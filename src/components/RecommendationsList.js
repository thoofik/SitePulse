import React, { useState } from 'react';
import { 
  CheckCircle, 
  Clock, 
  Calendar, 
  CalendarDays,
  ChevronDown, 
  ChevronRight,
  Zap,
  TrendingUp,
  Target
} from 'lucide-react';

const RecommendationsList = ({ recommendations }) => {
  const [activeTab, setActiveTab] = useState('quick_wins');
  const [expandedItems, setExpandedItems] = useState(new Set());

  const toggleExpanded = (index) => {
    const newExpanded = new Set(expandedItems);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedItems(newExpanded);
  };

  const tabs = [
    {
      id: 'quick_wins',
      label: 'Quick Wins',
      icon: Zap,
      description: 'Easy fixes with high impact',
      color: 'text-green-600',
      bgColor: 'bg-green-50'
    },
    {
      id: 'short_term',
      label: 'Short Term',
      icon: Clock,
      description: '1-2 weeks',
      color: 'text-blue-600',
      bgColor: 'bg-blue-50'
    },
    {
      id: 'medium_term',
      label: 'Medium Term',
      icon: Calendar,
      description: '1-3 months',
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-50'
    },
    {
      id: 'long_term',
      label: 'Long Term',
      icon: CalendarDays,
      description: '3+ months',
      color: 'text-purple-600',
      bgColor: 'bg-purple-50'
    }
  ];

  const getEffortColor = (effort) => {
    switch (effort) {
      case 'low':
        return 'bg-green-100 text-green-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'high':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getImpactColor = (impact) => {
    switch (impact) {
      case 'high':
        return 'bg-red-100 text-red-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'low':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (!recommendations || Object.keys(recommendations).length === 0) {
    return (
      <div className="card text-center py-12">
        <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <CheckCircle className="w-8 h-8 text-blue-600" />
        </div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">No Recommendations</h3>
        <p className="text-gray-600">Your website is in excellent shape! No recommendations at this time.</p>
      </div>
    );
  }

  const currentRecommendations = recommendations[activeTab] || [];

  return (
    <div className="space-y-6">
      {/* Tabs */}
      <div className="card">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            const count = recommendations[tab.id]?.length || 0;

            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`p-4 rounded-lg text-left transition-all duration-200 ${
                  isActive 
                    ? `${tab.bgColor} border-2 border-current ${tab.color}` 
                    : 'bg-gray-50 hover:bg-gray-100 text-gray-600 border-2 border-transparent'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <Icon className={`w-5 h-5 ${isActive ? tab.color : 'text-gray-400'}`} />
                  <span className={`text-sm font-bold px-2 py-1 rounded-full ${
                    isActive ? 'bg-white' : 'bg-gray-200'
                  }`}>
                    {count}
                  </span>
                </div>
                <h3 className="font-semibold text-sm mb-1">{tab.label}</h3>
                <p className="text-xs opacity-75">{tab.description}</p>
              </button>
            );
          })}
        </div>
      </div>

      {/* Recommendations List */}
      {currentRecommendations.length === 0 ? (
        <div className="card text-center py-8">
          <TrendingUp className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No {tabs.find(t => t.id === activeTab)?.label} Recommendations
          </h3>
          <p className="text-gray-600">
            Great! You don't have any recommendations in this category.
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {currentRecommendations.map((recommendation, index) => {
            const isExpanded = expandedItems.has(index);
            
            return (
              <div key={index} className="card hover:shadow-md transition-shadow">
                <button
                  onClick={() => toggleExpanded(index)}
                  className="w-full text-left"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-start space-x-3 mb-3">
                        <Target className="w-5 h-5 text-primary-500 mt-0.5 flex-shrink-0" />
                        <div className="flex-1">
                          <h3 className="font-semibold text-gray-900 mb-2">
                            {recommendation.title}
                          </h3>
                          <div className="flex items-center space-x-2 mb-2">
                            <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full">
                              {recommendation.category}
                            </span>
                            <span className={`text-xs px-2 py-1 rounded-full font-medium ${getEffortColor(recommendation.effort)}`}>
                              {recommendation.effort} effort
                            </span>
                            <span className={`text-xs px-2 py-1 rounded-full font-medium ${getImpactColor(recommendation.impact)}`}>
                              {recommendation.impact} impact
                            </span>
                          </div>
                          {!isExpanded && (
                            <p className="text-sm text-gray-600 line-clamp-2">
                              {recommendation.description}
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="ml-4 flex-shrink-0">
                      {isExpanded ? (
                        <ChevronDown className="w-5 h-5 text-gray-400" />
                      ) : (
                        <ChevronRight className="w-5 h-5 text-gray-400" />
                      )}
                    </div>
                  </div>
                </button>

                {isExpanded && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <div className="space-y-4">
                      <div>
                        <h4 className="font-medium text-gray-900 mb-2">Description</h4>
                        <p className="text-gray-700 leading-relaxed">
                          {recommendation.description}
                        </p>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="p-3 bg-blue-50 rounded-lg">
                          <h5 className="font-medium text-blue-900 mb-1">Implementation Effort</h5>
                          <p className="text-sm text-blue-700 capitalize">
                            {recommendation.effort} - {
                              recommendation.effort === 'low' ? 'Can be completed quickly' :
                              recommendation.effort === 'medium' ? 'Requires moderate time investment' :
                              'Significant time and resources needed'
                            }
                          </p>
                        </div>
                        
                        <div className="p-3 bg-green-50 rounded-lg">
                          <h5 className="font-medium text-green-900 mb-1">Business Impact</h5>
                          <p className="text-sm text-green-700 capitalize">
                            {recommendation.impact} - {
                              recommendation.impact === 'high' ? 'Significant improvement expected' :
                              recommendation.impact === 'medium' ? 'Moderate improvement expected' :
                              'Minor but valuable improvement'
                            }
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default RecommendationsList;
