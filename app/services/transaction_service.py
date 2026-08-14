from datetime import date
from decimal import Decimal

from sqlalchemy import asc, desc, func
from sqlalchemy.orm import Session

from app.core.errors import NotFoundError, ValidationError
from app.infrastructure.metrics import transactions_created_total
from app.models.category import Category
from app.models.enums import TransactionType
from app.models.transaction import Transaction
from app.models.user import User
from app.services.category_service import get_owned_category

SORT_COLUMNS = {
    "date": Transaction.transaction_date,
    "amount": Transaction.amount,
}


def _check_category_type_match(category: Category, type_: TransactionType) -> None:
    if category.type != type_:
        raise ValidationError("Transaction type must match the category's type.")


def create_transaction(
    db: Session,
    user: User,
    type_: TransactionType,
    description: str,
    amount: Decimal,
    transaction_date: date,
    category_id: int,
) -> Transaction:
    category = get_owned_category(db, user, category_id)
    _check_category_type_match(category, type_)

    transaction = Transaction(
        user_id=user.id,
        category_id=category.id,
        type=type_,
        description=description,
        amount=amount,
        transaction_date=transaction_date,
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    transactions_created_total.inc()
    return transaction


def get_owned_transaction(db: Session, user: User, transaction_id: int) -> Transaction:
    transaction = (
        db.query(Transaction)
        .filter(Transaction.id == transaction_id, Transaction.user_id == user.id)
        .first()
    )
    if transaction is None:
        raise NotFoundError("Transaction not found.")
    return transaction


def update_transaction(
    db: Session,
    user: User,
    transaction_id: int,
    *,
    type_: TransactionType | None = None,
    description: str | None = None,
    amount: Decimal | None = None,
    transaction_date: date | None = None,
    category_id: int | None = None,
) -> Transaction:
    transaction = get_owned_transaction(db, user, transaction_id)

    new_type = type_ if type_ is not None else transaction.type
    new_category_id = category_id if category_id is not None else transaction.category_id
    category = get_owned_category(db, user, new_category_id)
    _check_category_type_match(category, new_type)

    # Validated above before mutating anything - a rejected edit leaves the transaction untouched.
    transaction.type = new_type
    transaction.category_id = category.id
    if description is not None:
        transaction.description = description
    if amount is not None:
        transaction.amount = amount
    if transaction_date is not None:
        transaction.transaction_date = transaction_date

    db.commit()
    db.refresh(transaction)
    return transaction


def delete_transaction(db: Session, user: User, transaction_id: int) -> None:
    transaction = get_owned_transaction(db, user, transaction_id)
    db.delete(transaction)
    db.commit()


def list_transactions(
    db: Session,
    user: User,
    *,
    start_date: date | None = None,
    end_date: date | None = None,
    type_: TransactionType | None = None,
    category_id: int | None = None,
    sort_by: str = "date",
    order: str = "desc",
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Transaction], int]:
    query = db.query(Transaction).filter(Transaction.user_id == user.id)

    if start_date is not None:
        query = query.filter(Transaction.transaction_date >= start_date)
    if end_date is not None:
        query = query.filter(Transaction.transaction_date <= end_date)
    if type_ is not None:
        query = query.filter(Transaction.type == type_)
    if category_id is not None:
        query = query.filter(Transaction.category_id == category_id)

    total = query.with_entities(func.count(Transaction.id)).scalar() or 0

    sort_column = SORT_COLUMNS.get(sort_by, Transaction.transaction_date)
    direction = desc if order == "desc" else asc
    query = query.order_by(direction(sort_column), desc(Transaction.id))

    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return items, total
