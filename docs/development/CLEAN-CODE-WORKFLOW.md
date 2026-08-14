# Workflow: Escrever Código "Limpo" desde o Início

Este guia mostra como usar a skill `/python-best-practices` e templates durante o desenvolvimento, para que código **nasça** seguindo padrões de qualidade.

## 🎯 Princípios

1. **Pre-commit Hooks** - Validam código antes de commitar
2. **Templates** - Estrutura pronta com padrões corretos
3. **Type Hints** - Obrigatório desde a escrita
4. **Docstrings** - Documentação simultânea
5. **Auto-format** - Ruff formata automaticamente

## 📝 Workflow Passo a Passo

### Passo 1: Criar Feature Branch

```bash
git checkout -b feature/add-new-feature
```

### Passo 2: Criar Novo Componente (Router, Service, etc)

**Opção A: Usar Template**

```bash
# Para novo router
cp .claude/templates/router.py.template app/api/routers/new_feature.py

# Para novo service  
cp .claude/templates/service.py.template app/services/new_feature_service.py

# Depois editar: substituir {{ModelNamePascal}}, etc
```

**Opção B: Criar do Zero com Padrões**

```python
# ✅ CORRETO - Já nascer com:
# - Type hints em tudo
# - Docstring Google style
# - Max 78 caracteres
# - PEP 8 compliance

from typing import Optional
from sqlalchemy.orm import Session

from app.models.user import User
from app.core.errors import NotFoundError


def get_user_by_email(
    db: Session,
    email: str,
) -> Optional[User]:
    """Get user by email address.
    
    Args:
        db: Database session.
        email: User email to search.
        
    Returns:
        User if found, None otherwise.
    """
    return (
        db.query(User)
        .filter(User.email == email)
        .first()
    )
```

### Passo 3: Antes de Commitar - Rodar Checks Locais

```bash
source .venv/bin/activate

# Pre-commit faz isso automaticamente:
git add .
git commit -m "feat: add new feature"

# Se houver erros, pre-commit:
# 1. Mostra os problemas
# 2. Auto-formata (ruff)
# 3. Deixa você revisar e re-adicionar
```

### Passo 4: Se Pre-commit Bloqueou

```bash
# Revisar erros
git diff

# Re-adicionar após correções
git add .
git commit -m "feat: add new feature"
```

### Passo 5: Commit Sucesso ✓

```bash
# Pre-commit passou = Código já está:
# ✓ Formatado (78 chars, PEP 8)
# ✓ Tipado (mypy aceita)
# ✓ Sem issues (ruff/flake8 pass)
# ✓ Documentado (docstrings presentes)

git push origin feature/add-new-feature
```

## 🛠️ Pre-commit Hooks - O Que Roda Automaticamente

Quando você faz `git commit`, roda automaticamente:

```yaml
1. ruff check --fix      # Formata + arruma issues
2. ruff-format           # Formata código
3. mypy                  # Type checking
4. flake8                # PEP 8
5. pydocstyle            # Docstrings
6. trailing-whitespace   # Remove espaços extras
7. check-ast             # Valida Python syntax
```

**Se algo falhar:**
- ❌ Commit bloqueado
- 📝 Mostra problemas
- 🔧 Algumas coisas já são corrigidas (ruff)
- ⏸️ Você revisa e re-tenta

## 📋 Exemplo Prático: Adicionar Novo Router

### 1. Copiar template

```bash
cp .claude/templates/router.py.template \
   app/api/routers/posts.py
```

### 2. Editar (substituir placeholders)

```python
# Antes
from app.schemas.{{model_name_lower}} import ...

# Depois
from app.schemas.post import PostCreate, PostOut, PostUpdate
```

### 3. Testar antes de commitar

```bash
source .venv/bin/activate

# Type checking
mypy app/api/routers/posts.py

# Linting
ruff check app/api/routers/posts.py
flake8 app/api/routers/posts.py
```

### 4. Commitar

```bash
git add app/api/routers/posts.py
git commit -m "feat: add posts endpoint

- Create, read, update, delete posts
- Full type safety with Pydantic
- Google-style docstrings"
```

### 5. Pre-commit valida e aceita

```
✓ ruff check
✓ ruff-format  
✓ mypy
✓ flake8
✓ pydocstyle
✓ All checks passed!

[feature/add-posts 1a2b3c4] feat: add posts endpoint
 1 file changed, 150 insertions(+)
```

## 🔍 Validação Completa

Antes de pull request, rodar:

```bash
# Tudo junto
make check

# Ou individual
make lint        # ruff + flake8
make type-check  # mypy
make test        # pytest
```

## 📚 Recursos Disponíveis

| Arquivo | Uso |
|---------|-----|
| `BEST_PRACTICES.md` | Padrões + exemplos |
| `.claude/templates/router.py.template` | Template router |
| `.claude/templates/service.py.template` | Template service |
| `pyproject.toml` | Configuração (ruff, mypy) |
| `.flake8` | Configuração (flake8) |
| `.pre-commit-config.yaml` | Git hooks |

## ⚡ Quick Reference

### Type Hints

```python
# ✅ ALWAYS
def process(data: dict) -> str:
    """Process data and return string."""
    return str(data)

# ❌ NEVER
def process(data):
    return str(data)
```

### Docstrings (Google Style)

```python
def calculate_total(
    prices: list[float],
    tax_rate: float,
) -> float:
    """Calculate total with tax.
    
    Args:
        prices: List of item prices.
        tax_rate: Tax rate as decimal.
        
    Returns:
        Total including tax.
        
    Example:
        >>> calculate_total([10.0, 20.0], 0.1)
        33.0
    """
    return sum(prices) * (1 + tax_rate)
```

### Line Length (Max 78)

```python
# ❌ 90 chars - too long
def create_item(name: str, description: str, category_id: int, user_id: int) -> ItemOut:

# ✅ Broken correctly
def create_item(
    name: str,
    description: str,
    category_id: int,
    user_id: int,
) -> ItemOut:
```

### Exception Chaining

```python
# ✅ Shows full traceback
try:
    validate(data)
except ValidationError as err:
    raise ProcessError("Failed") from err

# ❌ Loses context
except ValidationError:
    raise ProcessError("Failed")
```

## 🚀 Integração com IDE

### VS Code

Arquivo `.vscode/settings.json`:

```json
{
    "[python]": {
        "editor.defaultFormatter": "charliermarsh.ruff",
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.fixAll": true
        }
    }
}
```

### PyCharm

1. Settings → Python Code Style → PEP 8
2. Settings → Tools → Python Integrated Tools
3. Install Ruff plugin

## 📊 Resultado

Seguindo este workflow:

- ✅ 100% tipo-seguro
- ✅ 100% PEP 8 compliant
- ✅ 100% documentado
- ✅ Sem surpresas em code review
- ✅ Sem refatorações depois
- ✅ Código pronto para produção

## 🔄 Para Cada Nova Feature

```
1. Criar branch
   └─ git checkout -b feature/...

2. Usar template ou seguir padrões
   └─ cp .claude/templates/*.template ...

3. Pre-commit valida
   └─ git commit (automático)

4. Code review + merge
   └─ Sem surpresas de qualidade!
```

---

**Status:** ✅ Padrões estabelecidos  
**Setup:** ✅ Pre-commit ativo  
**Templates:** ✅ Disponíveis  
**Documentação:** ✅ Completa
