from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class CategoryExpense(BaseModel):
    category_id: int
    category_name: str
    total: Decimal


class SummaryResponse(BaseModel):
    start_date: date
    end_date: date
    total_income: Decimal
    total_expenses: Decimal
    balance: Decimal
    income_count: int
    expense_count: int
    expenses_by_category: list[CategoryExpense]
