import React, { useState } from 'react';
import { Eye, Download, ExternalLink, Maximize2, Minimize2 } from 'lucide-react';

const ScreenshotViewer = ({ screenshot, url, className = "" }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  if (!screenshot || !screenshot.success) {
    return (
      <div className={`bg-gray-50 rounded-lg p-6 text-center ${className}`}>
        <Eye className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-gray-600 mb-2">Screenshot Unavailable</h3>
        <p className="text-gray-500 text-sm">
          {screenshot?.error || 'Failed to capture webpage screenshot'}
        </p>
        {screenshot?.note && (
          <p className="text-gray-400 text-xs mt-2 italic">{screenshot.note}</p>
        )}
      </div>
    );
  }

  const handleDownload = async () => {
    try {
      setIsLoading(true);
      const response = await fetch(`/api/screenshot/${screenshot.filename}`);
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = screenshot.filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (error) {
      console.error('Failed to download screenshot:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleViewOriginal = () => {
    window.open(url, '_blank');
  };

  const toggleExpanded = () => {
    setIsExpanded(!isExpanded);
  };

  return (
    <div className={`bg-white rounded-lg shadow-md overflow-hidden ${className}`}>
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Eye className="w-5 h-5 text-blue-600" />
            <div>
              <h3 className="text-lg font-semibold text-gray-800">Webpage Screenshot</h3>
              <p className="text-sm text-gray-600">
                Captured at {new Date(screenshot.timestamp).toLocaleString()}
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={handleViewOriginal}
              className="btn btn-outline btn-sm flex items-center space-x-2"
              title="View original webpage"
            >
              <ExternalLink className="w-4 h-4" />
              <span>Original</span>
            </button>
            <button
              onClick={handleDownload}
              disabled={isLoading}
              className="btn btn-outline btn-sm flex items-center space-x-2"
              title="Download screenshot"
            >
              <Download className="w-4 h-4" />
              <span>{isLoading ? 'Downloading...' : 'Download'}</span>
            </button>
            <button
              onClick={toggleExpanded}
              className="btn btn-outline btn-sm flex items-center space-x-2"
              title={isExpanded ? 'Minimize' : 'Expand'}
            >
              {isExpanded ? (
                <Minimize2 className="w-4 h-4" />
              ) : (
                <Maximize2 className="w-4 h-4" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Screenshot Content */}
      <div className="p-6">
        {/* Screenshot Info */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div className="bg-gray-50 rounded-lg p-4">
            <h4 className="font-medium text-gray-700 mb-2">Screenshot Details</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Dimensions:</span>
                <span className="font-medium">
                  {screenshot.dimensions.width} × {screenshot.dimensions.height}px
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Viewport:</span>
                <span className="font-medium">
                  {screenshot.viewport.width} × {screenshot.viewport.height}px
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">File Size:</span>
                <span className="font-medium">
                  {(screenshot.file_size / 1024).toFixed(1)} KB
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Method:</span>
                <span className="font-medium capitalize">{screenshot.method}</span>
              </div>
            </div>
          </div>
          
          <div className="bg-gray-50 rounded-lg p-4">
            <h4 className="font-medium text-gray-700 mb-2">Capture Information</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">URL:</span>
                <span className="font-medium text-blue-600 truncate ml-2" title={url}>
                  {url}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Timestamp:</span>
                <span className="font-medium">
                  {new Date(screenshot.timestamp).toLocaleString()}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Status:</span>
                <span className="font-medium text-green-600">✓ Captured</span>
              </div>
            </div>
          </div>
        </div>

        {/* Screenshot Display */}
        <div className="text-center">
          <div className="relative inline-block">
            <img
              src={`/api/screenshot/${screenshot.filename}`}
              alt={`Screenshot of ${url}`}
              className={`rounded-lg shadow-lg border border-gray-200 ${
                isExpanded ? 'max-w-none' : 'max-w-full h-auto'
              }`}
              style={{
                maxHeight: isExpanded ? 'none' : '600px',
                objectFit: 'contain'
              }}
            />
            
            {/* Overlay with expand/collapse info */}
            {!isExpanded && (
              <div className="absolute inset-0 bg-black bg-opacity-0 hover:bg-opacity-10 transition-all duration-200 rounded-lg flex items-center justify-center">
                <div className="bg-white bg-opacity-90 rounded-lg px-4 py-2 shadow-lg opacity-0 hover:opacity-100 transition-opacity duration-200">
                  <p className="text-sm text-gray-700 font-medium">Click to expand</p>
                </div>
              </div>
            )}
          </div>
          
          {/* Thumbnail if available */}
          {screenshot.thumbnail_path && (
            <div className="mt-4">
              <p className="text-sm text-gray-600 mb-2">Thumbnail Preview:</p>
              <img
                src={`/api/screenshot/${screenshot.filename.replace('.png', '_thumb.png')}`}
                alt={`Thumbnail of ${url}`}
                className="inline-block rounded border border-gray-200 shadow-sm"
                style={{ maxHeight: '150px' }}
              />
            </div>
          )}
        </div>

        {/* Additional Notes */}
        {screenshot.note && (
          <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0">
                <svg className="w-5 h-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
              </div>
              <div>
                <h4 className="text-sm font-medium text-yellow-800">Note</h4>
                <p className="text-sm text-yellow-700 mt-1">{screenshot.note}</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ScreenshotViewer;
