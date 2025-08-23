import React from 'react';
import { Link } from 'react-router-dom';
import { Shield, Zap, Search, Eye, ArrowRight, CheckCircle, Globe, TrendingUp } from 'lucide-react';

const HomePage = () => {
  const features = [
    {
      icon: Shield,
      title: 'Security Analysis',
      description: 'Comprehensive vulnerability scanning including SQL injection, XSS, SSL/TLS configuration, and security headers analysis.',
      color: 'text-red-500',
      bgColor: 'bg-red-50'
    },
    {
      icon: Zap,
      title: 'Performance Testing',
      description: 'Detailed performance analysis with Core Web Vitals, load times, resource optimization, and actionable speed improvements.',
      color: 'text-yellow-500',
      bgColor: 'bg-yellow-50'
    },
    {
      icon: Search,
      title: 'SEO Optimization',
      description: 'Complete SEO audit covering meta tags, structured data, content optimization, and search engine visibility factors.',
      color: 'text-blue-500',
      bgColor: 'bg-blue-50'
    },
    {
      icon: Eye,
      title: 'Accessibility Check',
      description: 'WCAG compliance testing for images, forms, navigation, color contrast, and inclusive design principles.',
      color: 'text-green-500',
      bgColor: 'bg-green-50'
    }
  ];

  const benefits = [
    'Identify security vulnerabilities before hackers do',
    'Improve search engine rankings and organic traffic',
    'Enhance user experience and reduce bounce rates',
    'Ensure compliance with accessibility standards',
    'Get actionable recommendations, not just problems',
    'Comprehensive reports with priority-based fixes'
  ];

  const stats = [
    { label: 'Websites Audited', value: '10,000+' },
    { label: 'Security Issues Found', value: '50,000+' },
    { label: 'Performance Improvements', value: '85%' },
    { label: 'Average Score Increase', value: '+32 points' }
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-primary-50 via-white to-purple-50 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
              Complete Website
              <span className="text-gradient"> Digital Health</span> Check
            </h1>
            <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
              Comprehensive auditing platform that evaluates your website for security vulnerabilities, 
              performance bottlenecks, SEO issues, and accessibility compliance. Get actionable insights 
              to improve your digital presence.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-12">
              <Link 
                to="/audit" 
                className="btn btn-primary text-lg px-8 py-3 flex items-center space-x-2 group"
              >
                <span>Start Free Audit</span>
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>
              <button className="btn btn-secondary text-lg px-8 py-3">
                View Sample Report
              </button>
            </div>

            {/* Trust indicators */}
            <div className="flex flex-wrap justify-center items-center gap-8 text-sm text-gray-500">
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-4 h-4 text-green-500" />
                <span>Free to use</span>
              </div>
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-4 h-4 text-green-500" />
                <span>No registration required</span>
              </div>
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-4 h-4 text-green-500" />
                <span>Instant results</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Four Essential Audits in One Platform
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Our comprehensive analysis covers all critical aspects of your website's health, 
              providing you with a complete picture of areas that need improvement.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="card hover:shadow-lg transition-all duration-300 group">
                <div className={`w-12 h-12 ${feature.bgColor} rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
                  <feature.icon className={`w-6 h-6 ${feature.color}`} />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">
                  {feature.title}
                </h3>
                <p className="text-gray-600 leading-relaxed">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
                Why Choose SitePulse?
              </h2>
              <p className="text-lg text-gray-600 mb-8">
                Don't let hidden issues hurt your website's performance, security, or user experience. 
                Our comprehensive audit identifies problems and provides clear, actionable solutions.
              </p>
              
              <div className="space-y-4">
                {benefits.map((benefit, index) => (
                  <div key={index} className="flex items-start space-x-3">
                    <CheckCircle className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
                    <span className="text-gray-700">{benefit}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="relative">
              <div className="bg-white rounded-2xl shadow-xl p-8">
                <div className="text-center mb-6">
                  <div className="w-16 h-16 bg-gradient-to-r from-primary-600 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
                    <TrendingUp className="w-8 h-8 text-white" />
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900">Sample Report</h3>
                  <p className="text-gray-600">See what you'll get</p>
                </div>

                <div className="space-y-4">
                  <div className="flex justify-between items-center p-3 bg-red-50 rounded-lg">
                    <span className="text-red-700 font-medium">Security Score</span>
                    <span className="text-red-600 font-bold">45/100</span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-yellow-50 rounded-lg">
                    <span className="text-yellow-700 font-medium">Performance</span>
                    <span className="text-yellow-600 font-bold">67/100</span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-blue-50 rounded-lg">
                    <span className="text-blue-700 font-medium">SEO Score</span>
                    <span className="text-blue-600 font-bold">82/100</span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
                    <span className="text-green-700 font-medium">Accessibility</span>
                    <span className="text-green-600 font-bold">91/100</span>
                  </div>
                </div>

                <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-600 text-center">
                    + Detailed recommendations for each issue
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-3xl md:text-4xl font-bold text-primary-600 mb-2">
                  {stat.value}
                </div>
                <div className="text-gray-600 font-medium">
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-primary-600 to-purple-600">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
            Ready to Improve Your Website?
          </h2>
          <p className="text-xl text-primary-100 mb-8">
            Get your comprehensive website audit report in minutes. 
            Identify issues, get solutions, and boost your digital performance.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link 
              to="/audit" 
              className="bg-white text-primary-600 hover:bg-gray-100 px-8 py-4 rounded-lg font-semibold text-lg transition-colors flex items-center justify-center space-x-2 group"
            >
              <Globe className="w-5 h-5" />
              <span>Audit My Website</span>
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};

export default HomePage;
