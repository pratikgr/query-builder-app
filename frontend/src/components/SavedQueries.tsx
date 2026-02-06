import React, { useState, useEffect } from 'react';
import { queryService } from '../services/api';
import { SavedQuery } from '../types';
import './SavedQueries.css';

interface SavedQueriesProps {
  onLoadQuery?: (query: SavedQuery) => void;
}

const SavedQueries: React.FC<SavedQueriesProps> = ({ onLoadQuery }) => {
  const [queries, setQueries] = useState<SavedQuery[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    loadQueries();
  }, []);

  const loadQueries = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await queryService.getSavedQueries();
      setQueries(data);
    } catch (err) {
      setError('Failed to load saved queries');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Are you sure you want to delete this query?')) {
      return;
    }

    try {
      await queryService.deleteQuery(id);
      setQueries(queries.filter((q) => q.id !== id));
    } catch (err) {
      alert('Failed to delete query');
      console.error(err);
    }
  };

  if (loading) {
    return <div className="saved-queries-loading">Loading saved queries...</div>;
  }

  return (
    <div className="saved-queries-container">
      <div className="saved-queries-header">
        <h2>Saved Queries</h2>
        <button onClick={loadQueries} className="btn-refresh">
          Refresh
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {queries.length === 0 ? (
        <div className="no-queries">No saved queries yet. Create and save your first query!</div>
      ) : (
        <div className="queries-list">
          {queries.map((query) => (
            <div key={query.id} className="query-card">
              <div className="query-card-header">
                <h3>{query.name}</h3>
                <span className="query-table-badge">{query.table_name}</span>
              </div>
              {query.description && <p className="query-description">{query.description}</p>}
              <div className="query-meta">
                <span className="query-date">
                  Created: {new Date(query.created_at).toLocaleDateString()}
                </span>
              </div>
              <div className="query-actions">
                {onLoadQuery && (
                  <button onClick={() => onLoadQuery(query)} className="btn-load">
                    Load
                  </button>
                )}
                <button onClick={() => handleDelete(query.id)} className="btn-delete">
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SavedQueries;
