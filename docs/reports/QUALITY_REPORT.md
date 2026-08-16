# Python Code Quality Report

> [!NOTE]
> **Resolvido.** Todos os achados abaixo (type mismatches, circular
> imports, linhas longas, exception chaining) foram corrigidos pela change
> `2026-08-15-refactor-python-quality-baseline` (commit `c5ab5bc`). `make
> quality` roda limpo hoje. Este documento é mantido como registro histórico
> do estado em 2026-08-13 — ver
> [`standards/BEST_PRACTICES.md`](../standards/BEST_PRACTICES.md) para o
> estado atual e os comandos corretos.

**Data:** 2026-08-13  
**Projeto:** pocketledger-openspec  
**Status:** ⚠️ Requer correções (na época; ver nota acima)

---

## 📊 Resumo Executivo

| Ferramenta | Problemas | Fixados | Restantes |
|-----------|-----------|---------|-----------|
| **Ruff** (Linter) | 52 | 12 | 40 |
| **Flake8** (PEP 8) | 73 E501 | - | 73 |
| **MyPy** (Types) | 26 | 0 | 26 |

**Arquivos Analisados:** 40 Python files (14 app/ + 26 tests/)

---

## 🔴 Problemas Críticos

### 1. Type Mismatches (12 erros) - CRÍTICO
**Impacto:** Pode causar falhas em runtime  
**Problema:** Retornando ORM models em vez de Pydantic schemas

```python
# ❌ ERRADO
@router.post("/register", response_model=UserOut)
def register(payload: RegisterRequest) -> UserOut:
    user = auth_service.register_user(db, ...)
    return user  # user é User, não UserOut!
```

**Solução:**
```python
# ✅ CORRETO
from app.schemas.user import UserOut

return UserOut.model_validate(user)
```

**Arquivos Afetados:**
- `app/api/routers/auth.py`
- `app/api/routers/transactions.py`
- `app/api/routers/categories.py`
- `app/api/routers/users.py`

---

### 2. Circular Imports (6 erros)
**Problema:** Forward references não resolvidas

```python
# ❌ app/models/user.py:21
transactions: Mapped[list["Transaction"]] = ...
# NameError: "Transaction" não está no escopo
```

**Solução com TYPE_CHECKING:**
```python
# ✅ CORRETO
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.transaction import Transaction


class User:
    transactions: Mapped[list["Transaction"]] = relationship(...)
```

---

## 🟡 Problemas de Formatação

### Linhas Muito Longas (73 casos)
**E501:** Linhas excedem 78 caracteres

```python
# ❌ 86 caracteres
@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)

# ✅ Quebrado em múltiplas linhas
@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
)
```

**Arquivos mais afetados:**
- `app/api/routers/transactions.py`
- `app/api/routers/categories.py`
- `app/models/`
- `app/api/error_handlers.py`

---

## 🔍 Achados Adicionais

### Ruff Issues (40 remanescentes)

| Code | Qtd | Tipo | Ação |
|------|-----|------|------|
| **B008** | 28 | FastAPI pattern ✓ | ✓ Aceitar (intencional) |
| **F821** | 6 | Undefined names | ⚠️ Usar TYPE_CHECKING |
| **B904** | 2 | Missing exception chain | ⚠️ Usar `from err` |

### MyPy Issues (26 erros)

- **Type Mismatches:** 12 (ORM → Schema)
- **Circular References:** 6 (models)
- **Missing Annotations:** 8 (middleware, etc)
- **Schema Validation:** 2 (enum mistos)

---

## ✅ Plano de Ação

### P0 - CRÍTICO (Fazer Primeiro)

- [ ] **Corrigir type mismatches** - routers convertem ORM → Schema
  - **Tempo:** 1-2 horas
  - **Arquivos:** auth, transactions, categories, users routers
  - **Impacto:** Previne bugs de runtime

- [ ] **Resolver circular imports** - usar TYPE_CHECKING
  - **Tempo:** 30 minutos
  - **Arquivos:** app/models/
  - **Impacto:** MyPy passes sem erros

### P1 - IMPORTANTE (Próximo Sprint)

- [ ] **Quebrar linhas longas** - reformatar decoradores e type hints
  - **Tempo:** 2-3 horas
  - **Arquivos:** routers/, models/
  - **Impacto:** Legibilidade, PEP 8 compliance

- [ ] **Exception chaining** - add `from err` em handlers
  - **Tempo:** 15 minutos
  - **Arquivos:** app/api/deps.py, services/category_service.py

### P2 - NICE TO HAVE

- [ ] **Docstrings** - Google style (30-40 funções)
  - **Tempo:** 3-4 horas
  - **Impacto:** Documentação, IDE hints

- [ ] **Type coverage** - aumentar de 65% para 85%+
  - **Tempo:** 1-2 horas
  - **Impacto:** Type safety

---

## 🔧 Configuração Pronta

✅ **Arquivos de Config Criados:**
- `pyproject.toml` - Ruff, MyPy, Coverage
- `.pre-commit-config.yaml` - Git hooks
- `Makefile` - Comandos de build

(Na época este relatório também listava um `.flake8`; o arquivo foi removido
desde então — ruff é a autoridade única de lint.)

---

## 📋 Comandos Úteis (atuais)

```bash
# Verificação completa — a definição de pronto
make quality

# Auto-fix, depois roda o gate completo
make fix

# Type checking isolado
make typecheck

# Pre-commit setup (só dano irreversível: segredos, arquivos
# grandes, conflitos de merge, .env real — não lint/type checking)
make install
pre-commit run --all-files
```

---

## 📈 Métricas

| Métrica | Valor | Status |
|---------|-------|--------|
| Type Coverage | ~65% | ⚠️ |
| PEP 8 Compliance | 70% | ⚠️ |
| Lint Issues | 52 | ⚠️ |
| MyPy Errors | 26 | ⚠️ |

---

## 🎯 Próximas Etapas

1. ✅ Skill de boas práticas criada e configurada
2. ⏳ Analisar e priorizar recomendações
3. ⏳ Criar PRs para cada grande mudança
4. ⏳ Adicionar pre-commit hooks para CI/CD
5. ⏳ Revisão de qualidade periódica

---

**Relatório Completo:** este arquivo é o relatório; não há um
`quality-report.txt` técnico separado.
