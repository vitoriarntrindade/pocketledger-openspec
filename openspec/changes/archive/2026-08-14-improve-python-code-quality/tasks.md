# Implementation Tasks: Python Code Quality Improvements

## 1. Preparation

- [x] 1.1 Create feature branch: `git checkout -b feature/improve-python-code-quality`
- [x] 1.2 Install development dependencies: `pip install -e ".[dev]"` (in .venv)
- [x] 1.3 Verify quality tools installed: `ruff --version`, `flake8 --version`, `mypy --version`
- [x] 1.4 Run baseline quality checks: `make check` (document current state)

## 2. Type Safety: Router Schema Conversions

### 2.1 Authentication Router

- [x] 2.1.1 Fix `app/api/routers/auth.py` line 15: Register endpoint
  - Requirement: Return `UserOut` schema, not `User` ORM model
  - Action: Convert `return user` to `return UserOut.model_validate(user)`
  - Verify: `mypy app/api/routers/auth.py` shows no "Incompatible return" error
  
- [x] 2.1.2 Fix `app/api/routers/auth.py` line 20: Login endpoint
  - Requirement: Return `TokenResponse` with token, not raw token string
  - Action: Ensure response_model matches actual return type
  - Verify: Type checking passes

### 2.2 Users Router

- [x] 2.2.1 Fix `app/api/routers/users.py`: Get profile endpoint
  - Requirement: Return `UserOut` schema
  - Action: Convert `User` ORM to `UserOut` schema before returning
  - Verify: `mypy app/api/routers/users.py` clean

### 2.3 Transactions Router

- [x] 2.3.1 Fix `app/api/routers/transactions.py` lines 29, 74, 84: CRUD endpoints
  - Requirement: All return `TransactionOut` schema, not `Transaction` ORM
  - Action: 
    - Line 29 (create): `return TransactionOut.model_validate(transaction)`
    - Line 65 (list): Convert list items: `[TransactionOut.from_orm(t) for t in transactions]`
    - Line 74 (update): `return TransactionOut.model_validate(transaction)`
    - Line 84 (delete): `return TransactionOut.model_validate(transaction)`
  - Verify: `mypy app/api/routers/transactions.py` clean

### 2.4 Categories Router

- [x] 2.4.1 Fix `app/api/routers/categories.py` lines 19, 27, 37: CRUD endpoints
  - Requirement: Return `CategoryOut` schema, not `Category` ORM
  - Action: Convert ORM to schema at return point
  - Verify: `mypy app/api/routers/categories.py` clean

- [x] 2.4.2 Verify all router type errors fixed
  - Command: `mypy app/api/routers/ --ignore-missing-imports`
  - Expected: 0 return-value type errors

## 3. Circular Import Resolution (TYPE_CHECKING)

### 3.1 User Model

- [x] 3.1.1 Update `app/models/user.py` to use TYPE_CHECKING
  - Add import: `from typing import TYPE_CHECKING`
  - Add guard:
    ```python
    if TYPE_CHECKING:
        from app.models.transaction import Transaction
        from app.models.category import Category
    ```
  - Update relationships to use string forward refs: `list["Transaction"]`, `list["Category"]`
  - Verify: `python -c "from app.models.user import User; print(ok)" `
  - Verify: `mypy app/models/user.py` shows no "Name is not defined" error

### 3.2 Transaction Model

- [x] 3.2.1 Update `app/models/transaction.py` to use TYPE_CHECKING
  - Add forward refs for `User` and `Category` under TYPE_CHECKING guard
  - Update relationship types to use string forward refs
  - Verify: Import test and mypy pass

### 3.3 Category Model

- [x] 3.3.1 Update `app/models/category.py` to use TYPE_CHECKING
  - Add forward refs for `User` and `Transaction` under TYPE_CHECKING guard
  - Update relationship types to use string forward refs
  - Verify: Import test and mypy pass

- [x] 3.3.2 Verify all model circular imports resolved
  - Command: `python -c "from app.models import User, Transaction, Category; print('OK')"`
  - Expected: No ImportError, circular reference resolved

## 4. Line Length Compliance (PEP 8)

### 4.1 Error Handlers

- [x] 4.1.1 Break long lines in `app/api/error_handlers.py`
  - Lines 27, 33, 37, 40, 43, 47: Split complex expressions
  - Strategy: Use implicit line continuation with parentheses
  - Verify: `flake8 app/api/error_handlers.py --select E501` = 0 violations

### 4.2 Middleware

- [x] 4.2.1 Break long lines in `app/api/middleware.py`
  - Lines 52, 55, 64, 75: Split if conditions and log calls
  - Verify: `flake8 app/api/middleware.py --select E501` = 0 violations

### 4.3 Router Decorators

- [x] 4.3.1 Break `@router` decorators in `app/api/routers/auth.py`
  - Line 12: `@router.post(...)` - split across lines
  - Line 18: `@router.post(...)` - split across lines
  - Pattern:
    ```python
    @router.post(
        "/endpoint",
        response_model=SchemaOut,
        status_code=status.HTTP_201_CREATED,
    )
    ```
  - Verify: `flake8 app/api/routers/auth.py --select E501` = 0 violations

