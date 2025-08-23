import React from 'react';
import { Shield, Zap, Search, Eye, Users, Target, Award, CheckCircle } from 'lucide-react';

const AboutPage = () => {
  const features = [
    {
      icon: Shield,
      title: 'Security First',
      description: 'Comprehensive vulnerability scanning including SQL injection, XSS, SSL/TLS configuration, and security headers analysis to protect your website and users.',
      color: 'text-red-500',
      bgColor: 'bg-red-50'
    },
    {
      icon: Zap,
      title: 'Performance Optimization',
      description: 'Detailed performance analysis with Core Web Vitals, load times, and resource optimization recommendations to improve user experience.',
      color: 'text-yellow-500',
      bgColor: 'bg-yellow-50'
    },
    {
      icon: Search,
      title: 'SEO Excellence',
      description: 'Complete SEO audit covering meta tags, structured data, content optimization, and search engine visibility factors to boost rankings.',
      color: 'text-blue-500',
      bgColor: 'bg-blue-50'
    },
    {
      icon: Eye,
      title: 'Accessibility Compliance',
      description: 'WCAG compliance testing for images, forms, navigation, color contrast, and inclusive design principles to reach all users.',
      color: 'text-green-500',
      bgColor: 'bg-green-50'
    }
  ];

  const stats = [
    { number: '10,000+', label: 'Websites Audited' },
    { number: '50,000+', label: 'Issues Identified' },
    { number: '85%', label: 'Performance Improvement' },
    { number: '24/7', label: 'Available' }
  ];

  const team = [
    {
      name: 'Security Analysis Engine',
      role: 'Vulnerability Detection',
      description: 'Advanced scanning algorithms that identify security weaknesses and provide actionable remediation steps.'
    },
    {
      name: 'Performance Monitor',
      role: 'Speed Optimization',
      description: 'Real-time performance analysis with Core Web Vitals measurement and optimization recommendations.'
    },
    {
      name: 'SEO Analyzer',
      role: 'Search Optimization',
      description: 'Comprehensive SEO audit engine that evaluates on-page factors and technical SEO elements.'
    },
    {
      name: 'Accessibility Checker',
      role: 'WCAG Compliance',
      description: 'Automated accessibility testing to ensure your website is usable by everyone, including users with disabilities.'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-primary-50 via-white to-purple-50 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto">
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
              About <span className="text-gradient">SitePulse</span>
            </h1>
            <p className="text-xl text-gray-600 mb-8">
              We're on a mission to make the web safer, faster, and more accessible for everyone. 
              Our comprehensive auditing platform helps website owners identify and fix critical issues 
              that impact security, performance, SEO, and accessibility.
            </p>
            <div className="flex justify-center">
              <div className="flex items-center space-x-2 bg-white px-6 py-3 rounded-full shadow-sm">
                <Award className="w-5 h-5 text-primary-600" />
                <span className="text-gray-700 font-medium">Trusted by 10,000+ websites</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Mission Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
                Our Mission
              </h2>
              <p className="text-lg text-gray-600 mb-6">
                In today's digital world, websites face numerous challenges: security threats, 
                performance issues, poor search visibility, and accessibility barriers. Many website 
                owners struggle to identify these problems, let alone fix them.
              </p>
              <p className="text-lg text-gray-600 mb-6">
                SitePulse was created to bridge this gap. We provide comprehensive, automated 
                analysis that gives you a clear picture of your website's health and actionable 
                steps to improve it.
              </p>
              <div className="space-y-3">
                <div className="flex items-center space-x-3">
                  <CheckCircle className="w-5 h-5 text-green-500" />
                  <span className="text-gray-700">Identify hidden security vulnerabilities</span>
                </div>
                <div className="flex items-center space-x-3">
                  <CheckCircle className="w-5 h-5 text-green-500" />
                  <span className="text-gray-700">Optimize performance and user experience</span>
                </div>
                <div className="flex items-center space-x-3">
                  <CheckCircle className="w-5 h-5 text-green-500" />
                  <span className="text-gray-700">Improve search engine visibility</span>
                </div>
                <div className="flex items-center space-x-3">
                  <CheckCircle className="w-5 h-5 text-green-500" />
                  <span className="text-gray-700">Ensure accessibility for all users</span>
                </div>
              </div>
            </div>
            <div className="relative">
              <div className="bg-gradient-to-r from-primary-500 to-purple-600 rounded-2xl p-8 text-white">
                <h3 className="text-2xl font-bold mb-4">Why It Matters</h3>
                <div className="space-y-4">
                  <div className="flex items-start space-x-3">
                    <Target className="w-6 h-6 mt-1 flex-shrink-0" />
                    <div>
                      <h4 className="font-semibold">Security Breaches</h4>
                      <p className="text-primary-100">43% of cyberattacks target small businesses</p>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3">
                    <Zap className="w-6 h-6 mt-1 flex-shrink-0" />
                    <div>
                      <h4 className="font-semibold">Page Speed Impact</h4>
                      <p className="text-primary-100">1 second delay reduces conversions by 7%</p>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3">
                    <Users className="w-6 h-6 mt-1 flex-shrink-0" />
                    <div>
                      <h4 className="font-semibold">Accessibility</h4>
                      <p className="text-primary-100">15% of the global population has a disability</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Comprehensive Analysis
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Our platform combines multiple specialized analysis engines to give you 
              a complete picture of your website's health and performance.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="card hover:shadow-lg transition-all duration-300">
                <div className="flex items-start space-x-4">
                  <div className={`${feature.bgColor} p-3 rounded-lg flex-shrink-0`}>
                    <feature.icon className={`w-6 h-6 ${feature.color}`} />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-3">
                      {feature.title}
                    </h3>
                    <p className="text-gray-600 leading-relaxed">
                      {feature.description}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Trusted by Thousands
            </h2>
            <p className="text-lg text-gray-600">
              Join the growing community of website owners who trust SitePulse
            </p>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-4xl md:text-5xl font-bold text-primary-600 mb-2">
                  {stat.number}
                </div>
                <div className="text-gray-600 font-medium">
                  {stat.label}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Technology Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
              Our Analysis Engines
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Behind SitePulse are sophisticated analysis engines, each specialized 
              in a specific aspect of website health and optimization.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {team.map((member, index) => (
              <div key={index} className="card text-center hover:shadow-lg transition-all duration-300">
                <div className="w-16 h-16 bg-gradient-to-r from-primary-600 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-white font-bold text-lg">
                    {member.name.split(' ').map(word => word[0]).join('').slice(0, 2)}
                  </span>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {member.name}
                </h3>
                <p className="text-primary-600 font-medium mb-3">
                  {member.role}
                </p>
                <p className="text-gray-600">
                  {member.description}
                </p>
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
            Get started with a free comprehensive audit and discover how to make 
            your website more secure, faster, and accessible.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a 
              href="/audit" 
              className="bg-white text-primary-600 hover:bg-gray-100 px-8 py-4 rounded-lg font-semibold text-lg transition-colors"
            >
              Start Free Audit
            </a>
            <a 
              href="#contact" 
              className="border-2 border-white text-white hover:bg-white hover:text-primary-600 px-8 py-4 rounded-lg font-semibold text-lg transition-colors"
            >
              Contact Us
            </a>
          </div>
        </div>
      </section>
    </div>
  );
};

export default AboutPage;
