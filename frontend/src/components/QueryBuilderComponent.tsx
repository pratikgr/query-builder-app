import React, { useState, useEffect } from 'react';
import { QueryBuilder as RQB, RuleGroupType, Field, formatQuery } from 'react-querybuilder';
import 'react-querybuilder/dist/query-builder.css';
import { queryService } from '../services/api';
import { TableMetadata, QueryExecuteResponse } from '../types';
import './QueryBuilderComponent.css';

const QueryBuilderComponent: React.FC = () => {
  const [query, setQuery] = useState<RuleGroupType>({
    combinator: 'and',
    rules: [],
  });

  const [fields, setFields] = useState<Field[]>([]);
  const [tables, setTables] = useState<TableMetadata[]>([]);
  const [selectedTable, setSelectedTable] = useState<string>('users');
  const [results, setResults] = useState<any[]>([]);
  const [sqlQuery, setSqlQuery] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const [saveModalOpen, setSaveModalOpen] = useState<boolean>(false);
  const [queryName, setQueryName] = useState<string>('');
  const [queryDescription, setQueryDescription] = useState<string>('');

  // Load fields on component mount
  useEffect(() => {
    loadFields();
  }, []);

  // Update fields when table changes
  useEffect(() => {
    updateFieldsForTable();
  }, [selectedTable, tables]);

  const loadFields = async () => {
    try {
      const data = await queryService.getFields();
      setTables(data.tables);
      if (data.tables.length > 0) {
        setSelectedTable(data.tables[0].name);
      }
    } catch (err) {
      setError('Failed to load fields');
      console.error(err);
    }
  };

  const updateFieldsForTable = () => {
    const table = tables.find((t) => t.name === selectedTable);
    if (table) {
      // setFields(table.fields);
      const mappedFields = table.fields.map((field) => ({
        ...field,
        operators: field.operators
          ? field.operators.map((op) => ({name: op, label: op}))
          : undefined,
      }));
      setFields(mappedFields as any);
    }
  };

  const handleExecuteQuery = async () => {
    setLoading(true);
    setError('');
    setResults([]);
    setSqlQuery('');

    try {
      const response: QueryExecuteResponse = await queryService.executeQuery({
        query: query as any,
        table_name: selectedTable,
        limit: 100,
      });

      if (response.success) {
        setResults(response.data || []);
        setSqlQuery(response.sql_query || '');
      } else {
        setError(response.error || 'Query execution failed');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to execute query');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveQuery = async () => {
    if (!queryName.trim()) {
      alert('Please enter a query name');
      return;
    }

    try {
      await queryService.saveQuery({
        name: queryName,
        description: queryDescription,
        query_json: JSON.stringify(query),
        sql_query: formatQuery(query, 'sql'),
        table_name: selectedTable,
      });

      alert('Query saved successfully!');
      setSaveModalOpen(false);
      setQueryName('');
      setQueryDescription('');
    } catch (err: any) {
      alert('Failed to save query: ' + (err.response?.data?.detail || err.message));
    }
  };

  const renderResults = () => {
    if (results.length === 0) return null;

    const columns = Object.keys(results[0]);

    return (
      <div className="results-container">
        <h3>Results ({results.length} rows)</h3>
        <div className="table-container">
          <table className="results-table">
            <thead>
              <tr>
                {columns.map((col) => (
                  <th key={col}>{col}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {results.map((row, idx) => (
                <tr key={idx}>
                  {columns.map((col) => (
                    <td key={col}>{String(row[col] ?? '')}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  return (
    <div className="query-builder-container">
      <div className="header">
        <h1>Query Builder</h1>
        <p>Build and execute dynamic database queries</p>
      </div>

      <div className="controls">
        <div className="control-group">
          <label htmlFor="table-select">Select Table:</label>
          <select
            id="table-select"
            value={selectedTable}
            onChange={(e) => setSelectedTable(e.target.value)}
            className="table-select"
          >
            {tables.map((table) => (
              <option key={table.name} value={table.name}>
                {table.label}
              </option>
            ))}
          </select>
        </div>

        <div className="button-group">
          <button onClick={handleExecuteQuery} disabled={loading} className="btn btn-primary">
            {loading ? 'Executing...' : 'Execute Query'}
          </button>
          <button onClick={() => setSaveModalOpen(true)} className="btn btn-secondary">
            Save Query
          </button>
          <button
            onClick={() => setQuery({ combinator: 'and', rules: [] })}
            className="btn btn-outline"
          >
            Clear
          </button>
        </div>
      </div>

      <div className="query-builder-wrapper">
        <RQB fields={fields} query={query} onQueryChange={setQuery} />
      </div>

      {sqlQuery && (
        <div className="sql-preview">
          <h3>Generated SQL:</h3>
          <pre>{sqlQuery}</pre>
        </div>
      )}

      {error && (
        <div className="error-message">
          <strong>Error:</strong> {error}
        </div>
      )}

      {renderResults()}

      {saveModalOpen && (
        <div className="modal-overlay" onClick={() => setSaveModalOpen(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Save Query</h2>
            <div className="form-group">
              <label>Query Name *</label>
              <input
                type="text"
                value={queryName}
                onChange={(e) => setQueryName(e.target.value)}
                placeholder="Enter query name"
              />
            </div>
            <div className="form-group">
              <label>Description</label>
              <textarea
                value={queryDescription}
                onChange={(e) => setQueryDescription(e.target.value)}
                placeholder="Enter query description"
                rows={3}
              />
            </div>
            <div className="modal-buttons">
              <button onClick={handleSaveQuery} className="btn btn-primary">
                Save
              </button>
              <button onClick={() => setSaveModalOpen(false)} className="btn btn-outline">
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default QueryBuilderComponent;
