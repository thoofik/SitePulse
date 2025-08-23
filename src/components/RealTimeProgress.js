import React from 'react';
import { useAudit } from '../contexts/AuditContext';
import { Activity, CheckCircle, AlertCircle, Clock, Zap, Eye } from 'lucide-react';

const RealTimeProgress = () => {
    const {
        isConnected,
        auditStatus,
        auditProgress,
        currentAudit,
        auditResults,
        connectionStatus
    } = useAudit();

    const getStatusIcon = () => {
        switch (auditStatus) {
            case 'idle':
                return <Clock className="w-5 h-5 text-gray-400" />;
            case 'starting':
                return <Zap className="w-5 h-5 text-blue-500 animate-pulse" />;
            case 'running':
                return <Activity className="w-5 h-5 text-green-500 animate-pulse" />;
            case 'completed':
                return <CheckCircle className="w-5 h-5 text-green-600" />;
            case 'error':
                return <AlertCircle className="w-5 h-5 text-red-500" />;
            default:
                return <Clock className="w-5 h-5 text-gray-400" />;
        }
    };

    const getStatusColor = () => {
        switch (auditStatus) {
            case 'idle':
                return 'bg-gray-100 text-gray-600';
            case 'starting':
                return 'bg-blue-100 text-blue-600';
            case 'running':
                return 'bg-green-100 text-green-600';
            case 'completed':
                return 'bg-green-100 text-green-600';
            case 'error':
                return 'bg-red-100 text-red-600';
            default:
                return 'bg-gray-100 text-gray-600';
        }
    };

    const getConnectionStatusColor = () => {
        switch (connectionStatus) {
            case 'connected':
                return 'bg-green-100 text-green-600';
            case 'disconnected':
                return 'bg-red-100 text-red-600';
            case 'error':
                return 'bg-red-100 text-red-600';
            default:
                return 'bg-gray-100 text-gray-600';
        }
    };

    const getCurrentAuditLabel = () => {
        if (!currentAudit) return 'Waiting...';
        
        const labels = {
            'screenshot': 'Capturing Screenshot',
            'security': 'Security Analysis',
            'performance': 'Performance Analysis',
            'seo': 'SEO Analysis',
            'accessibility': 'Accessibility Analysis'
        };
        
        return labels[currentAudit] || currentAudit;
    };

    const getCompletedAudits = () => {
        return Object.keys(auditResults).filter(key => 
            auditResults[key] && !auditResults[key].error
        );
    };

    if (!isConnected) {
        return (
            <div className="bg-white rounded-lg shadow-md p-6 mb-6">
                <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-gray-800">Audit Engine Status</h3>
                    <div className={`px-3 py-1 rounded-full text-sm font-medium ${getConnectionStatusColor()}`}>
                        {connectionStatus === 'connected' ? 'Connected' : 'Disconnected'}
                    </div>
                </div>
                <div className="text-center py-8">
                    <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
                    <p className="text-gray-600">Not connected to audit engine</p>
                    <p className="text-sm text-gray-500 mt-2">Please check your connection and try again</p>
                </div>
            </div>
        );
    }

    return (
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-800">Real-Time Audit Progress</h3>
                <div className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor()}`}>
                    {getStatusIcon()}
                    <span className="ml-2 capitalize">{auditStatus}</span>
                </div>
            </div>

            {/* Progress Bar */}
            <div className="mb-6">
                <div className="flex justify-between text-sm text-gray-600 mb-2">
                    <span>Progress</span>
                    <span>{auditProgress}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                    <div 
                        className="bg-gradient-to-r from-blue-500 to-green-500 h-3 rounded-full transition-all duration-500 ease-out"
                        style={{ width: `${auditProgress}%` }}
                    ></div>
                </div>
            </div>

            {/* Current Status */}
            {auditStatus === 'running' && (
                <div className="mb-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
                    <div className="flex items-center">
                        <Activity className="w-5 h-5 text-blue-500 mr-3 animate-pulse" />
                        <div>
                            <p className="font-medium text-blue-800">Currently Running</p>
                            <p className="text-sm text-blue-600">{getCurrentAuditLabel()}</p>
                        </div>
                    </div>
                </div>
            )}

            {/* Completed Audits */}
            {getCompletedAudits().length > 0 && (
                <div className="mb-4">
                    <h4 className="text-sm font-medium text-gray-700 mb-3">Completed Audits</h4>
                    <div className="grid grid-cols-2 gap-3">
                        {getCompletedAudits().map(auditType => {
                            if (auditType === 'screenshot') {
                                return (
                                    <div key={auditType} className="flex items-center p-3 bg-blue-50 rounded-lg border border-blue-200">
                                        <Eye className="w-4 h-4 text-blue-500 mr-2" />
                                        <div className="flex-1">
                                            <p className="text-sm font-medium text-blue-800 capitalize">Screenshot</p>
                                            <p className="text-xs text-blue-600">Captured ✓</p>
                                        </div>
                                    </div>
                                );
                            }
                            
                            const result = auditResults[auditType];
                            const score = result?.score || 0;
                            const grade = score >= 90 ? 'A' : score >= 80 ? 'B' : score >= 70 ? 'C' : score >= 60 ? 'D' : 'F';
                            
                            return (
                                <div key={auditType} className="flex items-center p-3 bg-green-50 rounded-lg border border-green-200">
                                    <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                                    <div className="flex-1">
                                        <p className="text-sm font-medium text-green-800 capitalize">{auditType}</p>
                                        <p className="text-xs text-green-600">{score}/100 (Grade {grade})</p>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            )}

            {/* Connection Status */}
            <div className="flex items-center justify-between text-sm">
                <span className="text-gray-500">Engine Status:</span>
                <div className={`px-2 py-1 rounded-full text-xs font-medium ${getConnectionStatusColor()}`}>
                    {connectionStatus === 'connected' ? 'Connected' : 'Disconnected'}
                </div>
            </div>
        </div>
    );
};

export default RealTimeProgress;
