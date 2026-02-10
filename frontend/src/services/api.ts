import axios from 'axios';
import {
  FieldsResponse,
  QueryExecuteRequest,
  QueryExecuteResponse,
  SavedQuery,
  SavedQueryCreate,
} from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:4000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const queryService = {
  // Get available fields for query builder
  getFields: async (): Promise<FieldsResponse> => {
    const response = await api.get<FieldsResponse>('/metadata/fields');
    return response.data;
  },

  // Get available tables
  getTables: async (): Promise<any> => {
    const response = await api.get('/metadata/tables');
    return response.data;
  },

  // Get fields for all tables (convenience)
  getAllFields: async (): Promise<FieldsResponse> => {
    const response = await api.get<FieldsResponse>('/metadata/fields');
    return response.data;
  },

  // Get fields for a specific table by name
  getFieldsByTable: async (tableName: string): Promise<any> => {
    const all = await api.get<FieldsResponse>('/metadata/fields');
    const table = all.data.tables.find((t) => t.name === tableName);
    return table || { name: tableName, label: tableName, fields: [] };
  },

  // Execute a query
  executeQuery: async (request: QueryExecuteRequest): Promise<QueryExecuteResponse> => {
    const response = await api.post<QueryExecuteResponse>('/queries/execute', request);
    return response.data;
  },

  // Save a query
  saveQuery: async (query: SavedQueryCreate): Promise<SavedQuery> => {
    const response = await api.post<SavedQuery>('/queries/save', query);
    return response.data;
  },

  // Get all saved queries
  getSavedQueries: async (): Promise<SavedQuery[]> => {
    const response = await api.get<SavedQuery[]>('/queries/');
    return response.data;
  },

  // Get a specific saved query
  getSavedQuery: async (id: number): Promise<SavedQuery> => {
    const response = await api.get<SavedQuery>(`/queries/${id}`);
    return response.data;
  },

  // Delete a saved query
  deleteQuery: async (id: number): Promise<void> => {
    await api.delete(`/queries/${id}`);
  },
};

export default api;
