from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import json

from app.db.database import get_db
from app.db.models import SavedQuery
from app.schemas.query import (
    QueryExecuteRequest,
    QueryExecuteResponse,
    SavedQueryCreate,
    SavedQueryUpdate,
    SavedQueryResponse,
    MessageResponse
)
from app.core.query_service import QueryService

router = APIRouter()


@router.post("/execute", response_model=QueryExecuteResponse)
async def execute_query(
    request: QueryExecuteRequest,
    db: Session = Depends(get_db)
):
    """Execute a query against the database"""
    try:
        # Convert query to dict if needed
        query_dict = request.query.model_dump(by_alias=True)
        
        # Execute the query
        data, sql_query = QueryService.execute_query(
            db=db,
            query_group=query_dict,
            table_name=request.table_name,
            limit=request.limit or 100
        )
        
        return QueryExecuteResponse(
            success=True,
            data=data,
            sql_query=sql_query,
            row_count=len(data)
        )
    
    except ValueError as e:
        return QueryExecuteResponse(
            success=False,
            error=str(e)
        )
    except Exception as e:
        return QueryExecuteResponse(
            success=False,
            error=f"Query execution failed: {str(e)}"
        )


@router.post("/save", response_model=SavedQueryResponse, status_code=status.HTTP_201_CREATED)
async def save_query(
    query_data: SavedQueryCreate,
    db: Session = Depends(get_db)
):
    """Save a query for later use"""
    try:
        saved_query = SavedQuery(
            name=query_data.name,
            description=query_data.description,
            query_json=query_data.query_json,
            sql_query=query_data.sql_query,
            table_name=query_data.table_name
        )
        
        db.add(saved_query)
        db.commit()
        db.refresh(saved_query)
        
        return saved_query
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save query: {str(e)}"
        )


@router.get("/", response_model=List[SavedQueryResponse])
async def list_queries(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all saved queries"""
    queries = db.query(SavedQuery).offset(skip).limit(limit).all()
    return queries


@router.get("/{query_id}", response_model=SavedQueryResponse)
async def get_query(
    query_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific saved query"""
    query = db.query(SavedQuery).filter(SavedQuery.id == query_id).first()
    
    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Query with id {query_id} not found"
        )
    
    return query


@router.put("/{query_id}", response_model=SavedQueryResponse)
async def update_query(
    query_id: int,
    query_data: SavedQueryUpdate,
    db: Session = Depends(get_db)
):
    """Update a saved query"""
    query = db.query(SavedQuery).filter(SavedQuery.id == query_id).first()
    
    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Query with id {query_id} not found"
        )
    
    # Update fields
    update_data = query_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(query, field, value)
    
    try:
        db.commit()
        db.refresh(query)
        return query
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update query: {str(e)}"
        )


@router.delete("/{query_id}", response_model=MessageResponse)
async def delete_query(
    query_id: int,
    db: Session = Depends(get_db)
):
    """Delete a saved query"""
    query = db.query(SavedQuery).filter(SavedQuery.id == query_id).first()
    
    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Query with id {query_id} not found"
        )
    
    try:
        db.delete(query)
        db.commit()
        return MessageResponse(message="Query deleted successfully")
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete query: {str(e)}"
        )
