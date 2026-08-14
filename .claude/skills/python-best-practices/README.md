# Python Best Practices Skill

Comprehensive guide for maintaining high-quality Python code following PEP 8, type safety, and documentation standards.

## Quick Start

### 1. Copy Configuration Files

Copy the example configuration files to your project root:

```bash
cp pyproject.toml.example your-project/pyproject.toml
cp .flake8.example your-project/.flake8
cp .pre-commit-config.yaml.example your-project/.pre-commit-config.yaml
cp Makefile.example your-project/Makefile
```

### 2. Install Dependencies

```bash
pip install -e ".[dev]"
# or manually:
pip install ruff flake8 mypy google-code-style pre-commit pytest
```

### 3. Setup Pre-commit Hook

```bash
pre-commit install
```

### 4. Run Quality Checks

```bash
# Check all
make check

# Auto-fix issues
make format fix-all

# Run tests
make test
```

## What's Checked

### Linting (Ruff + Flake8)
- ✓ PEP 8 style compliance
- ✓ Import organization (isort)
- ✓ Naming conventions (PEP 8)
- ✓ Code simplification
- ✓ Common bugs detection
- ✓ Comprehension improvements
- ✓ Performance issues
- ✓ Logging best practices

### Type Checking (MyPy)
- ✓ Type hint coverage
- ✓ Type consistency
- ✓ Optional/None handling
- ✓ Generic type parameters

### Docstrings (PyDocStyle)
- ✓ Google-style format
- ✓ Proper sections
- ✓ Parameter documentation
- ✓ Return type documentation

### Line Length
- ✓ Maximum 78 characters per line
- ✓ Implicit line continuation in parentheses
- ✓ String concatenation on multiple lines

## Key Standards

### Type Hints (Required)

Every function and class attribute must have type hints:

```python
def process(data: dict) -> str:
    """Process data and return result."""
    return str(data)

class Config:
    """Application configuration."""
    
    timeout: int = 30
    debug: bool = False
```

### Docstrings (Google Style)

All functions, classes, and modules need Google-style docstrings:

```python
def fetch_user(user_id: int) -> Optional[dict]:
    """Fetch user by ID from database.
    
    Args:
        user_id: The user's unique identifier.
        
    Returns:
        User data dictionary, or None if not found.
        
    Raises:
        ValueError: If user_id is negative.
        
    Example:
        >>> user = fetch_user(123)
        >>> user["name"]
        "John Doe"
    """
    pass
```

### Line Length: 78 Characters

Use implicit line continuation:

```python
# ✓ Good
result = function(
    arg1,
    arg2,
    arg3,
)

message = (
    "Line one "
    "line two "
    "line three"
)

# ✗ Bad - exceeds 78 chars
result = function(arg1, arg2, arg3)
```

### Naming Conventions

- **Modules**: `lowercase_with_underscores`
- **Classes**: `PascalCase`
- **Functions**: `lowercase_with_underscores`
- **Constants**: `UPPERCASE_WITH_UNDERSCORES`
- **Private**: `_leading_underscore`

```python
# ✓ Good naming
MAX_RETRIES = 3

class UserService:
    def __init__(self) -> None:
        self._cache: dict = {}
    
    def get_user(self, user_id: int) -> Optional[dict]:
        pass

# ✗ Bad naming
MAX = 3

class userService:
    def __init__(self):
        self.cache = {}
    
    def GetUser(self, UserId):
        pass
```

## Commands

### Quality Checks

```bash
# Run all linters
make lint

# Type checking only
make type-check

# Combined check
make check
```

### Auto-fixing

```bash
# Auto-format and fix
make format fix-all

# Ruff auto-fix only
ruff check --fix .

# Format only
ruff format .
```

### Testing

```bash
# Run tests
make test

# With coverage
make test-cov
```

### Cleanup

```bash
# Remove cache files
make clean
```

## File Structure

Example project structure:

```
project/
├── src/
│   └── app/
│       ├── __init__.py
│       ├── models.py           # Type hints, docstrings
│       ├── services.py         # Business logic
│       └── utils.py            # Utilities
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   └── test_services.py
├── Makefile                     # Build commands
├── pyproject.toml               # Project config
├── .flake8                      # Flake8 config
├── .pre-commit-config.yaml      # Pre-commit hooks
└── README.md
```

## IDE Integration

### VS Code

Install [Ruff extension](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff)

**.vscode/settings.json:**

```json
{
    "[python]": {
        "editor.defaultFormatter": "charliermarsh.ruff",
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.fixAll": true
        }
    },
    "python.linting.mypyEnabled": true
}
```

### PyCharm

1. Settings → Python Code Style → PEP 8
2. Settings → Tools → Python Integrated Tools → Test Runner: pytest
3. Install Ruff plugin from marketplace
4. Enable inspections: PEP 8, Type checking

## Common Issues & Solutions

### Error: Line too long
**Solution:** Break into multiple lines
```python
# Before
result = some_function(arg1, arg2, arg3, arg4, arg5)

# After
result = some_function(
    arg1,
    arg2,
    arg3,
    arg4,
    arg5,
)
```

### Error: Missing type hints
**Solution:** Add type annotations
```python
# Before
def calculate(x, y):
    return x + y

# After
def calculate(x: float, y: float) -> float:
    return x + y
```

### Error: Unused import
**Solution:** Remove it or add noqa comment
```python
import sys  # noqa: F401 (if intentionally unused)
```

### Error: Missing docstring
**Solution:** Add Google-style docstring
```python
def process(data: dict) -> None:
    """Process input data.
    
    Args:
        data: Dictionary containing configuration.
    """
    pass
```

## Testing Integration

Example pytest configuration in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = "-v --tb=short"
```

Run tests:
```bash
pytest                  # Run all
pytest tests/test_models.py  # Specific file
pytest -k "test_user"  # Specific test
pytest --cov=src       # With coverage
```

## References

- [PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)
- [PEP 484 Type Hints](https://www.python.org/dev/peps/pep-0484/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [MyPy Documentation](https://mypy.readthedocs.io/)

## Support

For questions about the standards in this skill, refer to:
- SKILL.md - Detailed documentation
- pyproject.toml.example - Configuration template
- Makefile.example - Common commands

See also: `/python-best-practices` skill documentation
