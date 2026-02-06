// Type definitions for the application

export interface Field {
  name: string;
  label: string;
  type?: string;
  inputType?: string;
  operators?: string[];
  values?: any[];
  valueEditorType?: string;
  defaultValue?: any;
}

export interface TableMetadata {
  name: string;
  label: string;
  fields: Field[];
}

export interface FieldsResponse {
  tables: TableMetadata[];
}

export interface QueryRule {
  field: string;
  operator: string;
  value: any;
}

export interface QueryGroup {
  combinator: string;
  rules: (QueryRule | QueryGroup)[];
  not?: boolean;
}

export interface QueryExecuteRequest {
  query: QueryGroup;
  table_name: string;
  limit?: number;
}

export interface QueryExecuteResponse {
  success: boolean;
  data?: any[];
  sql_query?: string;
  row_count: number;
  error?: string;
}

export interface SavedQuery {
  id: number;
  name: string;
  description?: string;
  query_json: string;
  sql_query?: string;
  table_name: string;
  created_at: string;
  updated_at: string;
}

export interface SavedQueryCreate {
  name: string;
  description?: string;
  query_json: string;
  sql_query?: string;
  table_name: string;
}
