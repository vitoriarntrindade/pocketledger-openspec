from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.infrastructure.database import get_db
from app.models.enums import TransactionType
from app.models.user import User
from app.schemas.transaction import (
    TransactionCreate,
    TransactionListResponse,
    TransactionOut,
    TransactionUpdate,
)
from app.services import transaction_service

router = APIRouter(prefix="/api/v1/transactions", tags=["transactions"])


@router.post(
    "",
    response_model=TransactionOut,
    status_code=status.HTTP_201_CREATED,
)
def create_transaction(
    payload: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TransactionOut:
    transaction = transaction_service.create_transaction(
        db,
        current_user,
        payload.type,
        payload.description,
        payload.amount,
        payload.transaction_date,
        payload.category_id,
    )
    return TransactionOut.model_validate(transaction)


@router.get("", response_model=TransactionListResponse)
def list_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    start_date: date | None = None,
    end_date: date | None = None,
    type: TransactionType | None = None,
    category_id: int | None = None,
    sort_by: Literal["date", "amount"] = "date",
    order: Literal["asc", "desc"] = "desc",
    page: int = Query(default=1, ge=1),
    page_size: int = Query(
        default=settings.default_page_size,
        ge=1,
        le=settings.max_page_size,
    ),
) -> TransactionListResponse:
    items, total = transaction_service.list_transactions(
        db,
        current_user,
        start_date=start_date,
        end_date=end_date,
        type_=type,
        category_id=category_id,
        sort_by=sort_by,
        order=order,
        page=page,
        page_size=page_size,
    )
    validated_items = [TransactionOut.model_validate(item) for item in items]
    return TransactionListResponse(
        items=validated_items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{transaction_id}", response_model=TransactionOut)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TransactionOut:
    transaction = transaction_service.get_owned_transaction(
        db,
        current_user,
        transaction_id,
    )
    return TransactionOut.model_validate(transaction)


@router.patch("/{transaction_id}", response_model=TransactionOut)
def update_transaction(
    transaction_id: int,
    payload: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TransactionOut:
    transaction = transaction_service.update_transaction(
        db,
        current_user,
        transaction_id,
        type_=payload.type,
        description=payload.description,
        amount=payload.amount,
        transaction_date=payload.transaction_date,
        category_id=payload.category_id,
    )
    return TransactionOut.model_validate(transaction)


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    transaction_service.delete_transaction(db, current_user, transaction_id)
