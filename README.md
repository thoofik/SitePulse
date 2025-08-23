# 🚀 SitePulse - Professional Website Audit Tool

A comprehensive, real-time website auditing platform that provides detailed performance, security, SEO, and accessibility analysis with interactive reports, actionable recommendations, and visual proof through webpage screenshots.

![SitePulse Logo](https://img.shields.io/badge/SitePulse-Audit%20Tool-blue?style=for-the-badge&logo=shield-check)
![Version](https://img.shields.io/badge/Version-2.1.0-green?style=for-the-badge)


## ✨ Features

### 🔍 **Comprehensive Auditing**
- **Performance Analysis**: Core Web Vitals, Lighthouse scores, page speed optimization
- **Security Scanning**: Vulnerability detection, SSL/TLS checks, security headers analysis
- **SEO Optimization**: Meta tags, structured data, content analysis, search engine optimization
- **Accessibility Testing**: WCAG compliance, screen reader compatibility, accessibility standards

### 📸 **Visual Proof & Evidence**
- **Webpage Screenshots**: Automatic capture of website state during audit
- **Selenium Integration**: High-quality screenshots using browser automation
- **Visual Documentation**: Proof of website condition at audit time
- **Screenshot Storage**: Organized storage with automatic cleanup

### 🚀 **Real-Time Experience**
- **Live Progress Tracking**: Real-time audit progress with WebSocket communication
- **Instant Results**: Live updates as each audit type completes
- **Interactive Reports**: Dynamic, responsive reports with real-time data
- **Auto-Redirect**: Seamless navigation from audit to detailed reports

### 🎨 **Modern UI/UX**
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile devices
- **Interactive Elements**: Hover effects, animations, and smooth transitions
- **Professional Reports**: Beautiful, presentation-ready audit reports
- **User-Friendly Interface**: Plain English explanations, no technical jargon

### 🔧 **Advanced Features**
- **Fallback Strategies**: Multiple API endpoints with graceful degradation
- **Data Compression**: Smart localStorage management with automatic cleanup
- **Quick Re-audit**: One-click re-auditing of previously analyzed websites
- **Export Options**: Print reports, export issues, recommendations, and detailed results
- **Copy Functionality**: Easy copying of audit details for team collaboration

## 🏗️ Architecture

### **Frontend (React)**
```
src/
├── components/           # Reusable UI components
│   ├── MetricsChart.js   # Performance metrics visualization
│   ├── ScoreCard.js      # Individual audit score cards
│   ├── IssuesList.js     # Issues and problems display
│   ├── RecommendationsList.js # Actionable recommendations
│   ├── RealTimeProgress.js    # Live audit progress
│   └── ScreenshotViewer.js   # Webpage screenshot display
├── contexts/             # React context providers
│   └── AuditContext.js   # Global audit state management
├── pages/                # Main application pages
│   ├── App.js           # Main app routing
│   ├── AuditPage.js     # Audit initiation and progress
│   └── ReportPage.js    # Detailed audit reports
└── services/             # External service integrations
    └── websocketService.js # WebSocket communication
```

### **Backend (Flask + Python)**
```
audit_engine/
├── __init__.py           # Package initialization
├── config.py             # Configuration management
├── lighthouse_api.py     # Google PageSpeed Insights integration
├── performance_analyzer.py # Core performance analysis engine
├── security_analyzer.py  # Security vulnerability scanning
├── seo_analyzer.py       # SEO optimization analysis
├── accessibility_analyzer.py # Accessibility compliance checking
├── screenshot_service.py # Webpage screenshot capture service
└── report_generator.py   # Report generation and formatting

app.py                    # Main Flask application
requirements.txt          # Python dependencies
```

## 🚀 Quick Start

### **Prerequisites**
- Python 3.11+ 
- Node.js 16+
- npm or yarn
- Chrome/Chromium browser (for screenshot functionality)

### **1. Clone the Repository**
```bash
git clone https://github.com/yourusername/sitepulse.git
cd sitepulse
```

### **2. Backend Setup**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables (optional)
export LIGHTHOUSE_API_KEY="your_api_key_here"
export LIGHTHOUSE_BASE_URL="https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

# Start the backend server
python app.py
```

### **3. Frontend Setup**
```bash
# Install dependencies
npm install

# Start development server
npm start
```

### **4. Access the Application**
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:5000
- **WebSocket**: ws://localhost:5000

## 📱 Usage Guide

### **Starting an Audit**

1. **Navigate to Audit Page**: Click "Start New Audit" or visit `/audit`
2. **Enter Website URL**: Input the full URL (https://example.com)
3. **Select Audit Types**: Choose from Security, Performance, SEO, Accessibility
4. **Click "Start Comprehensive Audit"**: Begin the analysis process
5. **Monitor Progress**: Watch real-time progress updates including screenshot capture
6. **Auto-Redirect**: Automatically redirected to detailed report

### **Understanding Reports**

#### **Executive Summary**
- **Overall Grade**: A-F rating based on comprehensive analysis
- **Key Metrics**: Critical issues, high priority items, recommendations count
- **Webpage Screenshot**: Visual proof of website state during audit
- **Business Impact**: Strategic insights and improvement opportunities

#### **Category Scores**
- **Individual Scores**: Performance, Security, SEO, Accessibility ratings
- **Interactive Cards**: Hover for detailed information
- **Visual Indicators**: Color-coded grades and progress bars

#### **Detailed Analysis**
- **Overview Tab**: Performance charts, key findings, and webpage screenshot
- **Issues Tab**: Prioritized problems with impact assessment and actionable fixes
- **Recommendations Tab**: User-friendly improvements categorized by timeline and effort
- **Detailed Results Tab**: Comprehensive analysis with technical details and export options

### **Quick Re-auditing**

1. **From Report Page**: Click "Re-audit This URL" button
2. **Pre-filled Form**: URL and audit types automatically populated
3. **Quick Start**: Use "Quick Start Audit" for immediate analysis
4. **Progress Tracking**: Monitor improvements over time

## 🔧 Configuration

### **Environment Variables**
```bash
# Lighthouse API Configuration
LIGHTHOUSE_API_KEY=your_google_api_key
LIGHTHOUSE_BASE_URL=https://www.googleapis.com/pagespeedonline/v5/runPagespeed

# Server Configuration
FLASK_ENV=development
FLASK_DEBUG=true
PORT=5000

# WebSocket Configuration
SOCKETIO_CORS_ALLOWED_ORIGINS=*

# Screenshot Configuration
SCREENSHOT_DIR=screenshots
SCREENSHOT_QUALITY=85
SCREENSHOT_TIMEOUT=30
```

### **Audit Engine Settings**
```python
# audit_engine/config.py
class AuditConfig:
    # Performance thresholds
    PERFORMANCE_THRESHOLD = 90
    ACCESSIBILITY_THRESHOLD = 80
    SEO_THRESHOLD = 85
    SECURITY_THRESHOLD = 95
    
    # API rate limiting
    API_RATE_LIMIT = 10  # requests per minute
    REQUEST_TIMEOUT = 30  # seconds
    
    # Fallback settings
    ENABLE_FALLBACK_APIS = True
    LOCAL_ANALYSIS_FALLBACK = True
    
    # Screenshot settings
    SCREENSHOT_ENABLED = True
    SCREENSHOT_WIDTH = 1920
    SCREENSHOT_HEIGHT = 1080
```

## 🎯 API Endpoints

### **Core Endpoints**
```
POST /api/audit              # Start comprehensive audit
POST /api/audit/raw          # Get raw audit results
GET  /api/audit/status       # Check audit status
GET  /api/audit/progress     # Get audit progress
POST /api/screenshot         # Capture webpage screenshot
```

### **WebSocket Events**
```javascript
// Client to Server
'start_audit'                 # Initiate new audit
'subscribe_to_audit'          # Subscribe to audit updates

// Server to Client
'audit_progress_update'       # Progress updates
'audit_results_update'        # Individual audit results
'audit_completed'            # Audit completion with screenshot data
'audit_error'                # Error notifications
```

## 🎨 Customization

### **Theming**
```css
/* Custom color schemes */
:root {
  --primary-color: #3b82f6;
  --success-color: #10b981;
  --warning-color: #f59e0b;
  --danger-color: #ef4444;
  --info-color: #06b6d4;
}

/* Custom animations */
.animate-fade-in {
  animation: fadeIn 0.6s ease-out;
}

.animate-slide-up {
  animation: slideUp 0.8s ease-out;
}
```

### **Component Customization**
```javascript
// Custom audit types
const customAuditTypes = [
  {
    id: 'custom',
    name: 'Custom Analysis',
    description: 'Custom audit type',
    icon: CustomIcon,
    color: 'text-purple-500',
    bgColor: 'bg-purple-50'
  }
];
```

## 🧪 Testing

### **Backend Testing**
```bash
# Run audit engine tests
python -m pytest test_audit_engine.py

# Run simple tests
python simple_test.py

# Test screenshot service
python simple_screenshot_test.py

# Test specific components
python -c "from audit_engine.performance_analyzer import PerformanceAnalyzer; print('Import successful')"
```

### **Frontend Testing**
```bash
# Run tests
npm test

# Run tests with coverage
npm run test:coverage

# Run tests in watch mode
npm run test:watch
```

## 📊 Performance Metrics

### **Core Web Vitals**
- **LCP (Largest Contentful Paint)**: < 2.5s
- **FID (First Input Delay)**: < 100ms
- **CLS (Cumulative Layout Shift)**: < 0.1

### **Performance Scores**
- **90-100**: Excellent (Grade A)
- **80-89**: Good (Grade B)
- **70-79**: Fair (Grade C)
- **60-69**: Poor (Grade D)
- **0-59**: Very Poor (Grade F)

## 🔒 Security Features

### **Vulnerability Scanning**
- **SSL/TLS Configuration**: Certificate validation and security
- **Security Headers**: HSTS, CSP, X-Frame-Options analysis
- **Content Security**: Malicious content detection
- **Input Validation**: Security parameter testing

### **Data Protection**
- **Local Storage**: Client-side data with automatic cleanup
- **No Data Persistence**: Audit results stored locally only
- **Secure Communication**: WebSocket over HTTPS/WSS
- **Screenshot Privacy**: Screenshots stored locally, not transmitted

## 🌐 Browser Support

- **Chrome**: 90+
- **Firefox**: 88+
- **Safari**: 14+
- **Edge**: 90+
- **Mobile Browsers**: iOS Safari 14+, Chrome Mobile 90+

## 🚀 Deployment

### **Production Build**
```bash
# Build frontend
npm run build

# Start production server
python app.py --production
```

### **Docker Deployment**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

### **Environment-Specific Configs**
```bash
# Development
FLASK_ENV=development
DEBUG=true

# Production
FLASK_ENV=production
DEBUG=false
FLASK_SECRET_KEY=your_secret_key_here
```

## 🤝 Contributing

### **Development Setup**
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Add tests for new functionality
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

### **Code Style**
- **Python**: Follow PEP 8 guidelines
- **JavaScript**: Use ESLint configuration
- **CSS**: Follow BEM methodology
- **Commits**: Use conventional commit format

## 📝 Changelog

### **Version 2.1.0** (Current)
- 📸 **Webpage Screenshot System**: Automatic capture and display of website state
- 🎯 **Enhanced User Experience**: Plain English explanations, no technical jargon
- 🔧 **Improved Recommendations**: User-friendly, actionable improvement suggestions
- 📊 **Better Issue Handling**: Clear problem descriptions with specific solutions
- 🚀 **Export Functionality**: Export issues, recommendations, and detailed results
- 📱 **Technical Terms Glossary**: Expandable glossary for technical concepts
- 🎨 **Enhanced UI Components**: Better visual hierarchy and user guidance
- 🔄 **Improved Data Flow**: Better WebSocket integration and state management

### **Version 2.0.0**
- ✨ Complete UI/UX redesign with modern components
- 🚀 Real-time WebSocket communication
- 🔄 Auto-redirect functionality from audit to reports
- 🎨 Enhanced animations and interactions
- 📱 Improved mobile responsiveness
- 🔧 Quick re-audit functionality
- 📊 Enhanced reporting with interactive elements

### **Version 1.0.0**
- 🎯 Initial release with basic audit functionality
- 📊 Basic performance analysis
- 🔒 Security scanning capabilities
- 📈 SEO optimization features

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google PageSpeed Insights API** for performance metrics
- **Lighthouse** for web performance auditing
- **Selenium** for webpage screenshot functionality
- **React** for the frontend framework
- **Flask** for the backend framework
- **Tailwind CSS** for styling and components


</div>
