# Quick Start — Standardized Development Workflow

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

## TL;DR

Para criar uma nova mudança, use:

```bash
bash .claude/scripts/new-change.sh
```

Ou invoque a skill do Claude Code:

```
/new-development-change
```

---

## Seu Workflow Padronizado

### 1️⃣ **Criar Mudança**

```bash
bash .claude/scripts/new-change.sh
# → Escolha tipo (feature, bugfix, security, etc)
# → Digite slug (audit-logging, rate-limit-fix, etc)
# → Branch criada: feature/audit-logging
# → Diretório criado: openspec/changes/active/2026-08-15-feature-audit-logging/
# → Templates copiados: proposal.md, design.md, tasks.md
```

### 2️⃣ **Documentar** (15 min)

Edite os 3 arquivos no diretório:

| Arquivo | O Quê? | Quando? |
|---------|--------|--------|
| `proposal.md` | **Por quê** fazer isso? Contexto, requisitos, riscos | Antes de iniciar |
| `design.md` | **Como** fazer? Decisões técnicas, trade-offs | Antes de codificar |
| `tasks.md` | **O quê** fazer? Lista de tarefas + checklist | Sempre atualizar |

### 3️⃣ **Implementar** (varia)

```bash
# Edite código conforme necessário
# Commit frequentemente com bom prefixo:
#   feat: new feature
#   fix: bug fix
#   security: security patch
#   refactor: refactoring
#   docs: documentation
#   test: tests

git commit -m "feat: add audit middleware"
```

### 4️⃣ **Testar** (5 min)

```bash
docker compose run --rm app-test pytest -v
```

### 5️⃣ **Revisar** (5 min)

Atualizar `tasks.md`: marque itens como ✓ enquanto completa

### 6️⃣ **Abrir PR** (Draft) (2 min)

```bash
git push origin feature/audit-logging
gh pr create --draft \
  --title "Feature: Audit logging" \
  --body "$(cat openspec/changes/active/2026-08-15-feature-audit-logging/proposal.md)"
```

**Importante:** Comece em DRAFT. Apenas converta para "ready for review" quando você (ou seu time) aprovar as mudanças.

### 7️⃣ **Mesclar** (1 min)

```bash
gh pr merge --squash
```

### 8️⃣ **Arquivar** (1 min)

```bash
mv openspec/changes/active/2026-08-15-feature-audit-logging \
   openspec/changes/archive/2026-08-15-feature-audit-logging
git add openspec/changes/archive/
git commit -m "archive: feature-audit-logging"
git push origin main
```

---

## Estrutura de Mudanças

```
openspec/changes/
├── active/                           # Em andamento
│   └── 2026-08-15-feature-audit-logging/
│       ├── proposal.md               # "Por quê?"
│       ├── design.md                 # "Como?"
│       ├── tasks.md                  # "O quê?"
│       └── specs/                    # (Opcional)
│
└── archive/                          # Finalizadas
    └── 2026-08-14-security-jwt-hardening/
        ├── proposal.md
        ├── design.md
        ├── tasks.md
        └── specs/
```

---

## Templates & Scripts

| Item | Localização | Descrição |
|------|------------|----------|
| Script de bootstrap | `.claude/scripts/new-change.sh` | Cria dir, copia templates, inicia branch |
| Template: Proposal | `.claude/templates/change-proposal.md` | Motivação, escopo, requisitos |
| Template: Design | `.claude/templates/change-design.md` | Decisões arquiteturais, APIs, infra |
| Template: Tasks | `.claude/templates/change-tasks.md` | Checklist de trabalho |
| Tipos definidos | `.claude/change-types.yaml` | feature, bugfix, security, refactor, perf, docs, chore |
| Skill Claude | `.claude/skills/new-development-change/` | Invocar via `/new-development-change` |

---

## Tipos de Mudança

Escolha um quando criar:

