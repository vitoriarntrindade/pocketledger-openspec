from datetime import date
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.infrastructure.metrics import summaries_requested_total
from app.models.category import Category
from app.models.enums import TransactionType
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.summary import CategoryExpense, SummaryResponse


def get_summary(db: Session, user: User, start_date: date, end_date: date) -> SummaryResponse:
    base_query = db.query(Transaction).filter(
        Transaction.user_id == user.id,
        Transaction.transaction_date >= start_date,
        Transaction.transaction_date <= end_date,
    )

    total_income = (
        base_query.filter(Transaction.type == TransactionType.income)
        .with_entities(func.coalesce(func.sum(Transaction.amount), 0))
        .scalar()
    )
    total_expenses = (
        base_query.filter(Transaction.type == TransactionType.expense)
        .with_entities(func.coalesce(func.sum(Transaction.amount), 0))
        .scalar()
    )
    income_count = base_query.filter(Transaction.type == TransactionType.income).count()
    expense_count = base_query.filter(Transaction.type == TransactionType.expense).count()

    category_rows = (
        base_query.filter(Transaction.type == TransactionType.expense)
        .join(Category, Category.id == Transaction.category_id)
        .with_entities(Category.id, Category.name, func.sum(Transaction.amount))
        .group_by(Category.id, Category.name)
        .order_by(func.sum(Transaction.amount).desc())
        .all()
    )

    total_income = Decimal(total_income)
    total_expenses = Decimal(total_expenses)

    summaries_requested_total.inc()

    return SummaryResponse(
        start_date=start_date,
        end_date=end_date,
        total_income=total_income,
        total_expenses=total_expenses,
        balance=total_income - total_expenses,
        income_count=income_count,
        expense_count=expense_count,
        expenses_by_category=[
            CategoryExpense(category_id=cid, category_name=name, total=Decimal(total))
            for cid, name, total in category_rows
        ],
    )
