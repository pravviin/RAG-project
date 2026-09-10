import React, { useState, useEffect } from 'react';
import './index.css';
import Intro from './components/Intro';
import Hero from './components/Hero';
import PdfEditor from './components/PdfEditor';

function App() {
  const [appState, setAppState] = useState('intro'); // intro, hero, editor

  useEffect(() => {
    if (appState === 'intro') {
      const timer = setTimeout(() => {
        setAppState('hero');
      }, 4000); // Intro lasts for 4 seconds
      return () => clearTimeout(timer);
    }
  }, [appState]);

  return (
    <div className="app-container">
      {appState === 'intro' && <Intro />}
      {appState === 'hero' && <Hero onStart={() => setAppState('editor')} />}
      {appState === 'editor' && <PdfEditor />}
    </div>
  );
}

export default App;