- **feature** — Nova funcionalidade (ex: audit-logging)
- **bugfix** — Correção de bug (ex: rate-limit-persistence)
- **security** — Patch de segurança (ex: jwt-hardening)
- **refactor** — Refatoração técnica (ex: error-handling)
- **perf** — Otimização de performance (ex: query-optimization)
- **docs** — Documentação (ex: api-guide)
- **chore** — Tarefas administrativas (ex: upgrade-python)

---

## Convenções de Naming

```
{DATE}-{TYPE}-{SLUG}
2026-08-15-feature-audit-logging
2026-08-14-bugfix-rate-limit-persistence
2026-08-13-security-jwt-hardening
```

---

## Convenções de Commit

```
{TYPE}: {message}

feat: add audit middleware
- Auto-capture all operations
- Store in audit_logs table

fix: handle edge case in rate limiter
security: validate JWT before processing
refactor: simplify error handling
docs: document audit logging endpoint
test: add rate limiting tests
perf: optimize transaction queries
chore: upgrade dependencies

Co-Authored-By: Your Name <email@example.com>
```

---

## Ao Revisar um Change Anterior

Se você quer entender uma mudança já feita:

```bash
# 1. Leia a proposta (contexto)
cat openspec/changes/archive/2026-08-14-security-jwt-hardening/proposal.md

# 2. Leia o design (decisões técnicas)
cat openspec/changes/archive/2026-08-14-security-jwt-hardening/design.md

# 3. Leia as tarefas (o que foi feito)
cat openspec/changes/archive/2026-08-14-security-jwt-hardening/tasks.md

# 4. Veja os commits
git log --grep="security-jwt-hardening" --oneline

# 5. Leia o código das mudanças
git show <commit-hash>
```

---

## Checklist Pré-Merge

Antes de mesclar um PR:

- [ ] `proposal.md` está claro e completo?
- [ ] `design.md` explica todas as decisões?
- [ ] `tasks.md` tem todos os itens marcados ✓?
- [ ] Todos os testes passam? (`pytest -v`)
- [ ] Nenhuma regressão em features existentes?
- [ ] Documentação atualizada (README, SECURITY, etc)?
- [ ] Commits têm bons prefixos (`feat:`, `fix:`, etc)?
- [ ] Nenhum `TODO/FIXME` não intencional?
- [ ] Code review aprovado?

---

## Exemplo Real Completo

Veja `openspec/changes/archive/2026-08-14-security-jwt-hardening/` para um exemplo real da mudança que acabamos de implementar:

- ✅ `proposal.md` — 14 findings de segurança foram remediados
- ✅ `design.md` — Decisões sobre startup guard, rate limiting, CORS, etc
- ✅ `tasks.md` — Todos os 10+ itens marcados como completos

---

## Mais Informações

- **Workflow completo:** veja `DEVELOPMENT.md`
- **Exemplo passo-a-passo:** veja `WORKFLOW-EXAMPLE.md`
- **Tipos e convenções:** veja `.claude/change-types.yaml`

---

## Perguntas Frequentes

**P: E se for uma mudança muito pequena (typo)?**
R: Mesmo typos ganham um `proposal.md` mínimo (1-2 linhas) para rastreabilidade.

**P: Posso fazer múltiplas features ao mesmo tempo?**
R: Sim! Crie branches separadas para cada mudança.

**P: A proposta pode mudar durante a implementação?**
R: Sim! Atualize `proposal.md`, `design.md`, etc. conforme necessário. Isso é normal.

**P: Como descartar uma mudança inacabada?**
R: Delete o diretório em `openspec/changes/active/` e a branch. Sem história será preservada.

**P: Preciso fazer PR em draft?**
R: Sim! Comece em draft. Converta para "ready for review" quando tudo estiver pronto.

---

## Próximo Passo

```bash
# Pronto para começar?
bash .claude/scripts/new-change.sh
```

Happy coding! 🚀