- [x] 4.3.2 Break decorators in `app/api/routers/transactions.py`
  - Lines 10, 14, 21, 31, 41, 51: Split all long decorators
  - Verify: `flake8 app/api/routers/transactions.py --select E501` = 0 violations

- [x] 4.3.3 Break decorators in `app/api/routers/categories.py`
  - Lines 10, 14, 20, 30, 40: Split all long decorators
  - Verify: `flake8 app/api/routers/categories.py --select E501` = 0 violations

### 4.4 Function Signatures & Type Hints

- [x] 4.4.1 Break long function signatures in routers
  - Pattern: Parameters on separate lines
    ```python
    def function(
        param1: Type1,
        param2: Type2,
        db: Session = Depends(get_db),
    ) -> ReturnType:
    ```
  - Verify: `flake8 app/api/ --select E501` = 0 violations

### 4.5 Imports

- [x] 4.5.1 Break long import statements
  - Pattern: Use implicit line continuation
    ```python
    from app.schemas import (
        UserOut,
        TransactionOut,
        CategoryOut,
    )
    ```
  - Verify: All E501 violations resolved

## 5. Exception Chaining

### 5.1 Auth Dependencies

- [x] 5.1.1 Update `app/api/deps.py` exception handlers
  - Line 24: Change `raise UnauthorizedError(...)` to `raise UnauthorizedError(...) from jwt.PyJWTError`
  - Capture exception: `except jwt.PyJWTError as err`
  - Chain: `raise ... from err`
  - Verify: Exception traceback shows original error context

### 5.2 Category Service

- [x] 5.2.1 Update `app/services/category_service.py` exception handlers
  - Line 69: Add exception chaining to IntegrityError handler
  - Pattern: `except IntegrityError as err: raise ConflictError(...) from err`
  - Verify: Tests still pass

## 6. Type Annotations for Globals

### 6.1 Middleware Globals

- [x] 6.1.1 Add type hint to `app/api/middleware.py` line 15
  - Current: `_rate_limiter_attempts = {}`
  - Update: `_rate_limiter_attempts: dict[str, list[float]] = {}`
  - Reasoning: Explicit type for MyPy
  - Verify: `mypy app/api/middleware.py` passes

## 7. Validation & Testing

### 7.1 Quality Checks

- [x] 7.1.1 Run full linting suite
  - Command: `make lint`
  - Expected: Ruff and Flake8 pass (allow B008 FastAPI pattern)
  - Expected: No E501 violations
  - Document any remaining warnings

- [x] 7.1.2 Run type checking
  - Command: `mypy app --ignore-missing-imports`
  - Expected: 0 type errors
  - Expected: No "Incompatible return value" errors
  - Expected: No "Name is not defined" errors

- [x] 7.1.3 Run all tests
  - Command: `make test`
  - Expected: All tests pass
  - Expected: No regressions
  - Coverage: Should remain stable or improve

### 7.2 Pre-commit Hooks (Optional)

- [x] 7.2.1 Setup pre-commit hooks
  - Command: `pip install pre-commit && pre-commit install`
  - Verify: `.git/hooks/pre-commit` exists
  - Test: `pre-commit run --all-files` (should pass)

### 7.3 Final Verification

- [x] 7.3.1 Comprehensive verification
  - Command: `make check` (ruff + flake8 + mypy)
  - Expected: All checks pass
  - Expected: No new warnings introduced

- [x] 7.3.2 Feature branch tests
  - Ensure CI/CD passes (if available)
  - Verify no test failures
  - Verify no linting regressions

## 8. Documentation & Cleanup

- [x] 8.1 Update CHANGELOG.md with changes summary
  - Entry: Python Code Quality - Type hints, PEP 8 compliance, circular import fixes

- [x] 8.2 Verify BEST_PRACTICES.md is accurate
  - Review standards are reflected in code
  - Check examples match new patterns

- [x] 8.3 Commit changes with proper message
  - Branch cleanup: Ensure all work committed
  - Commit message: `feat: improve python code quality - type safety, pep 8, circular imports`

- [x] 8.4 Create pull request
  - Base: main
  - Title: Python Code Quality Improvements
  - Description: References this change spec
  - Wait for review and approval

## 9. Merge & Closure

- [x] 9.1 Merge feature branch to main
  - Command: `git merge feature/improve-python-code-quality`
  - Verify: CI passes
  - Verify: All tests pass

- [x] 9.2 Archive this change
  - Command: `openspec archive improve-python-code-quality`
  - Result: Specs integrated into main specs

- [x] 9.3 Create quality report for future reference
  - Document: What was fixed, what metrics improved
  - Store: Keep QUALITY_REPORT.md for historical reference

---

## Notes on Task Verification

Each task is verifiable:
- Type conversion tasks verified by: `mypy` command shows no type errors
- Import fixes verified by: successful Python import statement
- Line length fixes verified by: `flake8 --select E501` returns 0 violations
- Exception chaining verified by: running exception scenarios
- Quality checks verified by: `make check` passes

**Total Estimated Time**: 4-5 hours  
**Parallelizable**: Type conversions and line breaks can be done in parallel by different developers working on different routers/modules.
