# Plano de Tarefas — Endurecimento JWT e Remediação de Security Findings

## Status Geral

- [x] Planejamento (design) completo
- [x] Implementação completa
- [x] Testes passando (81 testes)
- [x] Documentação atualizada
- [x] Code review aprovado
- [x] Pronto para mesclar

---

## Resumo

Remediar 14 findings de auditoria de segurança (2 Critical, 5 High, 5 Medium, 2 Low) via:
- Startup guard (fail-closed se secrets placeholder)
- Rate limiting (5 tentativas/min)
- Security headers (nosniff, deny-frames, no-referrer)
- CORS safe-by-default
- Docs gating (hidden in production)
- Password complexity (letter + digit)
- Container hardening (non-root, multi-stage, no dev-deps)
- DB port isolation (localhost only)
- Failed auth logging

---

## Tarefas

### Phase 1: Fix Blocker

- [x] **Fix alembic/env.py imports**
  - Arquivos: `alembic/env.py`
  - Problema: `from app.config` não existe, deveria ser `from app.core.config`
  - Testes: N/A (não há testes para alembic)

### Phase 2: Secrets & Startup Guard

- [x] **Add startup guard to config.py**
  - Arquivos: `app/core/config.py`
  - Adicionar `assert_production_ready()` function
  - Adicionar settings: `cors_allowed_origins`, `rate_limit_max_attempts`, `rate_limit_window_seconds`
  - Testes: `tests/test_config_guards.py` (8 novos testes)

- [x] **Call guard in app/main.py**
  - Arquivos: `app/main.py`
  - Chamar `assert_production_ready(settings)` após `configure_logging()`

### Phase 3: CORS & Docs Gating & Security Headers

- [x] **Add CORS middleware**
  - Arquivos: `app/main.py`, `app/core/config.py`
  - Adicionar setting `cors_allowed_origins`
  - Adicionar `CORSMiddleware` com parse de comma-separated origins
  - Testes: Integração testada em `test_security_headers.py` (1 test)

- [x] **Gate docs/redoc in production**
  - Arquivos: `app/main.py`
  - Condicional: `docs_url="/docs" if environment != "production" else None`

- [x] **Add security headers middleware**
  - Arquivos: `app/api/middleware.py`
  - Novo `SecurityHeadersMiddleware` classe
  - Headers: X-Content-Type-Options, X-Frame-Options, Referrer-Policy
  - Testes: `tests/test_security_headers.py` (3 novos testes)

### Phase 4: Password Complexity

- [x] **Add password validator**
  - Arquivos: `app/schemas/auth.py`
  - Novo `@field_validator` on `RegisterRequest.password`
  - Requisitos: 1+ letra, 1+ dígito
  - Testes: `tests/test_auth.py` (2 novos testes)

### Phase 5: Rate Limiting & Failed Auth Logging

- [x] **Add rate limiting middleware**
  - Arquivos: `app/api/middleware.py`, `app/core/config.py`, `app/main.py`
  - Novo `AuthRateLimitMiddleware` (fixed-window, in-memory)
  - Settings: `rate_limit_max_attempts`, `rate_limit_window_seconds`
  - Testes: `tests/test_auth.py` (1 novo test), `tests/conftest.py` (fixture para reset)

- [x] **Add failed auth logging**
  - Arquivos: `app/api/error_handlers.py`
  - Log `auth_failed` com `client_ip` e `path` para UnauthorizedError
  - Testes: `tests/test_observability.py` (1 novo test)

### Phase 6: Container Hardening

- [x] **Restructure Dockerfile (multi-stage)**
  - Arquivos: `Dockerfile`
  - Stages: `base` (deps), `runtime` (final, non-root), `test` (dev-deps)
  - Non-root user: uid 1000 appuser
  - Testes: Docker build apenas (não há testes automáticos, mas manual verify)

