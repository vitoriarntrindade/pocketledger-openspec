from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.infrastructure.database import get_db
from app.models.user import User
from app.schemas.summary import SummaryResponse
from app.services import summary_service

router = APIRouter(prefix="/api/v1/summary", tags=["summary"])


@router.get("", response_model=SummaryResponse)
def get_summary(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SummaryResponse:
    return summary_service.get_summary(db, current_user, start_date, end_date)
