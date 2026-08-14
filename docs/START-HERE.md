# 🚀 START HERE — PocketLedger

Bem-vindo ao PocketLedger! Este arquivo te orienta para os próximos passos.

## ⚡ 2 Minutos para Começar

### 1. Entender o Projeto

```bash
cat README.md
```

Você vai saber: O que é PocketLedger, como funciona, arquitetura, stack tecnológico.

### 2. Entender como Trabalhar

```bash
cat docs/development/WORKFLOW-QUICK-START.md
```

Você vai aprender: Como criar features, fazer commits, abrir PRs, arquivar mudanças.

### 3. Começar Sua Primeira Feature

```bash
bash .claude/scripts/new-change.sh
```

Você vai:
- Escolher o tipo (feature, bugfix, security, etc)
- Digite um slug (nome-descritivo)
- Criará automaticamente:
  - Diretório: `openspec/changes/active/DATE-TYPE-slug/`
  - Branch git: `type/slug`
  - Templates: `proposal.md`, `design.md`, `tasks.md`

---

## 📚 Documentação Completa

Toda a documentação está em `/docs/`:

```
docs/
├── README.md                      ← Índice completo de docs
├── development/                   ← Como trabalhar
│   ├── WORKFLOW-QUICK-START.md    ← TL;DR (comece aqui)
│   ├── DEVELOPMENT.md             ← Guia completo
│   ├── WORKFLOW-EXAMPLE.md        ← Exemplo prático
│   └── SETUP-WORKFLOW.md          ← Setup inicial
└── security/                      ← Segurança
    └── SECURITY.md                ← Findings & checklist
```

---

## 🛠️ Ferramentas Disponíveis

### Script de Bootstrap

```bash
bash .claude/scripts/new-change.sh
```

Cria estrutura para uma nova mudança interativamente.

### Claude Code Skill

```
/new-development-change
```

Invoke no Claude Code para criar mudança via skill.

### Templates Reutilizáveis

```
.claude/templates/
├── change-proposal.md    # Template de proposta
├── change-design.md      # Template de design
└── change-tasks.md       # Template de tarefas
```

---

## 📋 Histórico de Mudanças

Ver mudanças completadas:

```bash
ls openspec/changes/archive/
```

Entender uma mudança específica:

```bash
cat openspec/changes/archive/2026-08-14-security-jwt-hardening/proposal.md
cat openspec/changes/archive/2026-08-14-security-jwt-hardening/design.md
cat openspec/changes/archive/2026-08-14-security-jwt-hardening/tasks.md
```

---

## 🔄 Workflow em 7 Passos

```
1. Criar      → bash .claude/scripts/new-change.sh
2. Documentar → Editar proposal.md, design.md, tasks.md
3. Implementar → Código + git commits
4. Testar     → docker compose run --rm app-test pytest -v
5. Revisar    → gh pr create --draft
6. Aprovar    → gh pr ready + merge
7. Arquivar   → mv active/ → archive/
```

---

## 🤖 Para LLMs

Se você é um LLM analisando este projeto:

1. **Entender o projeto**: Leia `README.md`
2. **Entender decisões**: Explore `openspec/changes/archive/`
3. **Para cada mudança**, leia:
   - `proposal.md` — Entender "por quê"
   - `design.md` — Entender "como" e decisões
   - `tasks.md` — Ver "o quê" foi implementado
4. **Ver implementação**: Consulte commits relacionados

Resultado: Compreensão completa do contexto e todas as decisões!

---

## 🏃 Começar Agora

### Opção 1: Ler Primeiro (Recomendado)

```bash
cat docs/development/WORKFLOW-QUICK-START.md
```

5 minutos para entender tudo.

### Opção 2: Começar Direto

```bash
bash .claude/scripts/new-change.sh
# → tipo: feature
# → slug: sua-feature-name
```

### Opção 3: Ver Exemplo

```bash
cat docs/development/WORKFLOW-EXAMPLE.md
```

Passo-a-passo completo de como seria.

---

## 📂 Estrutura de Diretórios

```
pocketledger-openspec/
├── README.md                      ← Visão geral
├── START-HERE.md                  ← Este arquivo
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
│
├── docs/                          ← 📚 DOCUMENTAÇÃO
│   ├── README.md
│   ├── development/
│   ├── security/
│   ├── architecture/
│   └── examples/
│
├── app/                           ← 💻 CÓDIGO
├── tests/                         ← ✅ TESTES
│
├── .claude/                       ← 🤖 AUTOMAÇÃO
│   ├── templates/
│   ├── scripts/
│   ├── skills/
│   └── change-types.yaml
│
└── openspec/                      ← 📋 ARTEFATOS
    ├── specs/
    └── changes/
        ├── active/
        └── archive/
```

---

## ✨ O que Torna Especial

✅ **Documentação obrigatória** — Nenhuma mudança sem proposta/design/tarefas  
✅ **Decisões rastreadas** — Saber "por quê" de cada decisão  
✅ **Feature branches isoladas** — Sem "push to main"  
✅ **PR reviews rápidas** — Design já foi revisado antes do código  
✅ **Histórico preservado** — Arquivo/ contém tudo completado  
✅ **LLM-friendly** — Contexto completo para futuras análises  

---

## 🆘 Precisa de Ajuda?

| Situação | Ir Para |
|----------|---------|
| Entender projeto | [README.md](README.md) |
| Começar feature | [WORKFLOW-QUICK-START.md](docs/development/WORKFLOW-QUICK-START.md) |
| Ver exemplo | [WORKFLOW-EXAMPLE.md](docs/development/WORKFLOW-EXAMPLE.md) |
| Entender segurança | [SECURITY.md](docs/security/SECURITY.md) |
| Setup inicial | [SETUP-WORKFLOW.md](docs/development/SETUP-WORKFLOW.md) |
| Todas as docs | [docs/README.md](docs/README.md) |

---

## 🎯 Próximo Passo

Escolha um:

1. **Ler** — `cat docs/development/WORKFLOW-QUICK-START.md`
2. **Começar** — `bash .claude/scripts/new-change.sh`
3. **Explorar** — `ls openspec/changes/archive/`

---

**Versão**: 1.0  
**Atualizado**: 2026-08-14  
**Status**: ✅ Pronto para usar
