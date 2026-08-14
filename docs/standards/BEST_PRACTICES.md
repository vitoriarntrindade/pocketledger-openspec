# Boas Práticas Python - PocketLedger

Este projeto segue as boas práticas Python definidas pela skill `/python-best-practices`.

## 🚀 Quick Start

### Verificar Qualidade
```bash
source .venv/bin/activate
make check                    # Ruff + Flake8 + MyPy
make lint                     # Apenas linters
make type-check              # Apenas MyPy
```

### Auto-Corrigir Problemas
```bash
source .venv/bin/activate
make fix-all                 # Auto-fix tudo que conseguir
ruff check app --fix         # Só ruff
ruff format app              # Formatar código
```

### Rodar Testes
```bash
source .venv/bin/activate
make test                    # Testes simples
make test-cov               # Com coverage
```

---

## 📋 Padrões Obrigatórios

### 1. Type Hints (OBRIGATÓRIO)
Toda função e classe deve ter type hints.

```python
from typing import Optional, List

def process_transactions(
    transactions: List[dict],
    user_id: int,
) -> Optional[str]:
    """Process user transactions.
    
    Args:
        transactions: List of transaction dicts.
        user_id: User identifier.
        
    Returns:
        Result message or None if empty.
    """
    if not transactions:
        return None
    
    return f"Processed {len(transactions)} transactions"
```

### 2. Google-Style Docstrings
```python
def authenticate(
    email: str,
    password: str,
) -> User:
    """Authenticate user by email and password.
    
    Args:
        email: User's email address.
        password: Plain text password.
        
    Returns:
        Authenticated User object.
        
    Raises:
        UnauthorizedError: If credentials invalid.
        
    Example:
        >>> user = authenticate("user@example.com", "pass123")
        >>> user.email
        "user@example.com"
    """
    pass
```

### 3. Máximo 78 Caracteres por Linha
```python
# ❌ ERRADO - 86 caracteres
@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)

# ✅ CORRETO
@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
)
```

### 4. PEP 8 Naming
- Módulos: `lowercase_with_underscores`
- Classes: `PascalCase`
- Funções: `lowercase_with_underscores`
- Constantes: `UPPERCASE_WITH_UNDERSCORES`
- Privadas: `_leading_underscore`

```python
# Constants
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30

# Classes
class UserRepository:
    def get_user(self, user_id: int) -> Optional[User]:
        pass
    
    def _validate_id(self, user_id: int) -> bool:
        pass

# Functions
def fetch_active_users() -> List[User]:
    pass
```

### 5. Import Organization
```python
# Standard library
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

# Third-party
import jwt
from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine

# Local
from app.models import User
from app.schemas import UserOut
from app.core.config import settings
```

---

## ⚠️ Problemas Atuais

### P0 - CRÍTICO
1. **Type Mismatches** - ORM models sendo retornados como schemas
   - Afeta: auth, transactions, categories, users routers
   - Solução: `UserOut.model_validate(user)`

2. **Circular Imports** - models/user.py, transaction.py, category.py
   - Solução: usar TYPE_CHECKING para imports circulares

### P1 - IMPORTANTE
3. **Linhas Muito Longas** - 73 linhas com >78 caracteres
   - Afeta: routers, models, error_handlers
   - Solução: quebrar em múltiplas linhas

4. **Exception Chaining** - faltam `from err` em handlers
   - Afeta: api/deps.py, services/category_service.py

---

## 📊 Current Status

```
RUFF:  52 issues (12 fixados, 40 remanescentes)
  • 28 B008 (FastAPI Depends - ACEITAR)
  • 6  F821 (undefined names - CORRIGIR)
  • 2  B904 (exception chain - CORRIGIR)

FLAKE8: 73 E501 (linhas muito longas)
  • Quebrar decoradores e long imports

MYPY:  26 type errors
  • 12 type mismatches (ORM vs Schema) - CRÍTICO
  • 6  circular refs - IMPORTANTE
  • 8  missing annotations - IMPORTANTE
```

Detalhes completos: [QUALITY_REPORT.md](QUALITY_REPORT.md)

---

## 🔧 Configuração

Já está pronta:
- ✅ `pyproject.toml` - Ruff, MyPy, Coverage
- ✅ `.flake8` - Flake8 config
- ✅ `.pre-commit-config.yaml` - Git hooks
- ✅ `Makefile` - Comandos úteis

### Setup Pre-commit
```bash
source .venv/bin/activate
pip install pre-commit
pre-commit install
```

Agora roda automaticamente:
- Ruff lint & format
- MyPy type checking
- Flake8 validation

---

## 📚 Referências

- [PEP 8](https://www.python.org/dev/peps/pep-0008/) - Python Style Guide
- [PEP 484](https://www.python.org/dev/peps/pep-0484/) - Type Hints
- [Ruff Docs](https://docs.astral.sh/ruff/)
- [MyPy Docs](https://mypy.readthedocs.io/)

---

## 💡 Tips

### Auto-format Before Commit
```bash
make fix-all && make check
```

### Quick Type Check
```bash
mypy app --ignore-missing-imports
```

### View All Issues
```bash
ruff check app --show-fixes
```

### IDE Integration
- VS Code: Install Ruff extension
- PyCharm: Install Ruff plugin + enable inspections

---

## ❓ FAQ

**P: Preciso colocar type hints em tudo?**  
R: Sim! Pelo menos em argumentos e return types. Type hints ajudam MyPy e IDEs.

**P: E linhas muito longas?**  
R: Max 78 chars. Quebra em múltiplas linhas usando parentheses implícitas.

**P: FastAPI Depends() em defaults é erro?**  
R: Não! B008 em FastAPI é padrão válido. Ruff ignora isso.

**P: Como corrigir circular imports?**  
R: Use TYPE_CHECKING para imports que causam círculos.

---

**Skill:** `/python-best-practices`  
**Status:** ✅ Configurada e Pronta  
**Última Atualização:** 2026-08-13
