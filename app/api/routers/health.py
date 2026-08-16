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
        # The broad catch is deliberate here, and is why BLE001 is scoped
        # off for this module. A readiness probe answers one question —
        # can this instance serve traffic? — and any failure reaching this
        # point means no. Narrowing to SQLAlchemyError would let a driver,
        # DNS or configuration error escape as a 500, which tells an
        # orchestrator less than an orderly 503 does.
        #
        # The failure is not swallowed: it becomes the response.
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "not-ready"}
    return {"status": "ready"}
