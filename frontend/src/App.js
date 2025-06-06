// frontend/src/App.js
import React, { useState, useCallback } from 'react';
import FileUpload from './components/FileUpload';
import MindMapDisplay from './components/MindMapDisplay';
import QnAInterface from './components/QnAInterface';
import './App.css'; // Ensure your CSS is imported

function App() {
  const [mindMapData, setMindMapData] = useState(null);
  const [currentDocId, setCurrentDocId] = useState(null);
  const [isLoading, setIsLoading] = useState(false); // This is the actual loading state
  const [error, setError] = useState('');

  const handleFileUploadSuccess = useCallback((data) => {
    console.log("File upload success, received data:", data);
    setMindMapData(data.mind_map_data);
    setCurrentDocId(data.doc_id);
    setError('');
    setIsLoading(false);
  }, []);

  const handleFileUploadError = useCallback((errorMessage) => {
    setError(errorMessage);
    setMindMapData(null);
    setCurrentDocId(null);
    setIsLoading(false);
  }, []);

  // This function is correctly passed as 'onSetLoading' or similar
  // to allow FileUpload to trigger loading state changes.
  // Let's rename it in the prop for clarity.
  const handleSetLoading = useCallback((loadingStatus) => {
    setIsLoading(loadingStatus);
  }, []);


  return (
    <div className="App">
      <header className="App-header">
        <h1>CogniMap Studio 🧠</h1>
      </header>
      <main className="App-main">
        <div className="controls-section">
          <FileUpload 
            onUploadSuccess={handleFileUploadSuccess}
            onUploadError={handleFileUploadError}
            // Pass the function to SET loading state
            onSetLoading={handleSetLoading} 
            // ALSO pass the CURRENT loading state for the button
            isProcessing={isLoading} 
          />
           {error && <p className="error-message">Error: {error}</p>}
           {/* This loading message in App.js is fine */}
           {isLoading && <p className="loading-message">Processing your document, please wait...</p>}
        </div>

        <div className="content-section">
          <div className="mindmap-container">
            <h2>Mind Map</h2>
            {mindMapData ? (
              <MindMapDisplay mindMapData={mindMapData} docId={currentDocId} />
            ) : (
              !isLoading && <p>Upload a document to generate a mind map.</p>
            )}
          </div>
          <div className="qna-container">
            <h2>Ask Questions</h2>
            {currentDocId ? (
              <QnAInterface docId={currentDocId} />
            ) : (
              <p>Upload and process a document to enable Q&A.</p>
            )}
          </div>
        </div>
      </main>
      <footer className="App-footer">
        <p>CogniMap Studio MVP - Helping you learn better!</p>
      </footer>
    </div>
  );
}

export default App;