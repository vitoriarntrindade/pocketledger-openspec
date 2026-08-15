# Exemplo: Workflow de Desenvolvimento Padronizado

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

Este documento mostra, passo-a-passo, como seria desenvolver uma nova feature usando o novo workflow padronizado.

## Cenário: Implementar Audit Logging

Imagine que você quer adicionar audit logging detalhado para rastrear todas as operações.

---

## 1. Iniciar uma Nova Mudança

```bash
# Opção A: Interativa (recomendada)
bash .claude/scripts/new-change.sh

# Output:
# === Criar Nova Mudança ===
# Tipo de mudança:
#   1. feature    - Nova funcionalidade
#   ...
# Escolha (1-7): 1
# Slug (ex: audit-logging): audit-logging
# 
# ✓ Diretório criado: openspec/changes/active/2026-08-15-feature-audit-logging
# ✓ Criado: proposal.md
# ✓ Criado: design.md
# ✓ Criado: tasks.md
# ✓ Branch criada: feature/audit-logging
```

---

## 2. Documentação Inicial (Proposal)

Editar `openspec/changes/active/2026-08-15-feature-audit-logging/proposal.md`:

```markdown
# Feature: Audit Logging

## Motivação

Rastrear todas as operações críticas (login, CRUD de transações, etc.) para compliance e debugging.

## Descrição

Adicionar um middleware que registra:
- Quem (user_id)
- O quê (endpoint, método)
- Quando (timestamp)
- Resultado (status code)

Em um endpoint especial `/api/v1/audit-log` (apenas admin).

## Requisitos

- [ ] Endpoint GET para listar audit logs
- [ ] Middleware auto-rastreia operações
- [ ] Filter por date, user, endpoint
- [ ] Armazenar em banco de dados
- [ ] Apenas admin pode ver

## Escopo

### Incluído
- Audit middleware
- Database schema para audit logs
- API endpoint para queries
- Admin authorization

### Excluído
- Export para CSV
- Retention policy automático
- Real-time streaming
```

---

## 3. Especificação Técnica (Design)

Editar `openspec/changes/active/2026-08-15-feature-audit-logging/design.md`:

```markdown
# Design — Audit Logging

## Decisões Arquiteturais

### 1. Onde Armazenar Logs (Application Logs vs. Database)

**Escolha:**
- Opção A: Stdout/arquivo (application logs)
- **Opção B: Database (audit_logs table)**

**Rationale:**
- Database permite queries SQL
- Permite filtros complexos (date range, user, etc)
- Relaciona com user record
- Estruturado para compliance

**Impacto:**
- Nova migration para tabela `audit_logs`
- Novo model `AuditLog`
- Novo middleware para auto-capture

### 2. Middleware vs. Service-Level Logging

**Escolha:**
- **Opção A: Middleware (auto-capture todas as operações)**
- Opção B: Manual logging em cada service

**Rationale:**
- Middleware não requer mudança em código
- Captura tudo uniformemente
- Simples e manutenível

**Impacto:**
- Novo `AuditLogMiddleware`
- Tudo é automaticamente auditado

## Nova Tabela: audit_logs

```sql
CREATE TABLE audit_logs (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL REFERENCES users(id),
    http_method VARCHAR(10),
    http_route VARCHAR(255),
    http_status_code INT,
    query_params TEXT,  -- JSON
    response_summary TEXT,  -- Não armazenar dados sensíveis
    timestamp DATETIME DEFAULT NOW(),
    ip_address VARCHAR(45),
    user_agent VARCHAR(1024)
);

CREATE INDEX idx_audit_user_date ON audit_logs(user_id, timestamp);
CREATE INDEX idx_audit_route_date ON audit_logs(http_route, timestamp);
```

## Novo Endpoint

```yaml
GET /api/v1/audit-log
  Query Params:
    - start_date (optional)
    - end_date (optional)
    - user_id (optional, only admin can filter)
    - http_route (optional)
  Response:
    - items: [...]
    - total: int
    - page: int
  Authorization: Admin only
