---
name: python-best-practices
description: The Python code standards for this project — type hints, Google docstrings, 78-character lines, PEP 8 naming, error handling and structure — plus how to read and fix what ruff and mypy report. Use when writing or reviewing Python.
allowed-tools: Read, Grep, Glob, Bash, Edit, Write
license: MIT
metadata:
  author: development-team
  version: "2.0"
  category: code-quality
---

# Python best practices

The tools decide most of this. `ruff` settles formatting, imports, line length
and lint rules; `mypy` settles types. Run them rather than reasoning about
them:

```
make fast      formatting, lint, types — the edit loop
make fix       apply safe autofixes first, then check
make quality   the full gate, including tests and coverage
```

**Never satisfy a check by disabling it.** A blanket `# noqa`, a widened
`ignore` list or a deleted assertion converts a real signal into a false one.
If a rule genuinely does not fit this project, change the rule in
`pyproject.toml` as a deliberate, justified decision — not inline, silently.

What follows is the part tools cannot check.

## The standards that are not negotiable

**Type hints on every signature**, parameters and return alike. Modern syntax,
since this project targets Python 3.12:

```python
def get_owned_category(db: Session, user: User, category_id: int) -> Category:
```

Use `X | None`, `list[X]`, `dict[str, X]`. Not `Optional[X]`, `List[X]`,
`Dict[str, X]` — those are the pre-3.10 spelling and only add noise now.

**78-character lines.** Break with parentheses, never backslashes. The
formatter does most of it; you break the long strings and comments it cannot.

**Google-style docstrings** on public functions, classes and modules.

**Exception chaining.** Always `raise NewError(...) from err`. Dropping the
cause discards the traceback that explains the failure:

```python
try:
    user_id = decode_access_token(credentials.credentials)
except jwt.PyJWTError as err:
    raise UnauthorizedError("Invalid or expired access token.") from err
```

**Never catch bare `Exception`** to swallow it. If you must catch broadly,
log with `exc_info` and re-raise, or narrow the catch.

## Docstrings that earn their place

The point of a docstring is to say what the signature cannot.

```python
# Noise: restates the name, tells the reader nothing.
def get_user(user_id: int) -> User:
    """Get the user."""


# Useful: states the failure mode and the constraint.
def get_owned_transaction(
    db: Session, user: User, transaction_id: int
) -> Transaction:
    """Return the user's transaction.

    Ownership is part of the lookup rather than a check afterwards, so a
    transaction belonging to another user is reported as not found. The
    two cases are deliberately indistinguishable: separating them would
    leak whether the record exists.

    Raises:
        NotFoundError: If no such transaction belongs to this user.
    """
```

Document `Raises:` whenever a caller must handle something. Document `Args:`
and `Returns:` when the names alone are not self-explanatory — repeating
`user_id: The user id.` helps nobody.

## Structure

Functions do one thing and stay under about 50 lines. When a function grows a
second responsibility, extract it with a name that says what it does.

Prefer an early return to a nested `else`. Depth costs more comprehension than
length does.

Validate before mutating. In a multi-step update, check everything first so a
rejected operation leaves state untouched:

```python
# Validated above before mutating anything - a rejected edit leaves the
# transaction unchanged.
transaction.type = new_type
transaction.category_id = category.id
```

## Comments

Explain *why*, never *what*. Code already says what it does; it cannot say what
it was reacting to. The comments worth writing record a constraint, a
workaround, or a decision whose reason is invisible:

```python
# Unhandled exceptions must be caught here rather than via a FastAPI
# Exception handler: Starlette routes that handler to ServerErrorMiddleware,
# which sits outside every user-added middleware, so it could never see this
# middleware's request id.
```

That comment saves the next reader an hour. `# increment the counter` above
`counter += 1` costs them a line.

## Reference

Load these only when you need them:

- `references/patterns.md` — correct and incorrect forms, side by side, for
  each standard above
- `references/checklist.md` — a review checklist for a final pass
- `references/examples.py` — a longer worked module in the project's style
