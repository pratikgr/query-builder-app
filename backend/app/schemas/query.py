from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Any, Dict
from datetime import datetime


# Query Builder Schemas
class QueryRule(BaseModel):
    """Single query rule"""
    field: str
    operator: str
    value: Any
    
    
class QueryGroup(BaseModel):
    """Query group with combinator"""
    combinator: str = Field(..., description="AND or OR")
    rules: List[Any]  # Can contain QueryRule or nested QueryGroup
    not_: Optional[bool] = Field(False, alias="not")
    
    model_config = ConfigDict(populate_by_name=True)


class QueryExecuteRequest(BaseModel):
    """Request to execute a query"""
    query: QueryGroup
    table_name: str = Field(..., description="Table to query against")
    limit: Optional[int] = Field(100, description="Maximum rows to return")


class QueryExecuteResponse(BaseModel):
    """Response from query execution"""
    success: bool
    data: Optional[List[Dict[str, Any]]] = None
    sql_query: Optional[str] = None
    row_count: int = 0
    error: Optional[str] = None


class SavedQueryCreate(BaseModel):
    """Create a saved query"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    query_json: str
    sql_query: Optional[str] = None
    table_name: str


class SavedQueryUpdate(BaseModel):
    """Update a saved query"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    query_json: Optional[str] = None
    sql_query: Optional[str] = None


class SavedQueryResponse(BaseModel):
    """Saved query response"""
    id: int
    name: str
    description: Optional[str]
    query_json: str
    sql_query: Optional[str]
    table_name: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# Metadata Schemas
class FieldMetadata(BaseModel):
    """Field metadata for query builder"""
    name: str
    label: str
    type: str  # 'text', 'number', 'boolean', 'date', 'select'
    operators: Optional[List[str]] = None
    values: Optional[List[Any]] = None  # For select fields
    inputType: Optional[str] = None
    valueEditorType: Optional[str] = None
    defaultValue: Optional[Any] = None


class TableMetadata(BaseModel):
    """Table metadata"""
    name: str
    label: str
    fields: List[FieldMetadata]


class FieldsResponse(BaseModel):
    """Response containing available fields"""
    tables: List[TableMetadata]


# Generic Response
class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    detail: Optional[str] = None
