from fastapi import APIRouter
from app.api.endpoints import queries, metadata

api_router = APIRouter()

api_router.include_router(
    queries.router,
    prefix="/queries",
    tags=["queries"]
)

api_router.include_router(
    metadata.router,
    prefix="/metadata",
    tags=["metadata"]
)
