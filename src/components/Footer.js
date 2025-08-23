import React from 'react';
import { Activity, Github, Twitter, Mail } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="bg-white border-t border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="col-span-1 md:col-span-2">
            <div className="flex items-center space-x-2 mb-4">
              <div className="flex items-center justify-center w-8 h-8 bg-gradient-to-r from-primary-600 to-purple-600 rounded-lg">
                <Activity className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold text-gradient">SitePulse</span>
            </div>
            <p className="text-gray-600 mb-4 max-w-md">
              Comprehensive website auditing platform that evaluates security, performance, SEO, and accessibility. 
              Get actionable insights to improve your website's digital health.
            </p>
            <div className="flex space-x-4">
              <a href="#" className="text-gray-400 hover:text-gray-600 transition-colors">
                <Github className="w-5 h-5" />
              </a>
              <a href="#" className="text-gray-400 hover:text-gray-600 transition-colors">
                <Twitter className="w-5 h-5" />
              </a>
              <a href="#" className="text-gray-400 hover:text-gray-600 transition-colors">
                <Mail className="w-5 h-5" />
              </a>
            </div>
          </div>

          {/* Features */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wider mb-4">
              Features
            </h3>
            <ul className="space-y-2">
              <li>
                <span className="text-gray-600 hover:text-gray-900 transition-colors cursor-pointer">
                  Security Analysis
                </span>
              </li>
              <li>
                <span className="text-gray-600 hover:text-gray-900 transition-colors cursor-pointer">
                  Performance Testing
                </span>
              </li>
              <li>
                <span className="text-gray-600 hover:text-gray-900 transition-colors cursor-pointer">
                  SEO Optimization
                </span>
              </li>
              <li>
                <span className="text-gray-600 hover:text-gray-900 transition-colors cursor-pointer">
                  Accessibility Check
                </span>
              </li>
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 uppercase tracking-wider mb-4">
              Resources
            </h3>
            <ul className="space-y-2">
              <li>
                <span className="text-gray-600 hover:text-gray-900 transition-colors cursor-pointer">
                  Documentation
                </span>
              </li>
              <li>
                <span className="text-gray-600 hover:text-gray-900 transition-colors cursor-pointer">
                  API Reference
                </span>
              </li>
              <li>
                <span className="text-gray-600 hover:text-gray-900 transition-colors cursor-pointer">
                  Best Practices
                </span>
              </li>
              <li>
                <span className="text-gray-600 hover:text-gray-900 transition-colors cursor-pointer">
                  Support
                </span>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-8 pt-8 border-t border-gray-200">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <p className="text-gray-500 text-sm">
              © 2024 SitePulse. All rights reserved.
            </p>
            <div className="flex space-x-6 mt-4 md:mt-0">
              <span className="text-gray-500 hover:text-gray-900 text-sm cursor-pointer">
                Privacy Policy
              </span>
              <span className="text-gray-500 hover:text-gray-900 text-sm cursor-pointer">
                Terms of Service
              </span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
