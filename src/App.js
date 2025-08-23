import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuditProvider } from './contexts/AuditContext';
import Header from './components/Header';
import Footer from './components/Footer';
import HomePage from './pages/HomePage';
import AuditPage from './pages/AuditPage';
import ReportPage from './pages/ReportPage';
import AboutPage from './pages/AboutPage';

function App() {
  return (
    <AuditProvider>
      <Router>
        <div className="min-h-screen flex flex-col bg-gray-50">
          <Header />
          <main className="flex-1">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/audit" element={<AuditPage />} />
              <Route path="/report/:reportId" element={<ReportPage />} />
              <Route path="/about" element={<AboutPage />} />
            </Routes>
          </main>
          <Footer />
        </div>
      </Router>
    </AuditProvider>
  );
}

export default App;
