from datetime import datetime, timezone
from typing import Literal

from chromadb.api import ClientAPI
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.deps import get_chroma_client, get_db

router = APIRouter()


class DependencyStatus(BaseModel):
    status: Literal["ok", "error"]


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    timestamp: datetime
    database: DependencyStatus
    vector_store: DependencyStatus


@router.get("/health", response_model=HealthResponse, summary="Check service health")
def health_check(db: Session = Depends(get_db), chroma_client: ClientAPI = Depends(get_chroma_client)) -> HealthResponse:
    database_ok, vector_store_ok = True, True
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError:
        database_ok = False
    try:
        chroma_client.heartbeat()
    except Exception:
        vector_store_ok = False
    response = HealthResponse(status="ok" if database_ok and vector_store_ok else "degraded", timestamp=datetime.now(timezone.utc), database=DependencyStatus(status="ok" if database_ok else "error"), vector_store=DependencyStatus(status="ok" if vector_store_ok else "error"))
    if response.status == "degraded":
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=response.model_dump(mode="json"))
    return response
