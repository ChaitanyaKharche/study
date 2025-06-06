import React from 'react';
import { createRoot } from 'react-dom/client'; // Import createRoot
import App from './App';
import './App.css'; // Assuming you might have an App.css or index.css here

// Get the root element
const container = document.getElementById('root');

// Create a root
const root = createRoot(container); // Use createRoot

// Initial render
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);