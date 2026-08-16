# Setup: Inicializar Repositório com Workflow Padronizado

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

Este documento explica como configurar o PocketLedger com o novo workflow de desenvolvimento padronizado.

## Status Atual

Você já tem tudo pronto! Os arquivos necessários já foram criados:

```
✅ Documentação de workflow completa
✅ Templates reutilizáveis
✅ OpenSpec CLI (openspec new change)
✅ Skill do Claude Code (/spec-driven-workflow)
✅ Exemplo real de mudança arquivada
✅ Convenções padronizadas
```

## Próximos Passos

### 1. Inicializar Repositório Git

Se o repositório ainda não é um git repo:

```bash
cd /home/klg-02/Documents/pocketledger-openspec
git init
git add .
git commit -m "initial: pocketledger with security hardening and standardized workflow"
```

### 2. Configurar Git Hooks (Opcional)

Para adicionar validações automáticas (opcional, mas recomendado):

```bash
mkdir -p .git/hooks

# Hook: validar tasks.md antes de commit
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Validate that tasks.md exists in in-progress changes before committing
if ls openspec/changes/*/tasks.md &>/dev/null; then
  echo "✓ Tasks.md found in in-progress changes"
fi
exit 0
EOF

chmod +x .git/hooks/pre-commit
```

### 3. Criar Primeiro PR com Workflow

Agora que tudo está setupado, criar uma nova feature seria:

```bash
# Opção 1: OpenSpec CLI
openspec new change your-idea

# Opção 2: Claude Code skill
/spec-driven-workflow

# Opção 3: Manual (para entender o padrão)
mkdir -p openspec/changes/2026-08-15-feature-your-idea
cp .claude/templates/change-*.md openspec/changes/2026-08-15-feature-your-idea/
git checkout -b feature/your-idea
# Editar templates, implementar, etc
```

### 4. Publicar para GitHub (Opcional)

Se quiser sincronizar com GitHub:

```bash
git remote add origin https://github.com/seu-usuario/pocketledger.git
git branch -M main
git push -u origin main
```

## Estrutura Final

Seu projeto agora tem:

```
pocketledger-openspec/
├── README.md                    # Visão geral do projeto
├── DEVELOPMENT.md               # Guia de desenvolvimento
├── WORKFLOW-QUICK-START.md      # TL;DR do workflow
├── WORKFLOW-EXAMPLE.md          # Exemplo passo-a-passo
├── SECURITY.md                  # Documentação de segurança
├── SETUP-WORKFLOW.md            # Este arquivo
│
├── .claude/
│   ├── templates/               # Templates reutilizáveis
│   │   ├── change-proposal.md
│   │   ├── change-design.md
│   │   └── change-tasks.md
│   │
│   └── skills/
│       └── spec-driven-workflow/SKILL.md
│
├── openspec/
│   ├── changes/
│   │   ├── 2026-08-15-feature-your-idea/  # Em andamento
│   │   └── archive/
│   │       └── 2026-08-14-security-jwt-hardening/
│   │           ├── proposal.md
│   │           ├── design.md
│   │           └── tasks.md
│   │
│   └── specs/                   # Especificações
│
├── app/                         # Código-fonte
├── tests/                       # Testes
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .gitignore
│
└── .git/                        # Repository (após git init)
```

## Próxima Feature?

Para criar a próxima feature (ex: audit logging):

```bash
openspec new change audit-logging
# → feature
# → audit-logging
# → ✓ Pronto para documentar e implementar
```

## Para Time / Colaboradores

Se outras pessoas vão contribuir, compartilhe:

1. **Link para** `WORKFLOW-QUICK-START.md` — Resumo rápido
2. **Link para** `WORKFLOW-EXAMPLE.md` — Exemplo prático
3. **Comando a executar** — `openspec new change <nome>`

Eles vão seguir o mesmo padrão, resultando em:
- Documentação consistente
- Commits bem estruturados
- PRs claras e fáceis de revisar
- Histórico preservado

## Para LLMs (Futuros)

Quando um LLM for revisar ou trabalhar neste projeto no futuro, ele vai:

1. Ler `WORKFLOW-QUICK-START.md` → Entende o padrão
2. Ver `openspec/changes/archive/` → Entende decisões passadas
3. Ler `proposal.md` de mudanças → Sabe o "por quê"
4. Ler `design.md` → Sabe o "como" e trade-offs
5. Ver commits do `tasks.md` → Sabe o "o quê"

Resultado: Compreensão completa do projeto e suas decisões!

## Troubleshooting

**P: `openspec new change` não roda?**
R: Confirme que o OpenSpec CLI está instalado e que `openspec/` existe na raiz do projeto.

**P: Skill `/spec-driven-workflow` não aparece?**
R: Reinicie Claude Code ou verifique que está no diretório certo

**P: Não consigo fazer commit?**
R: Rode `git config user.email "seu@email.com" && git config user.name "Seu Nome"`

**P: Posso customizar os tipos de mudança?**
R: Sim! Edite a taxonomia em `CLAUDE.md` §2 e §4 e atualize os templates conforme necessário

## Resumo

Você tem agora um workflow de desenvolvimento **padronizado, documentado, e escalável** que:

- ✅ Garante que cada mudança é documentada
- ✅ Facilita reviews (design já aprovado antes de código)
- ✅ Preserva histórico para futuro
- ✅ Permite que LLMs entendam decisões
- ✅ Facilita onboarding de novos devs
- ✅ Mantém conformidade e auditabilidade

Próximo passo: comece a usar em sua próxima feature!

```bash
openspec new change <nome>
```

Boa sorte! 🚀
