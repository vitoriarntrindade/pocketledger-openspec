# Design: Python Code Quality Improvements

## Context

See proposal.md - Why section for motivation.

Current state:
- **Type mismatches**: Routers return ORM models (User, Transaction, Category) instead of Pydantic schemas (UserOut, TransactionOut, CategoryOut)
- **Circular imports**: Models have forward references without TYPE_CHECKING pattern
- **Line length**: 73 lines exceed 78-character PEP 8 limit
- **Exception handling**: Missing exception chaining (from err) in error handlers
- **Type coverage**: ~65% - many functions lack complete type annotations

Quality tools configured:
- Ruff (linter/formatter)
- Flake8 (PEP 8)
- MyPy (type checker)
- Pre-commit hooks (git integration)

## Goals

1. **Type Safety**: All endpoints return properly typed Pydantic schemas, verified by mypy
2. **PEP 8 Compliance**: All code fits within 78-character lines
3. **Import Safety**: Resolve circular import issues using TYPE_CHECKING pattern
4. **Exception Clarity**: All exception handlers use proper chaining
5. **Automation**: Pre-commit and CI/CD enforce standards on every commit
6. **Developer Experience**: Clear guidance in BEST_PRACTICES.md and Makefile commands

## Non-Goals

- Rewrite router logic or endpoints (pure refactor, no behavioral change)
- Increase test coverage (separate initiative)
- Add new features or capabilities
- Refactor models beyond TYPE_CHECKING pattern fix
- Change database schema or migrations

## Decisions

### Decision 1: Schema Conversion in Routers (not Services)

**Chosen**: Convert ORM → Schema at router level (endpoint response)

**Rationale**:
- Schemas are API contracts, should be validated at boundary
- Services return ORM models (database objects)
- Routers convert to schemas before returning to client
- Clear separation of concerns

**Alternatives**:
- ❌ Convert in services: Mixes API concerns with business logic
- ❌ Convert in models: Bloats ORM models with API knowledge

**Implementation**:
```python
# Before
@router.post("/register", response_model=UserOut)
def register(...) -> UserOut:
    user = auth_service.register_user(...)
    return user  # Type error: returning User instead of UserOut

# After
@router.post("/register", response_model=UserOut)
def register(...) -> UserOut:
    user = auth_service.register_user(...)
    return UserOut.model_validate(user)  # Proper conversion
```

### Decision 2: TYPE_CHECKING for Circular Imports

**Chosen**: Use `from typing import TYPE_CHECKING` to guard circular imports

**Rationale**:
- Standard Python pattern for circular import resolution
- Doesn't affect runtime performance
- MyPy understands it natively
- Cleaner than string forward references everywhere

**Alternatives**:
- ❌ Reorganize model files: Too disruptive, changes module structure
- ❌ Use all string forward refs: Loses IDE autocomplete, harder to read

**Implementation**:
```python
# app/models/user.py
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.transaction import Transaction  # Only for type checking
    from app.models.category import Category


class User:
    transactions: Mapped[list["Transaction"]] = relationship(...)
```

### Decision 3: Line Length via Line Breaking, not Wrapping

**Chosen**: Break long lines using implicit continuation (parentheses), not format strings

**Rationale**:
- More readable than single-line strings
- Implicit continuation is standard Python idiom
- Works for decorators, function calls, type hints, imports
- Preserves semantic meaning

**Examples**:
```python
# Decorators
@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
)

# Type hints
def process(
    transactions: List[Transaction],
    user_id: int,
) -> Optional[ProcessResult]:

# Imports
from app.schemas import (
    UserOut,
    TransactionOut,
    CategoryOut,
)
```

### Decision 4: Exception Chaining Strategy

**Chosen**: Use `raise ExceptionType(...) from original_error` in all handlers

**Rationale**:
- Preserves exception context for debugging
- Shows root cause in traceback
- PEP 409 best practice
- Helps identify error sources

**Implementation**:
```python
# Before
try:
    user_id = decode_token(token)
except jwt.PyJWTError:
    raise UnauthorizedError("Invalid token")

# After
try:
    user_id = decode_token(token)
except jwt.PyJWTError as err:
    raise UnauthorizedError("Invalid token") from err
```

### Decision 5: Type Annotations for Module-Level State

**Chosen**: Add explicit type hints to all module-level variables (caches, dicts, etc.)

