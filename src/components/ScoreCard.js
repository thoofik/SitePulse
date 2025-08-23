import React from 'react';

const ScoreCard = ({ title, score, grade, icon: Icon, color, bgColor }) => {
  const getGradeColor = (grade) => {
    const colors = {
      'A': 'text-green-600 bg-green-100 border-green-200',
      'B': 'text-blue-600 bg-blue-100 border-blue-200',
      'C': 'text-yellow-600 bg-yellow-100 border-yellow-200',
      'D': 'text-orange-600 bg-orange-100 border-orange-200',
      'F': 'text-red-600 bg-red-100 border-red-200'
    };
    return colors[grade] || 'text-gray-600 bg-gray-100 border-gray-200';
  };

  const getScoreColor = (score) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 80) return 'text-blue-600';
    if (score >= 70) return 'text-yellow-600';
    if (score >= 60) return 'text-orange-600';
    return 'text-red-600';
  };

  return (
    <div className="card hover:shadow-md transition-shadow duration-200">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className={`p-2 ${bgColor} rounded-lg`}>
            <Icon className={`w-5 h-5 ${color}`} />
          </div>
          <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        </div>
        <div className={`px-3 py-1 rounded-full text-sm font-bold border ${getGradeColor(grade)}`}>
          {grade}
        </div>
      </div>
      
      <div className="flex items-end justify-between">
        <div>
          <div className={`text-3xl font-bold ${getScoreColor(score)}`}>
            {score}
          </div>
          <div className="text-sm text-gray-500">out of 100</div>
        </div>
        
        {/* Progress bar */}
        <div className="flex-1 ml-4">
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className={`h-2 rounded-full transition-all duration-500 ${
                score >= 90 ? 'bg-green-500' :
                score >= 80 ? 'bg-blue-500' :
                score >= 70 ? 'bg-yellow-500' :
                score >= 60 ? 'bg-orange-500' : 'bg-red-500'
              }`}
              style={{ width: `${Math.min(score, 100)}%` }}
            ></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ScoreCard;
