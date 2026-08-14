# Design — Endurecimento JWT e Remediação de Security Findings

## Decisões Arquiteturais

### 1. Startup Guard (Fail-Closed vs. Log-Warning)

**Escolha:**
- Opção A: Log warning em produção com secrets placeholder
- Opção B: **RuntimeError na startup → recusa iniciar**

**Rationale:**
- Um log warning é fácil de ignorar em logs ruidosos
- A única forma de prevenir deploy inseguro é falhar-fechado
- Crash na startup é o sinal mais claro possível
- Operadores vão resolver imediatamente (não há workaround)

**Impacto:**
- `app/core/config.py` — Nova função `assert_production_ready()`
- `app/main.py` — Chamada antes de criar FastAPI app

### 2. Rate Limiting (Hand-rolled vs. Slowapi Library)

**Escolha:**
- Opção A: `slowapi` library com Redis backing
- Opção B: **Hand-rolled fixed-window em memória**

**Rationale:**
- Projeto é single-process (uma instância uvicorn por container)
- Apenas 2 endpoints precisam rate limiting (/auth/login, /auth/register)
- Fixed-window counter é suficiente para proteção brute-force
- Adicionar slowapi introduziria padrão decorator novo (vs. middleware existente)
- Simplicidade > funcionalidade "scalable" quando a escala não existe

**Impacto:**
- `app/api/middleware.py` — Novo `AuthRateLimitMiddleware`
- Resets em restart (aceitável), não coordena multi-processo (deferred)

### 3. CORS (Empty Default vs. Allow All)

**Escolha:**
- Opção A: Allow all origins (*)
- Opção B: **Allow no origins by default (empty list)**

**Rationale:**
- Frontend ainda não existe
- Safe-by-default: nega CORS até que frontend seja integrado
- Operadores têm que configurar `CORS_ALLOWED_ORIGINS` explicitamente
- Previne acidental exposure se config estiver errada

**Impacto:**
- `app/core/config.py` — Nova setting `cors_allowed_origins: str = ""`
- `app/main.py` — CORSMiddleware parse da config

### 4. Docs Gating (Always Hidden vs. Environment-Based)

**Escolha:**
- Opção A: Sempre esconder /docs
- Opção B: **Esconder apenas em production**

**Rationale:**
- Developers precisam de /docs para trabalhar localmente
- Production não deve expor API schema (informação leakage)
- Reusa environment setting já existente (development vs. production)

**Impacto:**
- `app/main.py` — Gating `docs_url`, `redoc_url`, `openapi_url`

### 5. Multi-Stage Docker (com vs. sem)

**Escolha:**
- Opção A: Single stage (atual)
- Opção B: **Multi-stage (base → runtime + test)**

**Rationale:**
- `requirements-dev.txt` (pytest, httpx) poluem runtime image
- Multi-stage é padrão da indústria, sem custo significativo
- Permite `docker compose run app-test pytest` sem dev-deps no produção
- Separa concerns: builder vs. runtime vs. test

**Impacto:**
- `Dockerfile` — Reestruturado com 3 stages
- `docker-compose.yml` — `app` usa `target: runtime`, novo service `app-test`

### 6. Container Security (UID 1000 vs. 0)

**Escolha:**
- Opção A: Root (atual)
- Opção B: **Non-root user uid:gid 1000:1000**

**Rationale:**
- Kubernetes + Docker best practices exigem non-root
- Se container é comprometido, attacker não é root na máquina host
- UID 1000 é a convenção padrão para non-root (não conflita com sistema)

**Impacto:**
- `Dockerfile` — useradd appuser, chown, USER appuser
- `docker-compose.yml` — bind-mount `.:/srv` pode precisar cuidado com permissions

### 7. Password Validation (Server vs. Client)

**Escolha:**
- Opção A: Cliente valida antes de enviar
- Opção B: **Servidor valida (server-side validation sempre)**

**Rationale:**
- Client validation pode ser bypassado
- Server é source of truth
- Field validator no schema Pydantic é o lugar certo

**Impacto:**
- `app/schemas/auth.py` — Field validator com `@field_validator`
- Reusa padrão existente (já usamos validators em transaction.py)

### 8. DB Credentials Isolation

**Escolha:**
- Opção A: Hardcoded na docker-compose.yml
- Opção B: **Environment variables + .env interpolation**

