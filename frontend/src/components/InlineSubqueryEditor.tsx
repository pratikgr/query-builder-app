import React, { useState, useEffect } from 'react';
import { QueryBuilder as RQB, RuleGroupType } from 'react-querybuilder';
import { TableMetadata } from '../types';
import 'react-querybuilder/dist/query-builder.css';

interface Props {
  value: any;
  onChange: (val: any) => void;
  tables: TableMetadata[];
}

const InlineSubqueryEditor: React.FC<Props> = ({ value, onChange, tables }) => {
  const [expanded, setExpanded] = useState(false);
  const [tableName, setTableName] = useState<string>(value?.table_name || (tables?.[0]?.name || ''));
  const [selectField, setSelectField] = useState<string>(value?.select_field || '');
  const [selectFields, setSelectFields] = useState<string[]>(value?.select_fields || []);
  const [whereQuery, setWhereQuery] = useState<RuleGroupType>(
    value?.query || { combinator: 'and', rules: [] }
  );

  useEffect(() => {
    if (value) {
      setTableName(value.table_name || (tables?.[0]?.name || ''));
      setSelectField(value.select_field || '');
      setSelectFields(value.select_fields || []);
      setWhereQuery(value.query || { combinator: 'and', rules: [] });
    }
  }, [value, tables]);

  const handleSave = () => {
    const payload = {
      table_name: tableName,
      select_field: selectField || undefined,
      select_fields: selectFields.length > 0 ? selectFields : undefined,
      query: whereQuery,
    };
    onChange(payload);
    setExpanded(false);
  };

  const fieldsForTable = tables.find((t) => t.name === tableName)?.fields || [];
  
  // Map operators to format expected by react-querybuilder
  const mappedFields = fieldsForTable.map((field: any) => {
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

  const displayText = value?.table_name
    ? `${value.table_name} ${value.select_field ? `(${value.select_field})` : value.select_fields?.length > 0 ? `(${value.select_fields.join(', ')})` : ''}`
    : 'Configure...';

  return (
    <div style={{ border: '1px solid #ddd', borderRadius: 4, padding: 8 }}>
      <button
        className="btn btn-outline"
        onClick={() => setExpanded(!expanded)}
        style={{
          width: '100%',
          textAlign: 'left',
          padding: '8px 12px',
          fontSize: '14px',
        }}
      >
        {expanded ? '▼' : '▶'} Subquery: {displayText}
      </button>

      {expanded && (
        <div style={{ marginTop: 12, paddingTop: 12, borderTop: '1px solid #eee' }}>
          {/* FROM table selector */}
          <div style={{ marginBottom: 12 }}>
            <label style={{ display: 'block', fontWeight: 600, marginBottom: 4 }}>FROM Table</label>
            <select
              value={tableName}
              onChange={(e) => setTableName(e.target.value)}
              style={{ width: '100%', padding: '6px', borderRadius: 3, border: '1px solid #ccc' }}
            >
              {tables.map((t) => (
                <option key={t.name} value={t.name}>
                  {t.label}
                </option>
              ))}
            </select>
          </div>

          {/* SELECT field(s) */}
          <div style={{ marginBottom: 12 }}>
            <label style={{ display: 'block', fontWeight: 600, marginBottom: 4 }}>
              SELECT Fields (optional)
            </label>
            <select
              multiple
              value={selectFields}
              onChange={(e) => setSelectFields(Array.from(e.target.selectedOptions).map((o) => o.value))}
              style={{
                width: '100%',
                minHeight: 80,
                padding: '6px',
                borderRadius: 3,
                border: '1px solid #ccc',
              }}
            >
              {fieldsForTable.map((f) => (
                <option key={f.name} value={f.name}>
                  {f.label || f.name}
                </option>
              ))}
            </select>
            <small style={{ color: '#666', marginTop: 4, display: 'block' }}>
              Ctrl/Cmd+Click to multi-select. Leave empty to select all fields.
            </small>
          </div>

          {/* WHERE conditions */}
          <div style={{ marginBottom: 12 }}>
            <label style={{ display: 'block', fontWeight: 600, marginBottom: 6 }}>WHERE Conditions</label>
            <div
              style={{
                border: '1px solid #ccc',
                borderRadius: 3,
                padding: 8,
                backgroundColor: '#fafafa',
              }}
            >
              <RQB
                fields={mappedFields as any}
                query={whereQuery}
                onQueryChange={setWhereQuery}
              />
            </div>
          </div>

          {/* Save/Cancel buttons */}
          <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
            <button
              className="btn btn-primary"
              onClick={handleSave}
              style={{ padding: '6px 12px', fontSize: '14px' }}
            >
              Apply
            </button>
            <button
              className="btn btn-outline"
              onClick={() => setExpanded(false)}
              style={{ padding: '6px 12px', fontSize: '14px' }}
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default InlineSubqueryEditor;
