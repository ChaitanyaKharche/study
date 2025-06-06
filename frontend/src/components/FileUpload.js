// frontend/src/components/FileUpload.js
import React, { useState } from 'react';
import axios from 'axios';

const API_BASE_URL = '/api';

// Renamed 'onLoading' prop to 'onSetLoading' for clarity, and added 'isProcessing'
function FileUpload({ onUploadSuccess, onUploadError, onSetLoading, isProcessing }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [message, setMessage] = useState(''); // Local message for this component

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
    setMessage(''); // Clear local message
    onUploadError(''); // Clear error in App.js
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!selectedFile) {
      setMessage('Please select a file first.');
      onUploadError('Please select a file first.');
      return;
    }

    onSetLoading(true); // Signal to App.js that processing has started
    setMessage('Uploading and processing...'); // Local feedback
    onUploadError('');

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await axios.post(`${API_BASE_URL}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      // Use a success message that doesn't conflict with App.js's loading message
      setMessage(`Document processed: ${response.data.filename}`); 
      onUploadSuccess(response.data);
    } catch (err) {
      let errorMessage = 'File upload failed.';
      if (err.response && err.response.data && err.response.data.error) {
        errorMessage = err.response.data.error;
      } else if (err.message) {
        errorMessage = err.message;
      }
      setMessage(errorMessage); // Show error locally
      onUploadError(errorMessage); // Also signal error to App.js
      console.error("Upload error:", err.response ? err.response.data : err);
    } finally {
      onSetLoading(false); // Signal to App.js that processing has ended (success or fail)
      // Don't clear message here, let it persist until next action
    }
  };

  return (
    <div>
      <h3>Upload Document (PDF or TXT)</h3>
      <form onSubmit={handleSubmit}>
        <input type="file" onChange={handleFileChange} accept=".pdf,.txt" disabled={isProcessing} />
        <button type="submit" disabled={!selectedFile || isProcessing}>
          {isProcessing ? 'Processing...' : 'Upload & Process'}
        </button>
      </form>
      {/* Display local messages (like "select a file" or "uploading...") from this component */}
      {message && !isProcessing && <p>{message}</p>}
    </div>
  );
}

export default FileUpload;