- [x] **Update docker-compose.yml**
  - Arquivos: `docker-compose.yml`
  - Add `target: runtime` para app service
  - Add `app-test` service com `target: test`
  - Postgres port: `0.0.0.0:5433` → `127.0.0.1:5433`
  - DB credentials: interpolação via `${DB_USER}`, etc

- [x] **Create .gitignore**
  - Arquivos: `.gitignore` (novo)
  - Entradas: `.env`, `__pycache__/`, `.venv/`, `.pytest_cache/`, etc

### Phase 7: Documentation

- [x] **Create SECURITY.md**
  - Arquivo: `SECURITY.md` (novo)
  - Conteúdo: Findings addressed, remediation, checklist, deferred items

- [x] **Update README.md**
  - Arquivo: `README.md`
  - Sections: Configuração table (add new vars), Testes (update docker compose command), Possíveis evoluções (add JWT rotation, API versioning)
  - Fix stale reference: `app/config.py` → `app/core/config.py`

- [x] **Create DEVELOPMENT.md**
  - Arquivo: `DEVELOPMENT.md` (novo)
  - Conteúdo: Standardized development workflow, change types, conventions, templates

### Phase 8: Tests

- [x] **Test config guards**
  - Arquivo: `tests/test_config_guards.py` (novo)
  - 8 testes cobrindo startup guard logic

- [x] **Test password complexity**
  - Arquivo: `tests/test_auth.py`
  - 2 testes: missing letter, missing digit

- [x] **Test rate limiting**
  - Arquivo: `tests/test_auth.py`
  - 1 teste: 6+ attempts bloqueado
  - Fixture reset: `tests/conftest.py`

- [x] **Test failed auth logging**
  - Arquivo: `tests/test_observability.py`
  - 1 teste: `auth_failed` log com client_ip

- [x] **Test security headers**
  - Arquivo: `tests/test_security_headers.py` (novo)
  - 3 testes: headers presentes em responses, error responses, CORS default deny

---

## Critério de Aceitação

- [x] Todos os requisitos de `proposal.md` atendidos
- [x] Todos os 81 testes passando (66 existentes + 15 novos)
- [x] Nenhum regression em features existentes
- [x] Documentação completa (SECURITY.md, DEVELOPMENT.md, README updates)
- [x] No TODO/FIXME comments não intencionais
- [x] Code review completo
- [x] Startup guard bloqueia placeholder secrets em prod
- [x] Rate limiting ativo em /api/v1/auth/login e /register
- [x] Security headers presentes em all responses
- [x] Docker build completa e container roda como non-root

---

## Log de Progresso

### 2026-08-13

- Auditoria de segurança completa identificando 14 findings
- Proposta de mudança criada com todos os 14 items endereçados
- Design técnico documentado com decisões arquiteturais

### 2026-08-14

- **10:30** — Iniciada implementação, começando com fix alembic bug
- **10:45** — Startup guard completado (assert_production_ready)
- **11:15** — CORS middleware adicionado
- **11:30** — Security headers middleware adicionado
- **11:45** — Rate limiting middleware completado
- **12:00** — Password complexity validator adicionado
- **12:30** — Failed auth logging adicionado
- **13:00** — Dockerfile reestruturado (multi-stage)
- **13:30** — docker-compose.yml atualizado
- **14:00** — .gitignore criado
- **14:30** — SECURITY.md e DEVELOPMENT.md escritos
- **15:00** — README.md atualizado
- **15:30** — Todos os testes rodando e passando (81 testes)
- **16:00** — Code review completo, tudo pronto

---

## Notas

- Rate limiter é single-process/in-memory — aceitável para escala atual, deferred para Redis em produção
- Startup guard é fail-closed — previne deploy inseguro mas operadores precisam configurar JWTkey
- Multi-stage Dockerfile não tem issues de permission com bind-mount (testado)
- Nenhuma mudança de schema de banco necessária
- All changes preservadas in git history para auditoria futura
