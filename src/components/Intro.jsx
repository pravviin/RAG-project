import React from 'react';
import { FileEdit } from 'lucide-react';
import './Intro.css';

const Intro = () => {
  return (
    <div className="intro-container">
      <div className="intro-content">
        <div className="logo-wrapper animate-pulse-glow">
          <FileEdit size={64} className="intro-icon" />
        </div>
        <h1 className="intro-title animate-fade-in-delayed">
          Local <span className="text-gradient">PDF Copilot</span>
        </h1>
        <p className="intro-subtitle animate-fade-in-delayed" style={{ animationDelay: '0.6s' }}>
          Your offline AI document editor.
        </p>
      </div>
    </div>
  );
};

export default Intro;
