# 📚 Documentação - Índice

Bem-vindo! Este é o centro de documentação do PocketLedger.

## 🚀 Começar

**Primeira vez aqui?** Leia na ordem:

1. **[START-HERE.md](START-HERE.md)** - Visão geral do projeto (5 min)
2. **[standards/BEST_PRACTICES.md](standards/BEST_PRACTICES.md)** - Padrões de código
3. **[development/NEW-FEATURES.md](development/NEW-FEATURES.md)** - Como adicionar features

## 📂 Estrutura de Documentação

```
docs/
├── README.md                        ← Você está aqui
├── START-HERE.md                    # Visão geral do projeto
│
├── standards/                       # Padrões & Convenções
│   └── BEST_PRACTICES.md           # Python: PEP 8, type hints, docstrings
│
├── development/                     # Guias de Desenvolvimento
│   ├── NEW-FEATURES.md             # Como adicionar nova feature (quick start)
│   └── CLEAN-CODE-WORKFLOW.md      # Workflow completo com templates
│
├── reports/                         # Relatórios de Qualidade
│   └── QUALITY_REPORT.md           # Último relatório de qualidade
│
└── security/                        # Segurança
    └── SECURITY.md                 # Políticas de segurança
```

## 🎯 Por Tarefa

### Adicionando Nova Feature
1. Leia: `development/NEW-FEATURES.md` (5 min)
2. Use: `.claude/scripts/generate-component.sh`
3. Templates: `.claude/templates/`

### Entendendo Padrões
1. Leia: `standards/BEST_PRACTICES.md`
2. Exemplos: Veja código em `app/`

### Refatorando Código
1. Use skill: `/python-best-practices`
2. Gera: `reports/QUALITY_REPORT.md`

## ✅ Convenções

**Código Python:**
- Type hints em TUDO
- Docstrings Google style
- Max 78 caracteres por linha

**Documentação:**
- ✅ Em `/docs/` (categorizado)
- ❌ NUNCA na raiz (exceto README.md)

## 🚀 Workflow Rápido

```bash
git checkout -b feature/seu-recurso
./claude/scripts/generate-component.sh router seu_recurso
# Editar e commitar
git commit -m "feat: seu_recurso"  # Pre-commit valida!
```

---

**Primeira vez?** Leia [START-HERE.md](START-HERE.md)
