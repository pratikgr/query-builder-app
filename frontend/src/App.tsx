import React, { useState } from 'react';
import QueryBuilderComponent from './components/QueryBuilderComponent';
import SavedQueries from './components/SavedQueries';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState<'builder' | 'saved'>('builder');

  return (
    <div className="App">
      <nav className="navbar">
        <div className="navbar-brand">
          <h1>Query Builder App</h1>
        </div>
        <div className="navbar-tabs">
          <button
            className={`tab-button ${activeTab === 'builder' ? 'active' : ''}`}
            onClick={() => setActiveTab('builder')}
          >
            Query Builder
          </button>
          <button
            className={`tab-button ${activeTab === 'saved' ? 'active' : ''}`}
            onClick={() => setActiveTab('saved')}
          >
            Saved Queries
          </button>
        </div>
      </nav>

      <main className="main-content">
        {activeTab === 'builder' ? <QueryBuilderComponent /> : <SavedQueries />}
      </main>

      <footer className="footer">
        <p>
          Built with React, FastAPI, and SQLAlchemy | &copy; 2024 Query Builder App
        </p>
      </footer>
    </div>
  );
}

export default App;
