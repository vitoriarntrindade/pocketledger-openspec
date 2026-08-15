# 🚀 Adicionando Novas Features com Código "Limpo"

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

**Objetivo:** Código já nasça tipado, documentado, seguindo PEP 8 - sem refatoração depois.

## ⚡ Quick Start (5 minutos)

### 1. Criar Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Usar Template para Novo Componente

```bash
# Para novo router (endpoint)
.claude/scripts/generate-component.sh router your_feature

# Para novo serviço (lógica)
.claude/scripts/generate-component.sh service your_feature
```

### 3. Editar e Implementar

O template já vem com:
- ✅ Type hints completos
- ✅ Docstrings (Google style)
- ✅ PEP 8 estrutura
- ✅ Max 78 caracteres

### 4. Commitar (Pre-commit Valida)

```bash
git add .
git commit -m "feat: add your feature"
# Pre-commit roda automaticamente, mas só cobre dano irreversível
# (segredos, arquivos grandes, .env real) — não lint nem type checking.

# Antes de abrir o PR, rode o gate completo:
make quality
```

### 5. Ready! ✓

`make quality` passou = pronto para production!

---

## 📋 Padrões Essenciais

### ✅ SEMPRE Fazer

```python
from typing import Optional, List


def get_user(user_id: int) -> Optional[User]:
    """Get user by ID.

    Args:
        user_id: User identifier.

    Returns:
        User if found, None otherwise.
    """
    # implementation
    pass
```

### ❌ NUNCA Fazer

```python
# Sem type hints
def get_user(user_id):
    return user  # Wrong!

# Linha muito longa (>78 chars)
def create_item(name: str, description: str, category_id: int) -> ItemOut:

# Sem docstring
def process_data(data):
    pass
```

---

## 🛠️ Templates Disponíveis

| Template | Localização | Uso |
|----------|-------------|-----|
| Router | `.claude/templates/router.py.template` | API endpoints |
| Service | `.claude/templates/service.py.template` | Business logic |

**Como usar:**

```bash
cp .claude/templates/router.py.template app/api/routers/new_router.py

# Editar: substituir {{ModelNamePascal}}, {{model_name_lower}}, etc
```

---

## 🔍 Validação Automática

### Pre-commit Hooks

Cada commit roda automaticamente, mas cobre só dano irreversível:

1. **detect-private-key** - Bloqueia chaves privadas
2. **check-added-large-files** - Bloqueia arquivos grandes por engano
3. **check-merge-conflict** - Bloqueia marcadores de conflito
4. **no-real-env-file** - Bloqueia um `.env` real sendo commitado

Lint, type checking e formatação **não** rodam aqui — já rodam a cada edição
do agente, em `make quality`, e de novo na CI.

**Se algo falhar:**
- ⏸️ Commit bloqueado
- 📝 Você vê o problema
- 🔁 Depois de corrigir: `git commit` novamente

### Verificação Manual

```bash
# Tudo junto — a definição de pronto
make quality

# Ou individual
make lint           # ruff
make typecheck      # mypy
make test           # pytest, sobe o PostgreSQL antes
```

---

## 📚 Recursos

| Arquivo | Conteúdo |
|---------|----------|
| `BEST_PRACTICES.md` | Padrões + exemplos detalhados |
| `CLEAN-CODE-WORKFLOW.md` | Workflow completo |
| `pyproject.toml` | Config (ruff, mypy) |
| `.pre-commit-config.yaml` | Git hooks |

---

## 🎯 Checklist: Nova Feature

- [ ] Criar branch: `git checkout -b feature/...`
- [ ] Usar template: `.claude/scripts/generate-component.sh ...`
- [ ] Type hints em **tudo**
- [ ] Docstrings (Google style)
- [ ] Max 78 caracteres por linha
- [ ] Commitar: `git commit`
- [ ] Pre-commit passou? ✓
- [ ] Ready para code review!

---

## 💡 Exemplos Rápidos

### Type Hints

```python
# ✅ Correto
def calculate(
    prices: list[float],
    tax_rate: float,
) -> float:
    """Calculate total with tax."""
    return sum(prices) * (1 + tax_rate)
```

### Docstrings

```python
def create_user(
    email: str,
    password: str,
) -> User:
    """Create new user account.
    
    Args:
        email: User email address.
        password: Plain text password (will be hashed).
        
    Returns:
        Created user object.
        
    Raises:
        ConflictError: If email already registered.
    """
    # implementation
    pass
```

### Line Length (78 chars max)

```python
# ❌ 92 characters - BAD
def create_user(email: str, password: str, name: str, phone: str) -> User:

# ✅ Broken correctly - GOOD  
def create_user(
    email: str,
    password: str,
    name: str,
    phone: str,
) -> User:
```

---

## ✅ Resultado

Seguindo este processo:

- ✅ Código tipado desde o início
- ✅ Documentado já na escrita
- ✅ Sem refatorações depois
- ✅ Code review é simples
- ✅ Production-ready na primeira tentativa

---

**Dúvidas?** Veja `BEST_PRACTICES.md` ou `CLEAN-CODE-WORKFLOW.md`
