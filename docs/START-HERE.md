# 🚀 START HERE — PocketLedger

> [!IMPORTANT]
> **Parcialmente superseded — leia [`agentic-development.md`](agentic-development.md)
> e a constituição do agente em uso primeiro: [`AGENTS.md`](../AGENTS.md) no
> Codex ou [`CLAUDE.md`](../CLAUDE.md) no Claude Code.**
>
> Este documento é o ponto de entrada, mas foi escrito contra um pipeline que
> nunca existiu. Concretamente:
>
> - `openspec new change <nome>   # ou a skill /spec-driven-workflow` — **o script foi removido**. Ele
>   gravava em `openspec/changes/active/`, um layout que o OpenSpec 1.8 não
>   reconhece, então as changes que criava eram invisíveis para a CLI. Use
>   `openspec new change <nome>` ou a skill `spec-driven-workflow`.
> - `openspec/changes/active/` — não existe. Changes ficam em
>   `openspec/changes/<nome>/`.
> - `.claude/change-types.yaml` — removido; a taxonomia de tipos está nas
>   constituições `AGENTS.md` e `CLAUDE.md`, §2 e §4.
> - `make check` — agora existe de verdade, como alias de `make quality`.
>
> A orientação geral sobre o projeto continua válida.

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
git checkout -b <tipo>/<slug>
openspec new change <nome>   # ou a skill /spec-driven-workflow
```

Você vai:
- Escolher o tipo (feature, bugfix, security, etc)
- Digite um slug (nome-descritivo)
- Criará automaticamente:
  - Diretório: `openspec/changes/DATE-TYPE-slug/`
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

### Bootstrap de Mudanca

```bash
git checkout -b <tipo>/<slug>
openspec new change <nome>   # ou a skill /spec-driven-workflow
```

Cria a estrutura de uma nova mudanca; a branch deve existir antes do primeiro
edit.

### Skill de Workflow

```
/spec-driven-workflow
```

No Codex, siga `AGENTS.md`; no Claude Code, siga `CLAUDE.md`. Ambos usam a
skill `spec-driven-workflow` em seus diretórios nativos.

### Templates do Claude Code

```
.claude/templates/
├── change-proposal.md    # Template de proposta
├── change-design.md      # Template de design
└── change-tasks.md       # Template de tarefas
```

O Codex usa os artefatos criados pelo OpenSpec; nao precisa de uma copia desses
templates.

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
1. Criar      → git checkout -b <tipo>/<slug>; openspec new change <nome>
2. Documentar → Editar proposal.md, design.md, tasks.md
3. Implementar → Código + git commits
4. Testar     → make test
5. Revisar    → verificação independente e relatório de conformidade
6. Aprovar    → aceite humano explícito; só então push e pull request
7. Arquivar   → openspec archive <nome>
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
openspec new change <nome>   # ou a skill /spec-driven-workflow
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
├── docs/START-HERE.md             ← Este arquivo
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
├── .claude/                       ← 🤖 CLAUDE CODE
│   ├── templates/
│   ├── scripts/
│   ├── skills/
│   └── settings.json
│
├── .agents/                       ← 🤖 CODEX SKILLS
├── .codex/                        ← 🤖 CODEX AGENTS E HOOKS
│
└── openspec/                      ← 📋 ARTEFATOS
    ├── specs/
    └── changes/
        ├── <nome>/
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
| Começar feature | [WORKFLOW-QUICK-START.md](development/WORKFLOW-QUICK-START.md) |
| Ver exemplo | [WORKFLOW-EXAMPLE.md](development/WORKFLOW-EXAMPLE.md) |
| Entender segurança | [SECURITY.md](security/SECURITY.md) |
| Setup inicial | [SETUP-WORKFLOW.md](development/SETUP-WORKFLOW.md) |
| Todas as docs | [docs/README.md](README.md) |

---

## 🎯 Próximo Passo

Escolha um:

1. **Ler** — `cat docs/development/WORKFLOW-QUICK-START.md`
2. **Começar** — crie a branch e execute `openspec new change <nome>`
3. **Explorar** — `ls openspec/changes/archive/`

---

**Versão**: 1.0  
**Atualizado**: 2026-08-14  
**Status**: ✅ Pronto para usar
