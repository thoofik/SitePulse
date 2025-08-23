import { io } from 'socket.io-client';

class WebSocketService {
    constructor() {
        this.socket = null;
        this.isConnected = false;
        this.listeners = new Map();
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
    }

    connect() {
        try {
            // Connect to the Flask-SocketIO backend
            this.socket = io('http://localhost:5000', {
                transports: ['websocket', 'polling'],
                timeout: 20000,
                reconnection: true,
                reconnectionAttempts: this.maxReconnectAttempts,
                reconnectionDelay: this.reconnectDelay,
                reconnectionDelayMax: 5000,
                maxReconnectionAttempts: this.maxReconnectAttempts,
                autoConnect: true
            });

            this.setupEventListeners();
            this.isConnected = true;
            
            console.log('WebSocket connected to SitePulse Audit Engine');
            
        } catch (error) {
            console.error('Failed to connect to WebSocket:', error);
            this.isConnected = false;
        }
    }

    setupEventListeners() {
        if (!this.socket) return;

        // Connection events
        this.socket.on('connect', () => {
            console.log('WebSocket connected');
            this.isConnected = true;
            this.reconnectAttempts = 0;
            this.emit('connected', { status: 'connected' });
        });

        this.socket.on('disconnect', () => {
            console.log('WebSocket disconnected');
            this.isConnected = false;
            this.emit('disconnected', { status: 'disconnected' });
        });

        this.socket.on('connect_error', (error) => {
            console.error('WebSocket connection error:', error);
            this.isConnected = false;
            this.emit('connection_error', { error: error.message });
        });

        // Audit progress events
        this.socket.on('audit_progress_update', (data) => {
            console.log('Audit progress update:', data);
            this.emit('audit_progress_update', data);
        });

        // Real-time audit results
        this.socket.on('audit_results_update', (data) => {
            console.log('Audit results update:', data);
            this.emit('audit_results_update', data);
        });

        // Audit summary
        this.socket.on('audit_summary_update', (data) => {
            console.log('Audit summary update:', data);
            this.emit('audit_summary_update', data);
        });

        // Audit completion
        this.socket.on('audit_completed', (data) => {
            console.log('Audit completed:', data);
            this.emit('audit_completed', data);
        });

        // Error handling
        this.socket.on('audit_error', (data) => {
            console.error('Audit error:', data);
            this.emit('audit_error', data);
        });

        // Audit data responses
        this.socket.on('audit_data_response', (data) => {
            console.log('Audit data response:', data);
            this.emit('audit_data_response', data);
        });

        // Subscription confirmation
        this.socket.on('audit_subscription_confirmed', (data) => {
            console.log('Audit subscription confirmed:', data);
            this.emit('audit_subscription_confirmed', data);
        });

        // Status response
        this.socket.on('audit_status_response', (data) => {
            console.log('Audit status response:', data);
            this.emit('audit_status_response', data);
        });
    }

    // Subscribe to events
    on(event, callback) {
        if (!this.listeners.has(event)) {
            this.listeners.set(event, []);
        }
        this.listeners.get(event).push(callback);
    }

    // Unsubscribe from events
    off(event, callback) {
        if (this.listeners.has(event)) {
            const callbacks = this.listeners.get(event);
            const index = callbacks.indexOf(callback);
            if (index > -1) {
                callbacks.splice(index, 1);
            }
        }
    }

    // Emit events to listeners
    emit(event, data) {
        if (this.listeners.has(event)) {
            this.listeners.get(event).forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error(`Error in event listener for ${event}:`, error);
                }
            });
        }
    }

    // Request audit status
    requestAuditStatus() {
        if (this.socket && this.isConnected) {
            this.socket.emit('request_audit_status', {});
        }
    }

    // Subscribe to audit updates
    subscribeToAudit() {
        if (this.socket && this.isConnected) {
            this.socket.emit('subscribe_to_audit', {});
        }
    }

    // Request specific audit data
    requestAuditData(auditType, url) {
        if (this.socket && this.isConnected) {
            this.socket.emit('request_audit_data', {
                audit_type: auditType,
                url: url
            });
        }
    }

    // Disconnect
    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
            this.socket = null;
            this.isConnected = false;
            this.listeners.clear();
        }
    }

    // Get connection status
    getConnectionStatus() {
        return {
            isConnected: this.isConnected,
            socketId: this.socket?.id || null
        };
    }
}

// Create and export a singleton instance
const websocketService = new WebSocketService();
export default websocketService;
