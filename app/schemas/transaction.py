from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import TransactionType


def _validate_amount(value: Decimal) -> Decimal:
    if value <= 0:
        raise ValueError("amount must be greater than zero")
    if value.as_tuple().exponent < -2:
        raise ValueError("amount must not have more than 2 decimal places")
    return value


class TransactionCreate(BaseModel):
    type: TransactionType
    description: str = Field(min_length=1, max_length=1000)
    amount: Decimal
    transaction_date: date
    category_id: int

    @field_validator("amount")
    @classmethod
    def check_amount(cls, value: Decimal) -> Decimal:
        return _validate_amount(value)


class TransactionUpdate(BaseModel):
    type: TransactionType | None = None
    description: str | None = Field(default=None, min_length=1, max_length=1000)
    amount: Decimal | None = None
    transaction_date: date | None = None
    category_id: int | None = None

    @field_validator("amount")
    @classmethod
    def check_amount(cls, value: Decimal | None) -> Decimal | None:
        return _validate_amount(value) if value is not None else value


class TransactionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    type: TransactionType
    description: str
    amount: Decimal
    transaction_date: date
    category_id: int
    created_at: datetime


class TransactionListResponse(BaseModel):
    items: list[TransactionOut]
    total: int
    page: int
    page_size: int
