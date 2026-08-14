---
name: python-best-practices
description: Enforce Python best practices following PEP 8, type hints, Google-style docstrings, and line length limits. Use with ruff, flake8, mypy, and other linting tools for comprehensive code quality.
allowed-tools: Read, Bash, Edit, Write
license: MIT
compatibility: Python 3.8+
metadata:
  author: development-team
  version: "1.0"
  category: code-quality
---

# Python Best Practices

## Goal

Enforce consistent, high-quality Python code following PEP 8, type safety, and documentation standards.

Code quality is enforced through:
- Automatic linting (ruff, flake8)
- Type checking (mypy)
- Docstring validation
- Line length constraints
- Import organization
- Naming conventions

---

## Configuration

### Setup Tools

Install required packages:

```bash
pip install ruff flake8 mypy google-code-style
```

### pyproject.toml

Configure project standards:

```toml
[tool.ruff]
line-length = 78
target-version = "py38"

[tool.ruff.lint]
select = [
    "E",      # pycodestyle errors
    "W",      # pycodestyle warnings
    "F",      # pyflakes
    "I",      # isort
    "N",      # pep8-naming
    "UP",     # pyupgrade
    "BLE",    # flake8-blind-except
    "B",      # flake8-bugbear
    "A",      # flake8-builtins
    "C4",     # flake8-comprehensions
    "DTZ",    # flake8-datetimez
    "T10",    # flake8-debugger
    "ISC",    # flake8-implicit-str-concat
    "PIE",    # flake8-pie
    "RSE",    # flake8-raise
    "RET",    # flake8-return
    "SIM",    # flake8-simplify
    "PERF",   # perflint
    "FURB",   # refurb
    "LOG",    # flake8-logging
    "RUF",    # ruff-specific
]

ignore = [
    "E501",   # line too long (handled by line-length)
    "E203",   # whitespace before colon
    "W503",   # line break before binary operator
]

[tool.ruff.lint.isort]
known-first-party = ["app", "src"]
known-third-party = ["fastapi", "sqlalchemy", "pydantic"]

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
strict_optional = true
strict_equality = true

[[tool.mypy.overrides]]
module = "tests.*"
ignore_errors = true

[tool.pydocstyle]
convention = "google"
add-ignore = ["D100", "D104"]

[tool.pylint.format]
max-line-length = 78

[tool.pylint.basic]
good-names = ["i", "j", "k", "ex", "Run", "_", "id", "x", "y", "z"]
```

### .flake8

```ini
[flake8]
max-line-length = 78
max-complexity = 10
exclude = .git,__pycache__,.venv,build,dist,.eggs,*.egg-info,venv
ignore = E203,W503
per-file-ignores =
    __init__.py:F401,F403
    tests/*:F401,F811
```

---

## Code Standards

### 1. Type Hints

**Rule:** All functions and class attributes must have type hints.

✅ Good:
```python
from typing import Optional, Dict, List

def calculate_total(
    prices: List[float],
    tax_rate: float,
) -> float:
    """Calculate total with tax.
    
    Args:
        prices: List of item prices.
        tax_rate: Tax rate as decimal (0.1 for 10%).
        
    Returns:
        Total amount including tax.
    """
    subtotal = sum(prices)
    return subtotal * (1 + tax_rate)


class UserRepository:
    """Repository for user data access."""
    
    def __init__(self, db_url: str) -> None:
        """Initialize repository.
        
        Args:
            db_url: Database connection URL.
        """
        self.db_url: str = db_url
    
    def find_by_id(
        self,
        user_id: int,
    ) -> Optional[Dict[str, any]]:
        """Find user by ID.
        
        Args:
            user_id: User identifier.
            
        Returns:
            User data dict or None if not found.
        """
        pass
```

❌ Bad:
```python
# Missing type hints
def calculate_total(prices, tax_rate):
    return sum(prices) * (1 + tax_rate)

# Incomplete type hints
class UserRepository:
    def __init__(self, db_url: str):
        self.db_url = db_url
```

