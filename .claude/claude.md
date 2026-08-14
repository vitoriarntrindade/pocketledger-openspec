# 🎯 PocketLedger - Claude Code Guidelines

Este arquivo define como trabalhar com este projeto. **Claude lê automaticamente.**

---

## 📁 Estrutura do Repositório

```
pocketledger-openspec/
├── app/                          # Código principal
│   ├── api/                      # API endpoints (routers)
│   ├── models/                   # SQLAlchemy ORM models
│   ├── schemas/                  # Pydantic schemas (request/response)
│   ├── services/                 # Business logic
│   ├── core/                     # Config, security, errors
│   └── infrastructure/           # Database, logging, metrics
│
├── tests/                        # Testes unitários
│   └── test_*.py
│
├── docs/                         # Documentação
│   ├── START-HERE.md            # Ponto de entrada
│   ├── standards/               # Padrões de código
│   │   └── BEST_PRACTICES.md   # Python best practices
│   ├── development/             # Guias de desenvolvimento
│   │   ├── NEW-FEATURES.md     # Como adicionar features
│   │   └── CLEAN-CODE-WORKFLOW.md
│   ├── reports/                 # Relatórios de qualidade
│   │   └── QUALITY_REPORT.md
│   ├── architecture/            # Arquitetura do sistema
│   └── security/                # Segurança
│
├── .claude/                      # Configuração Claude Code
│   ├── claude.md               # Este arquivo
│   ├── skills/                 # Skills personalizadas
│   │   └── python-best-practices/
│   ├── templates/              # Templates reutilizáveis
│   │   ├── router.py.template
│   │   └── service.py.template
│   └── scripts/                # Scripts úteis
│       └── generate-component.sh
│
├── openspec/                    # OpenSpec (Spec-Driven Development)
│   ├── specs/                  # Especificações do sistema
│   ├── changes/                # Mudanças em progresso
│   └── changes/archive/        # Mudanças arquivadas
│
├── pyproject.toml              # Config Python (ruff, mypy)
├── .flake8                     # Config Flake8
├── .pre-commit-config.yaml     # Git hooks automáticos
├── Makefile                    # Comandos úteis
└── README.md                   # Readme (usar apenas na raiz)
```

### 🎯 Regra Importante

**❌ NÃO criar .md na raiz do repo**
- Tudo em `/docs` (organizado por categoria)
- Exceto: `README.md` (padrão git)

---

## 📋 Convenções do Projeto

### Python Code Standards

✅ **OBRIGATÓRIO:**
- Type hints em TUDO (`def func(x: int) -> str:`)
- Docstrings Google style em toda função/classe
- Max 78 caracteres por linha
- PEP 8 compliance
- Exception chaining (`raise ... from err`)

✅ **Automático:**
- Pre-commit hooks validam cada commit
- Ruff formata automaticamente
- MyPy valida tipos

Veja: `docs/standards/BEST_PRACTICES.md`

### Estrutura de Código

**Routers (Endpoints):**
- Arquivo: `app/api/routers/{recurso}.py`
- Template: `.claude/templates/router.py.template`
- Padrão: Retornar schemas (Pydantic), não ORM models

**Services (Lógica):**
- Arquivo: `app/services/{recurso}_service.py`
- Template: `.claude/templates/service.py.template`
- Padrão: Receber Session + User, retornar ORM models

**Models (ORM):**
- Arquivo: `app/models/{recurso}.py`
- Padrão: SQLAlchemy com type hints completos

**Schemas (API):**
- Arquivo: `app/schemas/{recurso}.py`
- Padrão: Pydantic com Config(from_attributes=True)

### Naming Conventions

- **Módulos:** `lowercase_with_underscores`
- **Classes:** `PascalCase`
- **Funções:** `lowercase_with_underscores`
- **Constantes:** `UPPERCASE_WITH_UNDERSCORES`
- **Privados:** `_leading_underscore`

---

## 🚀 Workflow para Novas Features

### Quick Start (5 minutos)

```bash
# 1. Ler este guia (você está aqui!)
cat .claude/claude.md

# 2. Ler guia de features
cat docs/development/NEW-FEATURES.md

# 3. Criar feature
git checkout -b feature/seu-recurso
./claude/scripts/generate-component.sh router seu_recurso
./claude/scripts/generate-component.sh service seu_recurso

# 4. Editar e commitar
git add .
git commit -m "feat: add seu_recurso"
# Pre-commit valida automaticamente ✓

# 5. Push + PR
git push origin feature/seu-recurso
```

---

## 🛠️ Ferramentas & Skills

### Skill: `/python-best-practices`

Para quando precisa refatorar código existente:

```bash
/python-best-practices
# Gera report de qualidade
# Cria OpenSpec change automaticamente
# Propõe soluções com rastreabilidade
```

