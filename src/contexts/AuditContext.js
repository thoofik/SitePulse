import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import websocketService from '../services/websocketService';

const AuditContext = createContext();

export const useAudit = () => {
    const context = useContext(AuditContext);
    if (!context) {
        throw new Error('useAudit must be used within an AuditProvider');
    }
    return context;
};

export const AuditProvider = ({ children }) => {
    const [isConnected, setIsConnected] = useState(false);
    const [currentAudit, setCurrentAudit] = useState(null);
    const [auditProgress, setAuditProgress] = useState(0);
    const [auditStatus, setAuditStatus] = useState('idle');
    const [auditResults, setAuditResults] = useState({});
    const [auditSummary, setAuditSummary] = useState({});
    const [auditData, setAuditData] = useState({});
    const [connectionStatus, setConnectionStatus] = useState('disconnected');

    // Connect to WebSocket on component mount
    useEffect(() => {
        websocketService.connect();
        
        // Set up event listeners
        websocketService.on('connected', () => {
            setIsConnected(true);
            setConnectionStatus('connected');
        });

        websocketService.on('disconnected', () => {
            setIsConnected(false);
            setConnectionStatus('disconnected');
        });

        websocketService.on('connection_error', (data) => {
            setConnectionStatus('error');
        });

        // Audit progress updates
        websocketService.on('audit_progress_update', (data) => {
            setAuditProgress(data.progress);
            setAuditStatus(data.status);
            
            if (data.current_audit) {
                setCurrentAudit(data.current_audit);
            }
            

        });

        // Real-time audit results
        websocketService.on('audit_results_update', (data) => {
            setAuditResults(prev => {
                const newResults = {
                    ...prev,
                    [data.audit_type]: data.results
                };
                
                // Check if all audits are complete
                const expectedAuditTypes = ['security', 'performance', 'seo', 'accessibility'];
                const completedAudits = Object.keys(newResults).filter(key => 
                    newResults[key] && !newResults[key].error && newResults[key].score !== undefined
                );
                
                // If all expected audits are complete, set completion state
                if (completedAudits.length >= expectedAuditTypes.length &&
                    expectedAuditTypes.every(type => completedAudits.includes(type))) {
                    setAuditStatus('completed');
                    setAuditProgress(100);
                    setCurrentAudit(null);
                }
                
                return newResults;
            });
            

        });

        // Audit summary
        websocketService.on('audit_summary_update', (data) => {
            setAuditSummary(data.summary);
            setAuditProgress(data.progress);
        });

        // Audit completion
        websocketService.on('audit_completed', (data) => {
            setAuditStatus('completed');
            setAuditProgress(100);
            setCurrentAudit(null);
            
            // Store the complete results - handle the correct data structure
            if (data.raw_audit_results && data.raw_audit_results.results) {
                // This is the correct structure from the backend
                setAuditResults(data.raw_audit_results.results);
                
                // Store the complete audit data including screenshot
                setAuditData(data.raw_audit_results);
            } else if (data.results) {
                setAuditResults(data.results);
            } else if (data.audit_results) {
                setAuditResults(data.audit_results);
            } else {
                setAuditResults({});
            }
            
            // Set summary data
            if (data.summary) {
                setAuditSummary(data.summary);
            } else if (data.raw_audit_results && data.raw_audit_results.summary) {
                setAuditSummary(data.raw_audit_results.summary);
            } else {
                setAuditSummary({});
            }
            

        });

        // Error handling
        websocketService.on('audit_error', (data) => {
            setAuditStatus('error');
            setAuditProgress(0);
            setCurrentAudit(null);

        });

        // Cleanup on unmount
        return () => {
            websocketService.disconnect();
        };
    }, []);

    // Monitor audit status changes
    useEffect(() => {
        // Fallback completion detection
        const expectedAuditTypes = ['security', 'performance', 'seo', 'accessibility'];
        const completedAudits = Object.keys(auditResults).filter(key => 
            auditResults[key] && !auditResults[key].error && auditResults[key].score !== undefined
        );
        
        if (auditStatus === 'running' && 
            auditProgress === 100 && 
            completedAudits.length >= expectedAuditTypes.length &&
            expectedAuditTypes.every(type => completedAudits.includes(type))) {
            // All expected audit types are complete, but completion event hasn't fired
            // Set completion state manually
            setAuditStatus('completed');
            setCurrentAudit(null);
        }
    }, [auditStatus, auditProgress, auditResults]);

    // Start a new audit
    const startAudit = useCallback(async (url, auditTypes = ['security', 'performance', 'seo', 'accessibility']) => {
        try {
            setAuditStatus('starting');
            setAuditProgress(0);
            setAuditResults({});
            setAuditSummary({});
            setCurrentAudit(null);

            // Subscribe to audit updates
            websocketService.subscribeToAudit();

            // Start the audit via HTTP (WebSocket will receive real-time updates)
            const response = await fetch('/api/audit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    url,
                    audit_types: auditTypes
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            
            if (result.success) {
                setAuditStatus('running');
                return result;
            } else {
                throw new Error(result.error || 'Failed to start audit');
            }
            
        } catch (error) {
            console.error('Error starting audit:', error);
            setAuditStatus('error');
            throw error;
        }
    }, []);

    // Request specific audit data
    const requestAuditData = useCallback((auditType, url) => {
        websocketService.requestAuditData(auditType, url);
    }, []);

    // Get connection status
    const getConnectionStatus = useCallback(() => {
        return websocketService.getConnectionStatus();
    }, []);

    // Request audit status
    const requestAuditStatus = useCallback(() => {
        websocketService.requestAuditStatus();
    }, []);

    // Reset audit state
    const resetAudit = useCallback(() => {
        setCurrentAudit(null);
        setAuditProgress(0);
        setAuditStatus('idle');
        setAuditResults({});
        setAuditSummary({});
    }, []);

    // Manual completion trigger for testing
    const manuallyCompleteAudit = useCallback(() => {
        console.log('Manually completing audit...');
        setAuditStatus('completed');
        setAuditProgress(100);
        setCurrentAudit(null);
    }, []);

    const value = {
        // State
        isConnected,
        currentAudit,
        auditProgress,
        auditStatus,
        auditResults,
        auditSummary,
        auditData,
        connectionStatus,
        
        // Actions
        startAudit,
        requestAuditData,
        getConnectionStatus,
        requestAuditStatus,
        resetAudit,
        manuallyCompleteAudit,
        
        // Computed values
        isAuditRunning: auditStatus === 'running' || auditStatus === 'starting',
        isAuditCompleted: auditStatus === 'completed',
        hasResults: Object.keys(auditResults).length > 0,
        currentAuditType: currentAudit,
        progressPercentage: auditProgress
    };

    return (
        <AuditContext.Provider value={value}>
            {children}
        </AuditContext.Provider>
    );
};