### 2. Line Length: Maximum 78 Characters

**Rule:** No line exceeds 78 characters.

✅ Good:
```python
# Line break for long function calls
result = some_function(
    argument_one,
    argument_two,
    argument_three,
)

# Line break for long strings
message = (
    "This is a long message that would exceed "
    "the 78 character limit if on one line."
)

# Line break for long imports
from package.subpackage.module import (
    FirstClass,
    SecondClass,
    ThirdClass,
)
```

❌ Bad:
```python
# 95 characters - exceeds limit
result = some_function(argument_one, argument_two, argument_three)

# Long single-line string
message = "This is a very long message that exceeds the 78 character limit and should be broken up"
```

### 3. Google-Style Docstrings

**Rule:** All modules, classes, and functions have docstrings in Google format.

✅ Good:
```python
"""Module for user authentication and management.

This module provides utilities for user registration, login,
and token management.
"""

from typing import Optional


class AuthError(Exception):
    """Exception raised for authentication failures."""
    
    pass


def verify_password(
    password: str,
    hashed: str,
) -> bool:
    """Verify password matches hash.
    
    Uses bcrypt with constant-time comparison to prevent
    timing attacks.
    
    Args:
        password: Plain text password to verify.
        hashed: Bcrypt hashed password.
        
    Returns:
        True if password matches, False otherwise.
        
    Raises:
        AuthError: If hash verification fails.
        
    Example:
        >>> verify_password("secret", bcrypt_hash)
        True
    """
    pass


async def authenticate_user(
    username: str,
    password: str,
) -> Optional[dict]:
    """Authenticate user by username and password.
    
    Args:
        username: User's login username.
        password: User's login password.
        
    Returns:
        User data dict if authenticated, None otherwise.
        
    Raises:
        AuthError: If authentication service is unavailable.
    """
    pass
```

❌ Bad:
```python
# Missing module docstring
def verify_password(password, hashed):
    # This just calls bcrypt.checkpw
    return bcrypt.checkpw(password, hashed)

# Incomplete docstring
def authenticate_user(username: str, password: str) -> Optional[dict]:
    """Authenticate user."""
    pass
```

### 4. PEP 8 Naming Conventions

**Rule:** Follow PEP 8 naming conventions strictly.

- **Modules/Files:** `lowercase_with_underscores`
- **Classes:** `PascalCase`
- **Functions/Methods:** `lowercase_with_underscores`
- **Constants:** `UPPERCASE_WITH_UNDERSCORES`
- **Private:** Prefix with `_single_underscore`
- **Dunder:** Use `__double_underscore__` sparingly

✅ Good:
```python
# Module: user_service.py

from typing import List

MAX_LOGIN_ATTEMPTS = 5
DEFAULT_TIMEOUT = 30


class UserService:
    """User management service."""
    
    _cache: dict = {}
    
    def __init__(self) -> None:
        """Initialize service."""
        pass
    
    def create_user(self, username: str) -> bool:
        """Create new user."""
        pass
    
    def _validate_username(self, username: str) -> bool:
        """Validate username format."""
        pass


def fetch_active_users() -> List[dict]:
    """Fetch all active users."""
    pass
```

### 5. Import Organization

**Rule:** Organize imports in standard order with isort.

✅ Good:
```python
# Standard library
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

# Third-party
import requests
from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Local
from app.models import User
from app.utils import hash_password
```

### 6. Code Structure

**Rule:** Keep functions focused and under 50 lines.

✅ Good:
```python
def process_user_data(user_data: dict) -> dict:
    """Process and validate user data.
    
    Args:
        user_data: Raw user input data.
        
    Returns:
        Processed and validated user data.
        
    Raises:
        ValueError: If data validation fails.
    """
    email = _extract_email(user_data)
    password = _validate_password(user_data.get("password"))
    
    return {
        "email": email.lower().strip(),
        "password": password,
        "created_at": datetime.now(),
    }


def _extract_email(data: dict) -> str:
    """Extract and validate email from data."""
    pass


def _validate_password(password: Optional[str]) -> str:
    """Validate password strength."""
    pass
```

