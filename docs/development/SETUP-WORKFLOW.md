# Setup: Inicializar Repositório com Workflow Padronizado

Este documento explica como configurar o PocketLedger com o novo workflow de desenvolvimento padronizado.

## Status Atual

Você já tem tudo pronto! Os arquivos necessários já foram criados:

```
✅ Documentação de workflow completa
✅ Templates reutilizáveis
✅ Script de automação (new-change.sh)
✅ Skill do Claude Code (/new-development-change)
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
# Validate that tasks.md exists in active changes before committing
if ls openspec/changes/active/*/tasks.md &>/dev/null; then
  echo "✓ Tasks.md found in active changes"
fi
exit 0
EOF

chmod +x .git/hooks/pre-commit
```

### 3. Criar Primeiro PR com Workflow

Agora que tudo está setupado, criar uma nova feature seria:

```bash
# Opção 1: Script interativo
bash .claude/scripts/new-change.sh

# Opção 2: Claude Code skill
/new-development-change

# Opção 3: Manual (para entender o padrão)
mkdir -p openspec/changes/active/2026-08-15-feature-your-idea
cp .claude/templates/change-*.md openspec/changes/active/2026-08-15-feature-your-idea/
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
│   ├── scripts/
│   │   └── new-change.sh        # Script para criar mudanças
│   │
│   ├── skills/
│   │   └── new-development-change/SKILL.md
│   │
│   └── change-types.yaml        # Convenções padronizadas
│
├── openspec/
│   ├── changes/
│   │   ├── active/              # Em andamento
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
bash .claude/scripts/new-change.sh
# → feature
# → audit-logging
# → ✓ Pronto para documentar e implementar
```

## Para Time / Colaboradores

Se outras pessoas vão contribuir, compartilhe:

1. **Link para** `WORKFLOW-QUICK-START.md` — Resumo rápido
2. **Link para** `WORKFLOW-EXAMPLE.md` — Exemplo prático
3. **Comando a executar** — `bash .claude/scripts/new-change.sh`

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

**P: Script `new-change.sh` não roda?**
R: Verifique permissões: `chmod +x .claude/scripts/new-change.sh`

**P: Skill `/new-development-change` não aparece?**
R: Reinicie Claude Code ou verifique que está no diretório certo

**P: Não consigo fazer commit?**
R: Rode `git config user.email "seu@email.com" && git config user.name "Seu Nome"`

**P: Posso customizar os tipos de mudança?**
R: Sim! Edite `.claude/change-types.yaml` e atualize os templates conforme necessário

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
bash .claude/scripts/new-change.sh
```

Boa sorte! 🚀