```
```

---

## 4. Plano de Trabalho (Tasks)

Editar `openspec/changes/active/2026-08-15-feature-audit-logging/tasks.md`:

```markdown
# Plano de Tarefas — Audit Logging

## Tarefas

### Banco de Dados
- [ ] **Criar migration**
  - Arquivos: `alembic/versions/xxx_add_audit_logs.py`
  - Criar tabela `audit_logs` com campos e índices

### Implementação
- [ ] **Criar model AuditLog**
  - Arquivos: `app/models/audit_log.py`
  - Relacionamento com User

- [ ] **Criar middleware AuditLogMiddleware**
  - Arquivos: `app/api/middleware.py`
  - Capturar request/response, salvar em DB

- [ ] **Criar router audit**
  - Arquivos: `app/api/routers/audit.py`
  - Endpoint GET /api/v1/audit-log
  - Filtros (date, user, route)
  - Admin authorization

- [ ] **Criar schemas Pydantic**
  - Arquivos: `app/schemas/audit_log.py`
  - AuditLogOut, AuditLogListResponse

### Testes
- [ ] **Testes de middleware**
  - Verificar que operações são registradas
  
- [ ] **Testes de endpoint**
  - Listar audit logs
  - Filtros
  - Admin authorization
  - Non-admin rejeitado

### Documentação
- [ ] **README.md** — Descrever feature
- [ ] **API docs** — Swagger atualizado

## Critério de Aceitação

- [ ] All 81 tests passing (+ novos testes de audit)
- [ ] Migration aplica sem erros
- [ ] Admin pode ver todas as operações auditadas
- [ ] Filters funcionam corretamente
- [ ] Non-admin recebe 403 Forbidden
- [ ] Documentação completa
```

---

## 5. Implementação em Feature Branch

```bash
# Você está na branch feature/audit-logging

# 1. Criar migration
alembic revision --autogenerate -m "Add audit_logs table"

# 2. Editar a migration (se necessário)
nano alembic/versions/xxx_add_audit_logs.py

# 3. Criar model
touch app/models/audit_log.py
# ... escrever model ...

# 4. Commit
git add alembic/versions/ app/models/
git commit -m "feat: add audit_log model and migration"

# 5. Criar middleware
nano app/api/middleware.py
# ... escrever AuditLogMiddleware ...

# 6. Testar localmente
docker compose up -d
docker compose run --rm app-test pytest tests/test_audit.py -v

# 7. Commit
git add app/api/middleware.py
git commit -m "feat: add audit logging middleware"

# 8. Criar endpoint
touch app/api/routers/audit.py
# ... escrever router ...

# 9. Teste e commit
git add app/api/routers/ app/schemas/audit_log.py
git commit -m "feat: add audit log query endpoint"

# 10. Atualizar README
nano README.md
git add README.md
git commit -m "docs: document audit logging feature"

# 11. Marcar tasks como completas em tasks.md
nano openspec/changes/active/2026-08-15-feature-audit-logging/tasks.md
git add openspec/changes/active/2026-08-15-feature-audit-logging/
git commit -m "update: audit logging tasks completed"
```

---

## 6. Revisão e Testes

```bash
# Rodar todos os testes
docker compose run --rm app-test pytest -v

# Output:
# tests/test_auth.py ........................ PASSED
# tests/test_audit.py ................. PASSED (15 novos)
# tests/test_categories.py ................ PASSED
# ... 
# ========================== 96 passed in 45.23s ==========================

# Verificar que documentação está ok
head -20 openspec/changes/active/2026-08-15-feature-audit-logging/proposal.md
head -20 openspec/changes/active/2026-08-15-feature-audit-logging/design.md

# Verificar que tasks estão completas
grep "- \[x\]" openspec/changes/active/2026-08-15-feature-audit-logging/tasks.md | wc -l
# Output: 12 (todas as tarefas marcadas)
```

