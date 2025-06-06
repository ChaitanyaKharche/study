import React, { useState } from 'react';
import axios from 'axios';

const API_BASE_URL = '/api';

function QnAInterface({ docId }) {
  const [query, setQuery] = useState('');
  const [answer, setAnswer] = useState('');
  const [sources, setSources] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmitQuery = async (event) => {
    event.preventDefault();
    if (!query.trim()) {
      setError('Please enter a query.');
      return;
    }
    setIsLoading(true);
    setError('');
    setAnswer('');
    setSources([]);

    try {
      const response = await axios.post(`${API_BASE_URL}/query/${docId}`, { query });
      setAnswer(response.data.answer);
      setSources(response.data.sources || []); // Assuming sources are returned as an array of strings
    } catch (err) {
      let errorMessage = 'Failed to get answer. Check console for details.';
       if (err.response && err.response.data && err.response.data.error) {
        errorMessage = err.response.data.error;
      } else if (err.message) {
        errorMessage = err.message;
      }
      setError(errorMessage);
      console.error("Query error:", err.response ? err.response.data : err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmitQuery}>
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={`Ask a question about document: ${docId}`}
          rows="3"
          style={{ width: '90%', marginBottom: '10px' }}
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading || !docId}>
          {isLoading ? 'Asking...' : 'Ask'}
        </button>
      </form>
      {error && <p style={{ color: 'red' }}>Error: {error}</p>}
      {answer && (
        <div style={{ marginTop: '20px', textAlign: 'left', padding: '10px', border: '1px solid #eee' }}>
          <h4>Answer:</h4>
          <p>{answer}</p>
          {sources.length > 0 && (
            <div>
              <h5>Sources:</h5>
              <ul>
                {sources.map((source, index) => (
                  <li key={index} style={{ fontSize: '0.9em', color: '#555', marginBottom: '5px' }}>
                    {source.substring(0,150)}... {/* Display a snippet */}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default QnAInterface;