**Rationale:**
- docker-compose.yml vai pro git
- .env não vai pro git (gitignore)
- `${VAR:-default}` syntax é syntax nativo do compose
- Operador controla secrets em runtime, não em repo

**Impacto:**
- `.env.example` — Exemplo com placeholders
- `.gitignore` — Novo, exclui .env
- `docker-compose.yml` — `${DB_USER}`, `${DB_PASSWORD}`, `${DB_NAME}` interpolation

## Arquitetura & Fluxo

```
Request → RequestIdMiddleware → AuthRateLimitMiddleware → SecurityHeadersMiddleware 
       → CORSMiddleware → Router → Service → Model → Database
       ↓
   (errors) → error_handler → JSONResponse (com X-Request-ID header)

Startup: assert_production_ready(settings) → fail-closed if placeholder secrets
```

## Mudanças de Banco de Dados

- ✅ Nenhuma migration necessária (apenas config/middleware)

## Mudanças de API

- Novo endpoint implícito: rate limit behavior (429 responses)
- Nenhum novo endpoint de API
- Nenhuma mudança em schemas existentes

Erro de rate limit:
```json
POST /api/v1/auth/login (6º tentativa dentro de 60s)
Response: HTTP 429
{
  "error": {
    "code": "rate_limited",
    "message": "Too many attempts, try again later.",
    "request_id": "..."
  }
}
```

## Mudanças de Infraestrutura

### Variáveis de Ambiente

| Var | Novo/Mudado | Tipo |
|-----|-------------|------|
| `JWT_SECRET` | Mudado | Obrigatório fora de dev |
| `DATABASE_URL` | Mudado | Obrigatório fora de dev (sem default-creds) |
| `CORS_ALLOWED_ORIGINS` | Novo | Opcional (padrão: ""/deny-all) |
| `RATE_LIMIT_MAX_ATTEMPTS` | Novo | Opcional (padrão: 5) |
| `RATE_LIMIT_WINDOW_SECONDS` | Novo | Opcional (padrão: 60) |
| `DB_USER` | Novo | Opcional (para docker-compose interpolation) |
| `DB_PASSWORD` | Novo | Opcional (para docker-compose interpolation) |
| `DB_NAME` | Novo | Opcional (para docker-compose interpolation) |

### Docker

- Multi-stage Dockerfile: base → runtime + test
- Non-root user (uid 1000)
- Dev deps removidas do runtime image

### Database

- Postgres port: `0.0.0.0:5433` → `127.0.0.1:5433` (localhost only)
- Credentials: interpolados via `${DB_USER}` etc em docker-compose

## Dependências

- ✅ Nenhuma lib nova necessária
- Rate limiter é hand-rolled
- CORS usa stock `fastapi.middleware.cors.CORSMiddleware`

## Segurança

- ✅ Startup guard previne deploy com placeholder secrets
- ✅ Rate limiting protege contra brute-force
- ✅ Security headers (nosniff, deny-frames, no-referrer)
- ✅ CORS deny-all by default
- ✅ Docs hidden in production
- ✅ Container non-root (privilege reduction)
- ✅ Failed auth logging (audit trail)
- ✅ Port 5433 restricted to localhost

## Testes

- 15 novos testes:
  - 2 testes de password complexity
  - 1 teste de rate limiting
  - 1 teste de failed login logging
  - 3 testes de security headers
  - 8 testes de startup guard / config validation
- Todos os 81 testes devem passar (66 existentes + 15 novos)

## Rollback / Reverter

Se necessário reverter:
1. Revert commit que mesclou a feature branch
2. Remove openspec/changes/ directory entry
3. Database schema não mudou, sem data cleanup necessário
4. Environment variables voltam aos defaults (seguros em dev)

## Monitoramento & Alertas

Novos logs estruturados:
- `auth_failed` — Failed login com client_ip e path
- Request logging já existe, inclui status code 429 para rate limits

## Documentação

- ✅ `SECURITY.md` — Findings, remediação, checklist pre-prod
- ✅ `DEVELOPMENT.md` — Workflow de desenvolvimento
- ✅ `README.md` — Atualizado: Configuração table, test instructions, Possíveis evoluções
- ✅ Inline comments onde necessário (mínimos)
