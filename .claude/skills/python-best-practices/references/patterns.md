# Patterns, correct and incorrect

Load this when a standard in `SKILL.md` needs a concrete form.

## Type hints

```python
# Correct
def calculate_total(prices: list[Decimal], tax_rate: Decimal) -> Decimal:
    return sum(prices) * (1 + tax_rate)

# Wrong: unannotated
def calculate_total(prices, tax_rate):
    return sum(prices) * (1 + tax_rate)

# Wrong: pre-3.10 spelling, and float for money
def calculate_total(prices: List[float], tax_rate: Optional[float]) -> float:
```

Money is `Decimal`. `float` cannot represent 0.10 exactly, and a ledger that
loses a cent per rounding is wrong in a way tests rarely catch.

## Line breaking

```python
# Correct: parentheses, trailing comma
transaction = transaction_service.create_transaction(
    db,
    current_user,
    payload.type,
    payload.amount,
)

# Correct: implicit concatenation for long strings
message = (
    "DATABASE_URL must not use default development credentials "
    "outside development."
)

# Correct: parenthesised imports
from app.schemas.transaction import (
    TransactionCreate,
    TransactionOut,
    TransactionUpdate,
)

# Wrong: backslash continuation
total = first_value + \
    second_value
```

## Early returns

```python
# Correct: the exceptional case leaves immediately
def get_owned_category(db: Session, user: User, category_id: int) -> Category:
    category = (
        db.query(Category)
        .filter(Category.id == category_id, Category.user_id == user.id)
        .first()
    )
    if category is None:
        raise NotFoundError("Category not found.")
    return category

# Wrong: the happy path is buried
def get_owned_category(db, user, category_id):
    category = db.query(Category).filter(...).first()
    if category is not None:
        if category.user_id == user.id:
            return category
        else:
            raise NotFoundError("Category not found.")
    else:
        raise NotFoundError("Category not found.")
```

## Exception handling

```python
# Correct: narrow catch, cause preserved
try:
    user_id = decode_access_token(token)
except jwt.PyJWTError as err:
    raise UnauthorizedError("Invalid or expired access token.") from err

# Correct: broad catch that does not hide the failure
try:
    response = await call_next(request)
except Exception as exc:
    error_logger.error("unhandled_exception", exc_info=exc)
    response = JSONResponse(status_code=500, content=...)

# Wrong: the failure disappears
try:
    risky()
except Exception:
    pass

# Wrong: cause discarded, traceback lost
except jwt.PyJWTError:
    raise UnauthorizedError("Invalid token.")
```

## Naming

```python
# Correct: says what it is
MAX_LOGIN_ATTEMPTS = 5
SORT_COLUMNS = {"date": Transaction.transaction_date}

def get_owned_transaction(...) -> Transaction: ...
def _check_category_type_match(...) -> None: ...

# Wrong: says nothing
MAX = 5
d = {"date": Transaction.transaction_date}

def process(x): ...
def handle_data(data): ...
```

`data`, `tmp`, `result`, `process`, `handle` and `manager` almost always mean
the author had not yet decided what the thing was.

## Validate before mutating

```python
# Correct: all validation first, so a rejection changes nothing
def update_transaction(db, user, transaction_id, *, type_=None, ...):
    transaction = get_owned_transaction(db, user, transaction_id)
    new_type = type_ if type_ is not None else transaction.type
    category = get_owned_category(db, user, new_category_id)
    _check_category_type_match(category, new_type)

    transaction.type = new_type
    transaction.category_id = category.id
    db.commit()

# Wrong: partially applied on failure
def update_transaction(db, user, transaction_id, *, type_=None, ...):
    transaction = get_owned_transaction(db, user, transaction_id)
    if type_ is not None:
        transaction.type = type_          # already mutated
    category = get_owned_category(db, user, category_id)
    _check_category_type_match(category, transaction.type)   # may raise
    db.commit()
```

## Imports

```python
# Standard library
from datetime import date
from decimal import Decimal

# Third party
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# First party
from app.core.errors import NotFoundError
from app.models.user import User
```

Ruff enforces the grouping and ordering. Do not hand-sort.

For circular model relationships:

```python
if TYPE_CHECKING:
    from app.models.transaction import Transaction

transactions: Mapped[list["Transaction"]] = relationship(back_populates="user")
```
