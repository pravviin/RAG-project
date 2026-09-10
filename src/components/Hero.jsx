import React from 'react';
import { ArrowRight, FileText, Zap, Lock } from 'lucide-react';
import './Hero.css';

const Hero = ({ onStart }) => {
  return (
    <div className="hero-container animate-fade-in">
      <nav className="hero-nav">
        <div className="logo">
          <FileText size={24} className="text-accent" />
          <span>Local PDF Editor</span>
        </div>
        <button className="btn-secondary" onClick={onStart}>
          Enter Workspace
        </button>
      </nav>

      <main className="hero-main">
        <div className="hero-content">
          <div className="badge animate-fade-in-delayed">✨ Fully Local. Zero Cloud.</div>
          <h1 className="hero-heading animate-fade-in-delayed" style={{ animationDelay: '0.2s' }}>
            Edit Documents with <br />
            <span className="text-gradient">Natural Language.</span>
          </h1>
          <p className="hero-description animate-fade-in-delayed" style={{ animationDelay: '0.4s' }}>
            Upload a PDF, describe what you want changed, and let our offline AI Copilot rewrite the entire document instantly. Fast, secure, and purely magical.
          </p>
          
          <div className="hero-actions animate-fade-in-delayed" style={{ animationDelay: '0.6s' }}>
            <button className="btn-primary hero-btn" onClick={onStart}>
              Start Editing Now
              <ArrowRight size={20} />
            </button>
          </div>

          <div className="features-grid animate-fade-in-delayed" style={{ animationDelay: '0.8s' }}>
            <div className="feature-card glass-panel">
              <div className="feature-icon"><Lock size={24} /></div>
              <h3>100% Offline</h3>
              <p>Your documents never leave your machine.</p>
            </div>
            <div className="feature-card glass-panel">
              <div className="feature-icon"><Zap size={24} /></div>
              <h3>Instant Edits</h3>
              <p>Powered by local LLMs via Ollama.</p>
            </div>
            <div className="feature-card glass-panel">
              <div className="feature-icon"><FileText size={24} /></div>
              <h3>Native .docx</h3>
              <p>Download ready-to-use Word documents.</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Hero;
