import React, { useState } from 'react';
import axios from 'axios';
import { UploadCloud, FileText, Wand2, Download, AlertTriangle, ChevronRight, CheckCircle2 } from 'lucide-react';
import './PdfEditor.css';

const API_BASE = 'http://localhost:8000/api';

const PdfEditor = () => {
  const [file, setFile] = useState(null);
  const [originalText, setOriginalText] = useState('');
  const [instruction, setInstruction] = useState('');
  const [revisedText, setRevisedText] = useState('');
  const [diff, setDiff] = useState('');
  const [warning, setWarning] = useState('');
  
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState('');
  const [activeTab, setActiveTab] = useState('diff'); // 'diff' or 'full'

  const handleFileUpload = async (e) => {
    const uploadedFile = e.target.files[0];
    if (!uploadedFile) return;

    setFile(uploadedFile);
    setLoading(true);
    setStatus('Reading document...');
    setRevisedText('');
    setDiff('');
    setWarning('');

    const formData = new FormData();
    formData.append('file', uploadedFile);

    try {
      const res = await axios.post(`${API_BASE}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setOriginalText(res.data.original_text);
      if (res.data.word_count > res.data.max_words_safe) {
        setWarning(`Document is large (${res.data.word_count} words). Results might be less accurate.`);
      }
    } catch (err) {
      alert('Error uploading document: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
      setStatus('');
    }
  };

  const handleEdit = async () => {
    if (!instruction.trim() || !originalText) return;
    
    setLoading(true);
    setStatus('Applying edits with local AI...');
    setWarning('');
    
    try {
      const res = await axios.post(`${API_BASE}/edit`, {
        original_text: originalText,
        instruction: instruction
      });
      setRevisedText(res.data.revised_text);
      setDiff(res.data.diff);
      if (res.data.warning) setWarning(res.data.warning);
    } catch (err) {
      alert('Error applying edit: ' + (err.response?.data?.detail || err.message));
    } finally {
      setLoading(false);
      setStatus('');
    }
  };

  const handleDownload = async () => {
    if (!revisedText) return;
    
    setStatus('Preparing download...');
    try {
      const res = await axios.post(`${API_BASE}/download`, {
        revised_text: revisedText
      }, { responseType: 'blob' });
      
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `revised_${file?.name ? file.name.replace(/\.[^/.]+$/, "") : 'document'}.docx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      alert('Error downloading: ' + err.message);
    } finally {
      setStatus('');
    }
  };

  return (
    <div className="editor-layout animate-fade-in">
      {/* Sidebar */}
      <aside className="editor-sidebar glass-panel">
        <div className="sidebar-header">
          <FileText className="text-accent" />
          <h2>Workspace</h2>
        </div>
        
        <div className="sidebar-section">
          <h3>1. Upload Document</h3>
          <label className="upload-dropzone">
            <input type="file" accept=".pdf,.txt" onChange={handleFileUpload} hidden />
            <UploadCloud size={32} className="mb-2 text-secondary" />
            <span>{file ? file.name : "Click or drag PDF/TXT"}</span>
          </label>
        </div>

        <div className="sidebar-section" style={{ opacity: originalText ? 1 : 0.5 }}>
          <h3>2. AI Instruction</h3>
          <textarea 
            className="input-field instruction-input"
            placeholder="e.g. Make the tone more professional and fix all grammatical errors..."
            value={instruction}
            onChange={(e) => setInstruction(e.target.value)}
            disabled={!originalText || loading}
          ></textarea>
          <button 
            className="btn-primary w-full mt-3" 
            onClick={handleEdit}
            disabled={!originalText || !instruction.trim() || loading}
          >
            {loading && status.includes('Applying') ? (
              <span className="spinner-small"></span>
            ) : (
              <Wand2 size={18} />
            )}
            Apply Edit
          </button>
        </div>

        {revisedText && (
          <div className="sidebar-section animate-fade-in">
            <h3>3. Export</h3>
            <button className="btn-secondary w-full text-success export-btn" onClick={handleDownload}>
              <Download size={18} />
              Download .docx
            </button>
          </div>
        )}
      </aside>

      {/* Main Content */}
      <main className="editor-main">
        {loading && (
          <div className="loading-overlay glass-panel animate-fade-in">
            <div className="spinner"></div>
            <p>{status}</p>
          </div>
        )}

        {warning && (
          <div className="warning-banner glass-panel">
            <AlertTriangle className="text-warning" />
            <p>{warning}</p>
          </div>
        )}

        {!originalText && !loading ? (
          <div className="empty-state">
            <FileText size={64} className="text-secondary opacity-50" />
            <h2>No Document Loaded</h2>
            <p>Upload a PDF to start editing with natural language.</p>
          </div>
        ) : (
          <div className="editor-content-area glass-panel">
            {revisedText ? (
              <div className="results-container">
                <div className="tabs">
                  <button 
                    className={`tab ${activeTab === 'diff' ? 'active' : ''}`}
                    onClick={() => setActiveTab('diff')}
                  >
                    Differences (Diff)
                  </button>
                  <button 
                    className={`tab ${activeTab === 'full' ? 'active' : ''}`}
                    onClick={() => setActiveTab('full')}
                  >
                    Full Revised Text
                  </button>
                </div>
                
                <div className="tab-content">
                  {activeTab === 'diff' ? (
                    diff.trim() ? (
                      <pre className="diff-view">{diff}</pre>
                    ) : (
                      <div className="flex-center h-full text-secondary">
                        <CheckCircle2 className="mr-2" /> No differences detected.
                      </div>
                    )
                  ) : (
                    <textarea 
                      className="full-text-view input-field"
                      readOnly
                      value={revisedText}
                    ></textarea>
                  )}
                </div>
              </div>
            ) : (
              <div className="original-text-container">
                <h3>Original Document Content</h3>
                <textarea 
                  className="full-text-view input-field opacity-70"
                  readOnly
                  value={originalText}
                ></textarea>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
};

export default PdfEditor;
