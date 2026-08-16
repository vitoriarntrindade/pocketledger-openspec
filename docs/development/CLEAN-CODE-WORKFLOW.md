# Workflow: Escrever Código "Limpo" desde o Início

> [!IMPORTANT]
> **Superseded — read [`docs/agentic-development.md`](../agentic-development.md) first.**
>
> This document was written against a pipeline that was never installed. It
> refers to commands and layouts that do not work as described:
>
> - `make check` had no `Makefile` behind it; the gate is now `make quality`.
> - ruff, mypy, flake8 and pre-commit were documented but not installed.
> - `.claude/claude.md` was lowercase and so was likely never loaded; the
>   project constitution is now `CLAUDE.md` in the repository root.
> - `openspec/changes/active/` is not a layout OpenSpec 1.8 recognises; changes
>   live directly under `openspec/changes/<name>/`.
> - flake8 and pydocstyle have been retired; ruff is the single authority.
>
> It is kept for its background and reasoning, which remain useful. Where it
> disagrees with `CLAUDE.md` or `docs/agentic-development.md`, those win.

Este guia mostra como usar a skill `/python-best-practices` e templates durante o desenvolvimento, para que código **nasça** seguindo padrões de qualidade.

## 🎯 Princípios

1. **Pre-commit Hooks** - Bloqueiam dano irreversível antes de commitar
   (segredos, arquivos grandes, `.env` real); lint e type checking rodam em
   `make quality`, não aqui
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

### Passo 3: Antes de Commitar - Rodar o Gate Localmente

```bash
make quality   # format, lint, typecheck, testes, coverage, security,
                # secret scan, validação OpenSpec — a definição de pronto

# Pre-commit roda à parte, no git commit, e cobre só dano irreversível
# (segredos, arquivos grandes, conflitos de merge, .env real)
git add .
git commit -m "feat: add new feature"
```

### Passo 4: Se `make quality` Falhou

```bash
# Autofix seguro, depois roda o gate completo de novo
make fix

# Revisar o que sobrou
git diff
git add .
git commit -m "feat: add new feature"
```

### Passo 5: Commit Sucesso ✓

```bash
# make quality passou = código já está:
# ✓ Formatado (78 chars, PEP 8, ruff format)
# ✓ Tipado (mypy aceita)
# ✓ Sem issues (ruff check pass)
# ✓ Documentado (docstrings presentes)

git push origin feature/add-new-feature
```

## 🛠️ Pre-commit Hooks - O Que Roda Automaticamente

Quando você faz `git commit`, o `.pre-commit-config.yaml` deste projeto roda
apenas checagens contra dano irreversível — não lint, não type checking:

```yaml
1. detect-private-key      # Bloqueia chaves privadas commitadas
2. check-added-large-files # Bloqueia arquivos grandes por engano
3. check-merge-conflict    # Bloqueia marcadores de conflito não resolvidos
4. no-real-env-file        # Bloqueia um .env real sendo commitado
```

Ruff e mypy já rodam a cada edição do agente e de novo em `make quality` e na
CI; repeti-los no commit só tornaria o commit lento o bastante para as
pessoas caírem no `--no-verify`.

**Se algo falhar:**
- ❌ Commit bloqueado
- 📝 Mostra o problema
- ⏸️ Você corrige e re-tenta

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
# Type checking
mypy app/api/routers/posts.py

# Linting (ruff é a autoridade única — substitui o flake8)
ruff check app/api/routers/posts.py
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
✓ detect-private-key
✓ check-added-large-files
✓ check-merge-conflict
✓ no-real-env-file
✓ All checks passed!

[feature/add-posts 1a2b3c4] feat: add posts endpoint
 1 file changed, 150 insertions(+)
```

## 🔍 Validação Completa

Antes de pull request, rodar:

```bash
# Tudo junto — a definição de pronto
make quality

# Ou individual
make lint        # ruff
make typecheck    # mypy
make test         # pytest, sobe o PostgreSQL antes
```

## 📚 Recursos Disponíveis

| Arquivo | Uso |
|---------|-----|
| `BEST_PRACTICES.md` | Padrões + exemplos |
| `.claude/templates/router.py.template` | Template router |
| `.claude/templates/service.py.template` | Template service |
| `pyproject.toml` | Configuração (ruff — autoridade única de lint — e mypy) |
| `.pre-commit-config.yaml` | Git hooks (só dano irreversível) |

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