---

## 7. Abrir Pull Request (Draft)

```bash
# Push branch
git push origin feature/audit-logging

# Criar PR em draft
gh pr create --draft \
  --title "Feature: Audit logging" \
  --body "$(cat openspec/changes/active/2026-08-15-feature-audit-logging/proposal.md)"

# Output:
# Creating pull request for feature/audit-logging into main in anthropics/pocketledger
# ? Title Feature: Audit logging
# ? Body
# ? What's next? [Create draft] (use arrow keys)
# [draft] - create draft

# PR criado: https://github.com/anthropics/pocketledger/pull/123
```

---

## 8. Revisão & Aprovação

Você compartilha o PR link com colegas/mentores:

> "Implementei audit logging. Checklist:
> - ✓ Proposal clara em proposal.md
> - ✓ Design técnico em design.md
> - ✓ Tasks completas em tasks.md
> - ✓ 96 testes passando
> - ✓ Sem regressions
> 
> Pronto para revisar quando quiser."

Após revisão e aprovação:

```bash
# Marcar PR como pronto para review
gh pr ready 123

# Ou esperar feedback, fazer ajustes
git add app/api/routers/audit.py
git commit -m "fix: sanitize audit log response"
git push origin feature/audit-logging
# PR automaticamente atualizado
```

---

## 9. Mesclar na Main

```bash
# Após aprovação final
gh pr merge 123 --squash

# Output:
# ✓ Pull request #123 was merged
# Deleted branch feature/audit-logging

# main agora tem audit logging
```

---

## 10. Arquivar a Mudança

```bash
# Mover de active para archive
mv openspec/changes/active/2026-08-15-feature-audit-logging \
   openspec/changes/archive/2026-08-15-feature-audit-logging

# Commit e push
git add openspec/changes/archive/
git commit -m "archive: feature-audit-logging"
git push origin main
```

---

## 11. Histórico Preservado

Agora, no futuro:

```bash
# Alguém quer entender audit logging
ls openspec/changes/archive/ | grep audit
# Output: 2026-08-15-feature-audit-logging

cat openspec/changes/archive/2026-08-15-feature-audit-logging/proposal.md
# Lê: "Por que foi feita?"

cat openspec/changes/archive/2026-08-15-feature-audit-logging/design.md
# Lê: "Como foi implementada? Que decisões?"

git log --oneline | grep audit
# Lê: "Quais commits fizeram isso? Como implementado?"

# Um LLM (ou novo dev) agora entende completamente
# o contexto, motivação, e design de audit logging
```

---

## Benefícios Deste Workflow

1. **Para você (desenvolvedor)**
   - Estrutura clara do que fazer
   - Templates prontos
   - Histórico preservado
   - Review mais fácil (está tudo documentado)

2. **Para código**
   - Commits bem estruturados
   - Sem mistura de concerns
   - Feature branch isolada
   - Fácil de reverter se necessário

3. **Para futuros LLMs/desenvolvedores**
   - proposal.md explica o "por quê"
   - design.md explica o "como"
   - tasks.md mostra o "o quê"
   - Git history mostra "o código"
   - Tudo junto = contexto completo

4. **Para time**
   - PR review é rápida (design já foi revisado)
   - Nada surpresa (tudo em proposal/design primeiro)
   - Mudanças rastreáveis
   - Conhecimento compartilhado

---

## Próxima Feature?

Repita o processo para a próxima mudança. O template e o script estão lá, esperando por você.

```bash
bash .claude/scripts/new-change.sh
# → tipo: feature
# → slug: caching-summary
# → Branch: feature/caching-summary
# → Documentação pronta
# → Implementar conforme acima
```

---

## Resumo

**Antes:** Mudanças ad-hoc, código sem documentação, LLMs confusos

**Depois:** Mudanças bem documentadas, código estruturado, LLMs entendem tudo

**Tempo:** 5 minutos para setup, depois fluxo natural