### Skill: `/openspec-propose`

Para quando precisa planejar mudanças grandes:

```bash
/openspec-propose "Feature description"
# Cria spec-driven change
# Documentação + design + tasks
```

### Script: `./claude/scripts/generate-component.sh`

Para gerar novo componente:

```bash
./claude/scripts/generate-component.sh router posts
./claude/scripts/generate-component.sh service posts
```

---

## 📚 Documentação Importante

| Arquivo | Leia quando |
|---------|------------|
| `docs/START-HERE.md` | Primeira vez no projeto |
| `docs/standards/BEST_PRACTICES.md` | Dúvidas sobre padrões |
| `docs/development/NEW-FEATURES.md` | Adicionando feature nova |
| `docs/development/CLEAN-CODE-WORKFLOW.md` | Entender workflow completo |
| `docs/reports/QUALITY_REPORT.md` | Revisar qualidade do código |

---

## ✅ Pre-commit Hooks (Automático)

Cada `git commit` roda automaticamente:

```
✓ ruff check --fix    (formata + arruma)
✓ mypy               (type checking)
✓ flake8             (PEP 8)
✓ pydocstyle         (docstrings)
```

Se falhar:
1. Mostra os problemas
2. Ruff já corrige automaticamente
3. Você revisa e re-tenta `git commit`

---

## 🔍 Validação Manual

```bash
source .venv/bin/activate

# Check tudo
make check

# Ou individual
make lint              # Ruff + Flake8
make type-check        # MyPy
make test              # Pytest
```

---

## 📊 OpenSpec (Spec-Driven Development)

Para mudanças significativas, use OpenSpec:

```bash
# Criar proposta
/openspec-propose "Feature description"

# Implementar com rastreabilidade
/openspec-apply-change nome-da-change

# Arquivar após completo
openspec archive nome-da-change --yes
```

Resultado: Especificação + Design + Tasks + Commits rastreáveis

---

## 🎯 Instruções para Claude

**Quando receber tarefa neste projeto:**

1. ✅ Ler `docs/standards/BEST_PRACTICES.md` se for código novo
2. ✅ Usar templates em `.claude/templates/` quando possível
3. ✅ Type hints + docstrings em TUDO
4. ✅ Max 78 caracteres por linha
5. ✅ Não criar .md na raiz (usar `/docs/`)
6. ✅ Para refatoração: usar `/python-best-practices`
7. ✅ Para mudanças grandes: usar `/openspec-propose`
8. ✅ Commitar com messages descritivas
9. ✅ Testar localmente com `make check`

**Não faça:**
- ❌ Código sem type hints
- ❌ Linhas > 78 caracteres
- ❌ Docstrings faltando
- ❌ .md espalhados na raiz
- ❌ ORM models no return de routers (usar schemas)

---

## 🚨 Problemas Comuns

### Problema: Linha muito longa
**Solução:** Quebrar com parênteses (implicit line continuation)
```python
# ❌ 95 caracteres
def create_item(name: str, description: str, category_id: int) -> ItemOut:

# ✅ Correto
def create_item(
    name: str,
    description: str,
    category_id: int,
) -> ItemOut:
```

### Problema: Falta type hint
**Solução:** Sempre adicionar tipos
```python
# ❌ Errado
def get_user(user_id):

# ✅ Correto
def get_user(user_id: int) -> Optional[User]:
```

### Problema: Router retornando ORM model
**Solução:** Converter para schema
```python
# ❌ Errado
def get_user(user_id: int) -> UserOut:
    return db.get(User, user_id)

# ✅ Correto
def get_user(user_id: int) -> UserOut:
    user = db.get(User, user_id)
    return UserOut.model_validate(user)
```

---

## 📞 Resumo

| Aspecto | Padrão |
|---------|--------|
| **Linguagem** | Python 3.8+ |
| **Framework** | FastAPI + SQLAlchemy |
| **Type Checking** | MyPy (strict) |
| **Linting** | Ruff + Flake8 |
| **Formatting** | 78 chars max |
| **Docstrings** | Google style |
| **Docs** | Em `/docs/` (nunca raiz) |
| **CI/CD** | Pre-commit hooks + git |
| **Workflows** | OpenSpec (SDD) |

---

## 🎓 Quick Links

- 📖 **Começar:** `docs/START-HERE.md`
- 🎯 **Nova Feature:** `docs/development/NEW-FEATURES.md`
- 📋 **Padrões:** `docs/standards/BEST_PRACTICES.md`
- 🔧 **Refatorar:** `/python-best-practices` skill
- 📊 **Spec-Driven:** `/openspec-propose` skill

---

**Status:** ✅ Projeto padronizado e pronto para uso

**Última atualização:** 2026-08-14
