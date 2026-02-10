import React, { useEffect, useState } from 'react';
import { QueryBuilder as RQB, RuleGroupType } from 'react-querybuilder';
import { TableMetadata } from '../types';
import 'react-querybuilder/dist/query-builder.css';
import './QueryBuilderComponent.css';

interface Props {
  open: boolean;
  onClose: () => void;
  onSave: (sub: { query: RuleGroupType; table_name: string; select_field?: string; select_fields?: string[] }) => void;
  tables: TableMetadata[];
  initial?: { query?: RuleGroupType; table_name?: string; select_field?: string; select_fields?: string[] } | null;
}

const SubqueryModal: React.FC<Props> = ({ open, onClose, onSave, tables, initial = null }) => {
  const [tableName, setTableName] = useState<string>(initial?.table_name || (tables?.[0]?.name || ''));
  const [selectField, setSelectField] = useState<string | undefined>(initial?.select_field || undefined);
  const [selectFields, setSelectFields] = useState<string[]>(initial?.select_fields || []);
  const [subquery, setSubquery] = useState<RuleGroupType>(initial?.query || { combinator: 'and', rules: [] });

  useEffect(() => {
    if (open) {
      setTableName(initial?.table_name || (tables?.[0]?.name || ''));
      setSelectField(initial?.select_field || undefined);
      setSelectFields(initial?.select_fields || []);
      setSubquery(initial?.query || { combinator: 'and', rules: [] });
    }
  }, [open, initial, tables]);

  const fieldsForTable = tables.find((t) => t.name === tableName)?.fields || [];

  if (!open) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()} style={{ maxWidth: 900 }}>
        <h2>Configure Subquery</h2>
        <div className="form-group" style={{ display: 'flex', gap: 12 }}>
          <div style={{ flex: 1 }}>
            <label>From (table)</label>
            <select value={tableName} onChange={(e) => setTableName(e.target.value)}>
              {tables.map((t) => <option key={t.name} value={t.name}>{t.label}</option>)}
            </select>
          </div>
          <div style={{ flex: 1 }}>
            <label>Select fields (ctrl+click to multi-select)</label>
            <select multiple value={selectFields} onChange={(e) => setSelectFields(Array.from(e.target.selectedOptions).map(o => o.value))} style={{ minHeight: 90 }}>
              {fieldsForTable.map((f) => <option key={f.name} value={f.name}>{f.label || f.name}</option>)}
            </select>
          </div>
        </div>

        <div style={{ marginTop: 12 }}>
          <label style={{ fontWeight: 600 }}>WHERE</label>
          <div className="subquery-builder">
            <RQB fields={fieldsForTable as any} query={subquery} onQueryChange={setSubquery} />
          </div>
        </div>

        <div className="modal-buttons">
          <button className="btn btn-primary" onClick={() => { onSave({ query: subquery, table_name: tableName, select_field: selectField, select_fields: selectFields.length ? selectFields : undefined }); onClose(); }}>Attach</button>
          <button className="btn btn-outline" onClick={onClose}>Cancel</button>
        </div>
      </div>
    </div>
  );
};

export default SubqueryModal;