---

## Linting Workflow

### Check Code Quality

```bash
# Run ruff (fast, comprehensive)
ruff check .

# Run flake8 (traditional linter)
flake8 .

# Run type checking
mypy .

# Run all checks
make lint
```

### Auto-Fix Issues

```bash
# Auto-fix with ruff
ruff check --fix .

# Format code (if using ruff format)
ruff format .
```

### Makefile Example

```makefile
.PHONY: lint format type-check

lint:
	ruff check .
	flake8 .

format:
	ruff format .
	ruff check --fix .

type-check:
	mypy .

check: lint type-check
```

---

## Pre-commit Hook

Setup automatic checking before commits:

**.pre-commit-config.yaml:**

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.0.280
    hooks:
      - id: ruff
        args: ["--fix"]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.4.1
    hooks:
      - id: mypy
        additional_dependencies:
          - "types-all"

  - repo: https://github.com/PyCQA/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: ["--max-line-length=78"]
```

Install:
```bash
pip install pre-commit
pre-commit install
```

---

## Common Issues & Fixes

### Issue: Lines too long
**Fix:** Break into multiple lines with implicit line continuation.

```python
# Before
result = function_with_long_name(argument_one, argument_two, argument_three)

# After
result = function_with_long_name(
    argument_one,
    argument_two,
    argument_three,
)
```

### Issue: Missing type hints
**Fix:** Add types to all parameters and return values.

```python
# Before
def calculate(x, y):
    return x + y

# After
def calculate(x: float, y: float) -> float:
    return x + y
```

### Issue: Docstring format
**Fix:** Use Google format with proper sections.

```python
# Before
def function(param):
    """Does something with param."""
    pass

# After
def function(param: str) -> None:
    """Do something with parameter.
    
    Args:
        param: Description of parameter.
        
    Raises:
        ValueError: When validation fails.
    """
    pass
```

### Issue: Unused imports
**Fix:** Remove or add `# noqa` if intentional.

```python
# Before
import os
import sys
from datetime import datetime

def main():
    print(sys.version)

# After
import sys

def main():
    print(sys.version)
```

---

## IDE Setup

### VS Code

**.vscode/settings.json:**

```json
{
    "python.linting.enabled": true,
    "python.linting.ruffEnabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "none",
    "[python]": {
        "editor.defaultFormatter": "charliermarsh.ruff",
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.fixAll": true
        }
    },
    "python.linting.mypyEnabled": true,
    "python.linting.mypyArgs": [
        "--strict"
    ]
}
```

### PyCharm

- Settings → Python Code Style → PEP 8
- Settings → Tools → Python Integrated Tools → Default Test Runner: pytest
- Install Ruff plugin from marketplace
- Enable inspections: PEP 8 warnings, Type checking

---

## Enforcement Strategy

When reviewing code or implementing features:

1. **Automatic Checks First**
   - Run `ruff check --fix` to auto-fix issues
   - Run `mypy .` to catch type errors
   - Review remaining warnings

2. **Manual Review**
   - Verify docstring completeness
   - Check type hint accuracy
   - Ensure line lengths
   - Review naming conventions

3. **Documentation**
   - All public functions have docstrings
   - All parameters documented
   - All return types documented
   - Examples provided when helpful

4. **Testing**
   - Type checking passes
   - No lint warnings
   - Code is readable and maintainable

---

## References

- [PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)
- [PEP 484 Type Hints](https://www.python.org/dev/peps/pep-0484/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Flake8 Documentation](https://flake8.pycqa.org/)
- [MyPy Documentation](https://mypy.readthedocs.io/)
