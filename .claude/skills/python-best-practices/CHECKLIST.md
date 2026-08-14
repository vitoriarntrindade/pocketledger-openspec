# Python Best Practices Checklist

Quick reference checklist for code review and implementation.

## Before Committing Code

### ✓ Type Hints
- [ ] All function parameters have type hints
- [ ] All return types are specified
- [ ] Class attributes have type annotations
- [ ] Used `Optional[T]` for nullable values
- [ ] Used `Union[T, U]` for multiple types
- [ ] No `Any` without justification

### ✓ Docstrings (Google Style)
- [ ] Module has module-level docstring
- [ ] All classes have docstrings
- [ ] All public functions have docstrings
- [ ] Docstrings use Google format
- [ ] Args section documents parameters
- [ ] Returns section documents return value
- [ ] Raises section documents exceptions
- [ ] Examples provided for complex functions

### ✓ Line Length (78 characters)
- [ ] No line exceeds 78 characters
- [ ] Long function calls broken across lines
- [ ] Long strings use implicit continuation
- [ ] Long lists/dicts broken across lines
- [ ] Long imports use parentheses

### ✓ Naming Conventions
- [ ] Modules: `lowercase_with_underscores`
- [ ] Classes: `PascalCase`
- [ ] Functions: `lowercase_with_underscores`
- [ ] Constants: `UPPERCASE_WITH_UNDERSCORES`
- [ ] Private: `_leading_underscore`
- [ ] No single letter variables (except i, j, k in loops)

### ✓ Code Organization
- [ ] Imports organized: stdlib, third-party, local
- [ ] Imports sorted alphabetically
- [ ] Related imports grouped together
- [ ] Unused imports removed
- [ ] Functions under 50 lines
- [ ] Classes under 200 lines

### ✓ PEP 8 Compliance
- [ ] 4-space indentation (not tabs)
- [ ] 2 blank lines between top-level items
- [ ] 1 blank line between class methods
- [ ] No trailing whitespace
- [ ] Proper spacing around operators

## Linting Tools

### Run Before Commit
```bash
# Ruff (fast comprehensive linter)
ruff check . --fix

# Flake8 (traditional linter)
flake8 .

# Type checking
mypy . --ignore-missing-imports

# Or all together
make check
```

### Auto-format Code
```bash
# Ruff formatter
ruff format .

# Fix issues
ruff check . --fix
```

## Common Issues Checklist

### Functions
- [ ] Has type hints on all parameters
- [ ] Has return type annotation
- [ ] Has docstring with Args/Returns/Raises
- [ ] Under 50 lines of code
- [ ] Single responsibility principle

### Classes
- [ ] Has class-level docstring
- [ ] Has `__init__` with type hints
- [ ] Attributes have type annotations
- [ ] Methods have return type hints
- [ ] Private methods prefixed with `_`

### Docstrings
- [ ] First line is summary (under 79 chars)
- [ ] Blank line after summary
- [ ] Args section formatted correctly
- [ ] Returns section formatted correctly
- [ ] Raises section if applicable
- [ ] Examples section if helpful

### Imports
- [ ] Organized by category (stdlib, 3rd, local)
- [ ] Alphabetically sorted within category
- [ ] No unused imports
- [ ] No circular imports
- [ ] Specific imports (not `import *`)

### Variables
- [ ] Lowercase with underscores
- [ ] Descriptive names (>3 chars usually)
- [ ] No ambiguous names (l, O, I)
- [ ] Constants in UPPERCASE
- [ ] Type hints on class attributes

## Before Pushing to Repository

### Final Checks
- [ ] All linting passes (`make lint`)
- [ ] Type checking passes (`make type-check`)
- [ ] Tests pass (`make test`)
- [ ] No warnings or errors in output
- [ ] Code follows all style guidelines

### Pre-commit Hook
If using pre-commit:
```bash
pre-commit run --all-files
```

Should produce:
```
ruff ..................... PASSED
ruff-format .............. PASSED
mypy ..................... PASSED
flake8 ................... PASSED
trailing-whitespace ...... PASSED
end-of-file-fixer ........ PASSED
check-yaml ............... PASSED
```

## Code Review Questions

Ask yourself these questions before submitting:

### Correctness
- [ ] Does the code do what it's supposed to?
- [ ] Are all edge cases handled?
- [ ] Are exceptions caught and handled?
- [ ] Is error handling appropriate?

### Clarity
- [ ] Would another developer understand this?
- [ ] Are variable names clear and descriptive?
- [ ] Are complex operations commented?
- [ ] Is the docstring accurate?

### Efficiency
- [ ] Any obvious performance issues?
- [ ] Unnecessary loops or recursion?
- [ ] Proper data structures used?
- [ ] No N+1 query problems?

### Security
- [ ] No SQL injection vulnerabilities?
- [ ] No hardcoded secrets/passwords?
- [ ] Proper input validation?
- [ ] No unsafe file operations?

### Testing
- [ ] Are edge cases tested?
- [ ] Is error handling tested?
- [ ] Do tests verify the expected behavior?
- [ ] Are tests independent and isolated?

## Example Compliance

### ✗ Before (Multiple Issues)
```python
def get_user_data(id,cached=False):
    # Get user from database
    from models import User
    u = User.query.filter_by(id=id).first()
    return u
```

### ✓ After (Best Practices)
```python
"""User data retrieval module."""

from typing import Optional

from models import User


def get_user_data(
    user_id: int,
    cached: bool = False,
) -> Optional[dict]:
    """Get user data by ID.
    
    Args:
        user_id: User's unique identifier.
        cached: Use cached result if available.
        
    Returns:
        User data dictionary or None if not found.
    """
    user = User.query.filter_by(id=user_id).first()
    return user.to_dict() if user else None
```

## Tools Used

| Tool | Purpose | Command |
|------|---------|---------|
| ruff | Fast linter & formatter | `ruff check .` |
| flake8 | PEP 8 compliance | `flake8 .` |
| mypy | Type checking | `mypy .` |
| black/ruff-format | Code formatting | `ruff format .` |
| isort/ruff | Import sorting | `ruff check --fix .` |
| pre-commit | Git hooks | `pre-commit run --all` |

## References

- [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- [PEP 484 - Type Hints](https://www.python.org/dev/peps/pep-0484/)
- [Google Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Ruff Docs](https://docs.astral.sh/ruff/)
- [MyPy Docs](https://mypy.readthedocs.io/)

## Quick Command Reference

```bash
# Check everything
make check              # lint + type-check

# Auto-fix issues
make fix-all            # format + ruff fix

# Setup
make install-dev        # Install dependencies
make pre-commit          # Setup git hooks

# Testing
make test               # Run tests
make test-cov           # Tests with coverage

# Cleanup
make clean              # Remove cache files
```

---

**Last Updated:** 2024
**Skill:** python-best-practices v1.0
