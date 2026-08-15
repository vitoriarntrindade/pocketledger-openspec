# 📚 Documentação — Índice

Bem-vindo! Este é o centro de documentação do PocketLedger.

## 🚀 Começar

**Primeira vez aqui?** Leia na ordem:

1. **[START-HERE.md](START-HERE.md)** — visão geral do projeto (5 min)
2. **[agentic-development.md](agentic-development.md)** — como o desenvolvimento
   funciona aqui: gates, agentes, hooks e o ciclo de vida de uma mudança
3. **[standards/BEST_PRACTICES.md](standards/BEST_PRACTICES.md)** — padrões de código

As regras permanentes do projeto ficam em **[`CLAUDE.md`](../CLAUDE.md)**, na
raiz. Ele é a constituição: quando qualquer documento aqui discordar dele, ele
vence.

## 📂 Estrutura

```
docs/
├── README.md                    ← você está aqui
├── START-HERE.md                # visão geral do projeto
├── agentic-development.md       # arquitetura de desenvolvimento autônomo
│
├── standards/
│   └── BEST_PRACTICES.md        # Python: PEP 8, type hints, docstrings
│
├── development/                 # guias antigos, marcados como superseded
│
├── reports/
│   └── QUALITY_REPORT.md
│
└── security/
    └── SECURITY.md
```

> Os documentos em `development/` foram escritos contra um pipeline que nunca
> foi instalado (`make check` sem `Makefile`, ruff/mypy/pre-commit ausentes,
> `openspec/changes/active/`). Cada um traz um aviso no topo. São mantidos pelo
> raciocínio que contêm, mas `agentic-development.md` é a fonte atual.

## 🎯 Por tarefa

### Adicionando uma feature

1. Descreva o que quer. O sistema classifica, especifica e implementa —
   veja [agentic-development.md](agentic-development.md).
2. Manualmente: `git checkout -b feature/<slug>`, implemente, `make quality`.
3. Templates: `.claude/templates/`, via `.claude/scripts/generate-component.sh`.

### Entendendo os padrões

1. Leia `standards/BEST_PRACTICES.md` e a skill `python-best-practices`.
2. Arquitetura e invariantes: skill `pocketledger-architecture`.

### Verificando qualidade

```bash
make quality   # a definition of done: format, lint, tipos, testes, cobertura ≥95%, segurança, specs
make fast      # só checagens estáticas, para o loop de edição
make fix       # aplica autofixes seguros e roda o gate
```

## ✅ Convenções

**Código Python:**

- type hints em tudo
- docstrings Google style
- máximo de 78 caracteres por linha
- cobertura mínima de 95%, aplicada pelo build

**Documentação:**

- ✅ em `/docs/`, categorizada
- ❌ nunca na raiz — exceto `README.md` e `CLAUDE.md`, que é configuração e
  precisa estar onde o Claude Code o encontra

---

**Primeira vez?** Leia [START-HERE.md](START-HERE.md)
