# Quick Start — Standardized Development Workflow

> [!IMPORTANT]
> Read [`docs/agentic-development.md`](../agentic-development.md) and the
> applicable constitution first: `AGENTS.md` for Codex or `CLAUDE.md` for
> Claude Code. Both runtimes use the same `make quality` gate and shared skills.

## TL;DR

Para criar uma nova mudança, use:

```bash
openspec new change <nome>
```

Ou invoque a skill compartilhada:

```
/spec-driven-workflow
```

---

## Seu Workflow Padronizado

### 1️⃣ **Criar Mudança**

```bash
openspec new change <nome>
# → Escolha tipo (feature, bugfix, security, etc)
# → Digite slug (audit-logging, rate-limit-fix, etc)
# → Diretório criado: openspec/changes/2026-08-15-feature-audit-logging/
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
make quality
```

### 5️⃣ **Revisar** (5 min)

Atualizar `tasks.md`: marque itens como ✓ enquanto completa

### 6️⃣ **Aceite Humano**

Produza o relatório de conformidade e aguarde aceite humano explícito. Antes
disso, o agente não faz push nem abre pull request. Depois do aceite, o humano
decide sobre publicação e merge.

### 7️⃣ **Arquivar** (1 min)

```bash
openspec archive 2026-08-15-feature-audit-logging
git add openspec/changes/archive/
git commit -m "archive: feature-audit-logging"
```

---

## Estrutura de Mudanças

```
openspec/changes/
├── 2026-08-15-feature-audit-logging/  # Em andamento
│   ├── proposal.md               # "Por quê?"
│   ├── design.md                 # "Como?"
│   ├── tasks.md                  # "O quê?"
│   └── specs/                    # (Opcional)
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
| Bootstrap | `openspec new change <nome>` | Cria diretório e artefatos; crie a branch antes |
| Template: Proposal | `.claude/templates/change-proposal.md` | Motivação, escopo, requisitos |
| Template: Design | `.claude/templates/change-design.md` | Decisões arquiteturais, APIs, infra |
| Template: Tasks | `.claude/templates/change-tasks.md` | Checklist de trabalho |
| Tipos definidos | `AGENTS.md` / `CLAUDE.md` §2 e §4 | feature, bugfix, security, refactor, perf, docs, chore |
| Skill compartilhada | `.claude/skills/spec-driven-workflow/` | Codex usa `.agents/skills -> ../.claude/skills`; invoque `/spec-driven-workflow` |

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
- [ ] O gate passa? (`make quality`)
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
- **Tipos e convenções:** veja `AGENTS.md` ou `CLAUDE.md`, §2 e §4

---

## Perguntas Frequentes

**P: E se for uma mudança muito pequena (typo)?**
R: Siga a classificação TRIVIAL nas constituições; não é necessário criar uma
mudança OpenSpec.

**P: Posso fazer múltiplas features ao mesmo tempo?**
R: Sim! Crie branches separadas para cada mudança.

**P: A proposta pode mudar durante a implementação?**
R: Sim! Atualize `proposal.md`, `design.md`, etc. conforme necessário. Isso é normal.

**P: Como descartar uma mudança inacabada?**
R: Delete o diretório em `openspec/changes/<nome>/` e a branch. Sem história será preservada.

**P: Preciso fazer PR em draft?**
R: Não antes do aceite humano explícito. O agente produz o relatório de
conformidade e para; a publicação e a abertura do PR acontecem somente depois
do aceite.

---

## Próximo Passo

```bash
# Pronto para começar?
openspec new change <nome>
```

Happy coding! 🚀
