import React, { useState, useEffect, useCallback } from 'react';
import { QueryBuilder as RQB, RuleGroupType, Field, formatQuery } from 'react-querybuilder';
import 'react-querybuilder/dist/query-builder.css';
import { queryService } from '../services/api';
import { TableMetadata, QueryExecuteResponse } from '../types';
import './QueryBuilderComponent.css';
import SavedQueries from './SavedQueries';
import InlineSubqueryEditor from './InlineSubqueryEditor';

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

  const updateFieldsForTable = useCallback(() => {
    const table = tables.find((t) => t.name === selectedTable);
    if (table) {
      const mappedFields = table.fields.map((field) => {
        const ops: string[] = Array.isArray((field as any).operators) ? [...((field as any).operators)] : [];
        if (!ops.includes('in')) ops.push('in');
        if (!ops.includes('notIn')) ops.push('notIn');

        const mappedOps = ops.map((op) => {
          if (op === 'in') return { name: 'in', label: 'IN (subquery/list)' } as any;
          if (op === 'notIn') return { name: 'notIn', label: 'NOT IN (subquery/list)' } as any;
          return { name: op, label: op } as any;
        });

        return { ...field, operators: mappedOps } as any;
      });
      setFields(mappedFields as any);
    }
  }, [selectedTable, tables]);

  const loadFieldsForTable = useCallback(async (tableName: string) => {
    try {
      const table = await queryService.getFieldsByTable(tableName);
      if (table && table.fields) {
        const mappedFields = table.fields.map((field: any) => {
          const ops: string[] = Array.isArray(field.operators) ? [...field.operators] : [];
          if (!ops.includes('in')) ops.push('in');
          if (!ops.includes('notIn')) ops.push('notIn');

          const mappedOps = ops.map((op) => {
            if (op === 'in') return { name: 'in', label: 'IN (subquery/list)' } as any;
            if (op === 'notIn') return { name: 'notIn', label: 'NOT IN (subquery/list)' } as any;
            return { name: op, label: op } as any;
          });

          return { ...field, operators: mappedOps } as any;
        });

        setFields(mappedFields as any);
      }
    } catch (err) {
      console.error('Failed to load table fields', err);
    }
  }, []);

  // Update fields when table changes (declared after helpers)
  useEffect(() => {
    updateFieldsForTable();
    // also fetch fresh table fields from API for selected table
    loadFieldsForTable(selectedTable);
  }, [selectedTable, tables, updateFieldsForTable, loadFieldsForTable]);

  // Custom value editor to open modal for IN/NOT IN subqueries
  const CustomValueEditor = (props: any) => {
    const { value, handleOnChange, operator, rule } = props;

    if (operator === 'in' || operator === 'notIn') {
      // support subquery stored either in rule.value or rule.subquery
      const existing = value && typeof value === 'object' ? value : (rule && rule.subquery ? rule.subquery : undefined);
      const val = existing || {};

      return (
        <div style={{ width: '100%', minWidth: 300 }}>
          <InlineSubqueryEditor
            value={val}
            onChange={handleOnChange}
            tables={tables}
          />
        </div>
      );
    }

    // default
    return (
      <input type="text" value={value ?? ''} onChange={(e) => handleOnChange(e.target.value)} />
    );
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
        <RQB fields={fields} query={query} onQueryChange={setQuery} controlElements={{ valueEditor: CustomValueEditor as any }} />
      </div>

      <div style={{ marginTop: 18 }}>
        <SavedQueries onLoadQuery={(q) => {
          try {
            const parsed = JSON.parse(q.query_json);
            setSelectedTable(q.table_name);
            setQuery(parsed as any);
            setSqlQuery(q.sql_query || '');
            // ensure fields are loaded for the table
            loadFieldsForTable(q.table_name);
          } catch (err) {
            alert('Failed to load saved query');
            console.error(err);
          }
        }} />
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