**Rationale**:
- Makes intent clear to MyPy and developers
- Enables IDE type checking for usage
- Prevents accidental type mutations
- Example: `_rate_limiter_attempts: dict[str, list[float]] = {}`

## Risks & Trade-offs

### [Risk] Schema Conversion Overhead
**Impact**: Minor - Each request undergoes ORM → Pydantic conversion  
**Mitigation**: Conversion is fast (microseconds), acceptable for API boundary. Pydantic handles it efficiently. No caching needed.

### [Risk] Circular Import Complexity
**Impact**: Developers might not understand TYPE_CHECKING pattern  
**Mitigation**: Document in BEST_PRACTICES.md with examples. Code comment explaining pattern.

### [Risk] Large Line-Break Refactor
**Impact**: Many files change, harder to review  
**Mitigation**: Break into focused PRs by module (routers, models, services). Use git blame to trace changes.

### [Risk] MyPy Type Errors from Libraries
**Impact**: Third-party libs might lack type hints (sqlalchemy, fastapi)  
**Mitigation**: Use `# type: ignore[specific-error]` for known library issues. Configure mypy `ignore_missing_imports = true` for third-party.

### [Risk] Pre-commit Hook Friction
**Impact**: Developers might find hooks slowing down commits  
**Mitigation**: Hooks are fast (ruff/flake8 run in <1sec). Make them optional initially, then mandatory in CI.

## Migration Plan

### Phase 1: Setup & Preparation (no code changes yet)
1. Config files already in place (pyproject.toml, .flake8, etc.)
2. Documentation in place (BEST_PRACTICES.md, QUALITY_REPORT.md)
3. Feature branch: `feature/improve-python-code-quality`

### Phase 2: Type Safety (ORM → Schema conversions)
1. Update routers/auth.py - register, login return schema
2. Update routers/users.py - get_profile returns schema
3. Update routers/transactions.py - all CRUD endpoints
4. Update routers/categories.py - all CRUD endpoints
5. Run `make type-check` - verify mypy passes

### Phase 3: Import Resolution (TYPE_CHECKING)
1. Update models/user.py - forward refs with TYPE_CHECKING
2. Update models/transaction.py - forward refs with TYPE_CHECKING
3. Update models/category.py - forward refs with TYPE_CHECKING
4. Verify no import errors: `python -c "import app.models"`

### Phase 4: Line Length Compliance
1. Break long decorators (@router decorators)
2. Format long function signatures
3. Split long type hints
4. Organize long imports
5. Run `flake8 --select E501` - verify all E501 fixed

### Phase 5: Exception Chaining
1. Update api/deps.py - add exception chaining
2. Update services/category_service.py - add exception chaining
3. Run tests to verify error handling still works

### Phase 6: Type Annotations
1. Add type hints to middleware.py globals
2. Add any missing function annotations
3. Run `mypy . --ignore-missing-imports` - verify success

### Phase 7: Validation & Testing
1. Run `make check` - all linters pass
2. Run `make test` - all tests pass
3. Setup pre-commit hooks: `pre-commit install`
4. Test hooks on single commit
5. Merge feature branch to main

### Rollback Strategy
If critical issues discovered:
1. Revert feature branch: `git revert <merge-commit>`
2. Issues will be in git history for inspection
3. Fix and re-propose separately
4. No data loss - pure code refactor

## Open Questions

**Q1**: Should we add docstrings (Google style) to all functions in this change, or separate PR?  
→ **A**: Separate PR. This change focuses on type safety, line length, and import fixes. Docstrings can follow as documentation improvement.

**Q2**: Should B008 (FastAPI Depends) trigger ruff failures in CI?  
→ **A**: No. Configure ruff to accept B008 as valid pattern for FastAPI (already in pyproject.toml ignore list).

**Q3**: Do we need backward compatibility for old schema formats?  
→ **A**: No. API is not public (internal service). Schemas change with no versioning needed.

## Acceptance Criteria (Design Level)

- [ ] All code changes follow spec requirements (type safety, PEP 8, etc.)
- [ ] MyPy passes with <5% of code needing `# type: ignore` comments
- [ ] All new functions have type hints and pass mypy
- [ ] No behavioral changes - endpoints return same data, just properly typed
- [ ] Pre-commit hooks functional and non-blocking initially
- [ ] Code review passes (focuses on type safety logic, not formatting)
