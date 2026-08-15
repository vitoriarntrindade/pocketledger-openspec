# Naming and module conventions

## Naming

| Kind | Style | Example |
|---|---|---|
| module | `lower_with_underscores` | `transaction_service.py` |
| class | `PascalCase` | `TransactionOut` |
| function | `lower_with_underscores` | `get_owned_transaction` |
| constant | `UPPER_WITH_UNDERSCORES` | `SORT_COLUMNS` |
| private | `_leading_underscore` | `_check_category_type_match` |

Files follow their layer:

- routers: `app/api/routers/<plural>.py` — `transactions.py`
- services: `app/services/<singular>_service.py` — `transaction_service.py`
- models: `app/models/<singular>.py` — `transaction.py`
- schemas: `app/schemas/<singular>.py` — `transaction.py`
- tests: `tests/test_<plural>.py` — `test_transactions.py`

`type` is a builtin, so the service layer takes `type_` as a parameter name
while the API keeps `type` in its public shape. This is deliberate: the wire
format should not leak a Python constraint.

## Service function signatures

Services are modules of functions, not classes. There is no state to hold, and
a class would only add a layer of indirection.

The first two parameters are always `db: Session, user: User`. Optional
parameters come after a `*`, forcing them to be passed by name at the call
site:

```python
def list_transactions(
    db: Session,
    user: User,
    *,
    start_date: date | None = None,
    type_: TransactionType | None = None,
    page: int = 1,
) -> tuple[list[Transaction], int]:
```

## Imports

Three groups, separated by a blank line, ordered by ruff's isort rules:
standard library, third party, then first party (`app`). Ruff enforces this —
do not hand-order imports.

Use `from __future__ import annotations` in new modules so annotations stay
cheap and forward references work without quoting.

For model relationships that would import circularly, import under
`TYPE_CHECKING` and quote the annotation:

```python
if TYPE_CHECKING:
    from app.models.transaction import Transaction

transactions: Mapped[list["Transaction"]] = relationship(back_populates="user")
```

## Line length

78 characters. Break with parentheses rather than backslashes:

```python
transaction = transaction_service.create_transaction(
    db,
    current_user,
    payload.type,
    payload.description,
)
```

The formatter handles most of this. Where it cannot — long string literals,
comments — break them yourself into implicit concatenations.

## Docstrings

Google style, on public functions, classes and modules.

Write them to explain what the reader cannot get from the signature: the
constraint, the failure mode, the reason for an unobvious decision. A docstring
that restates its own signature is noise, and noise trains people to skip
docstrings entirely.

```python
def decode_access_token(token: str) -> int:
    """Return the user id encoded in the token.

    Raises:
        jwt.PyJWTError: If the token is malformed, expired, or signed
            with a different secret.
    """
```

## Type hints

Every function signature is annotated, parameters and return alike. Use modern
syntax — `X | None`, `list[X]`, `dict[str, X]` — since the project targets
Python 3.12.

Annotate SQLAlchemy columns with `Mapped[...]`, which is what makes the models
type-check at all.
