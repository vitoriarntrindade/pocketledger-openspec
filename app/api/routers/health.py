from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db

router = APIRouter(tags=["ops"])


@router.get("/health")
def health() -> dict:
    return {"status": "healthy"}


@router.get("/ready")
def ready(response: Response, db: Session = Depends(get_db)) -> dict:
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "not-ready"}
    return {"status": "ready"}
