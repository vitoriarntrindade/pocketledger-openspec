# Boas Práticas Python - PocketLedger

Este projeto segue as boas práticas Python definidas pela skill `/python-best-practices`.

## 🚀 Quick Start

### Verificar Qualidade
```bash
make quality                  # o gate completo: format, lint, typecheck,
                               # testes, coverage, security, secret scan,
                               # validação OpenSpec — a definição de pronto
make fast                     # checks estáticos e rápidos (format, lint,
                               # typecheck, secret scan, openspec validate),
                               # sem testes — para o loop de edição
make lint                     # só ruff
make typecheck                # só mypy
```

### Auto-Corrigir Problemas
```bash
make fix                      # aplica autofixes seguros e roda o gate
                               # completo em seguida
ruff check . --fix            # só ruff
ruff format .                 # formatar código
```

### Rodar Testes
```bash
make test                    # Suite completa com coverage e o piso de 95%
                              # (sobe o PostgreSQL antes)
make test-cov                # Igual, e também grava o relatório HTML em
                              # htmlcov/
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

## ⚠️ Status Atual

O baseline de qualidade descrito em
[`docs/reports/QUALITY_REPORT.md`](../reports/QUALITY_REPORT.md) — tipos
incompatíveis (ORM vs. schema), imports circulares, linhas longas e exception
chaining faltando — foi corrigido pela change
`2026-08-15-refactor-python-quality-baseline` (commit `c5ab5bc`). `make
quality` roda limpo: sem findings de ruff, mypy ou bandit.

Qualquer nova violação encontrada por `make quality` deve ser corrigida na
mesma change que a introduziu — ver CLAUDE.md §1: um gate falhando nunca é
resolvido enfraquecendo o gate.

---

## 🔧 Configuração

Já está pronta:
- ✅ `pyproject.toml` - Ruff (linter e formatter, autoridade única) e MyPy
- ✅ `.pre-commit-config.yaml` - Git hooks
- ✅ `Makefile` - Comandos úteis

Não há um segundo arquivo de configuração de lint (`.flake8` ou similar):
ruff substitui o flake8 por completo, incluindo a checagem de complexidade
(regra `C901`).

### Setup Pre-commit
```bash
make install
```

O hook de pre-commit cobre apenas dano irreversível em tempo de commit —
segredos, arquivos grandes, conflitos de merge não resolvidos e um `.env`
real sendo commitado. Ele **não** roda ruff/mypy: essas checagens já rodam a
cada edição do agente, em `make quality` e novamente na CI, então uma
quarta cópia só tornaria o commit lento o bastante para as pessoas caírem no
`--no-verify`.

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
make fix
```

### Quick Type Check
```bash
make typecheck
```

### View All Issues
```bash
ruff check . --show-fixes
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
