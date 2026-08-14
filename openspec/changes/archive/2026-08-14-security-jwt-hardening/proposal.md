# Segurança: Endurecimento JWT e Remediação de 14 Findings

## Motivação

Uma auditoria de segurança abrangente identificou 14 vulnerabilidades no PocketLedger (2 Critical, 5 High, 5 Medium, 2 Low). As mais críticas envolvem:

- Placeholder secrets (JWT_SECRET, database credentials) hardcoded e facilmente reconhecidos
- Container rodando como root
- Dependências de desenvolvimento no runtime
- Falta de proteções contra brute-force
- Swagger UI exposto em produção
- Headers de segurança ausentes

Sem remediação, o projeto não é seguro para produção.

## Descrição

Implementar defesas de segurança em camadas:

1. **Startup Guard** — Falha-fechada se secrets placeholder forem usados fora de dev/test
2. **Rate Limiting** — Proteção contra brute-force em endpoints de autenticação
3. **Security Headers** — X-Content-Type-Options, X-Frame-Options, Referrer-Policy
4. **CORS** — Safe-by-default (nega todas as origins por padrão)
5. **Docs Gating** — /docs e /redoc ocultos em produção
6. **Password Complexity** — Exigir letra + digit
7. **Container Hardening** — Non-root user, multi-stage Docker, dev deps removidas
8. **DB Isolation** — Postgres bound apenas a localhost, credenciais interpoladas via .env
9. **Failed Auth Logging** — Rastrear tentativas de login falhadas com client IP
10. **Startup Guard** — Validar secrets não-placeholder

## Contexto

O PocketLedger foi criado como exercício de Spec-Driven Development. Agora, com uma auditoria de segurança completa, é o momento perfeito para endurecer a aplicação mantendo a simplicidade e a documentação clara.

A mudança será a **primeira** a seguir o novo workflow de desenvolvimento padronizado (DEVELOPMENT.md).

## Requisitos

- [ ] Todos os 14 findings endereçados com evidência
- [ ] Testes cobrindo os novos comportamentos
- [ ] Startup guard previne deploy inseguro
- [ ] Documentação completa (SECURITY.md, README updates)
- [ ] 81 testes passando (66 existentes + 15 novos)
- [ ] Sem regressões em features existentes

## Escopo

### Incluído

- Hardcoding de secrets detection via startup guard
- Rate limiting em endpoints de auth (5/min por IP)
- Security headers (3: nosniff, deny-frames, no-referrer)
- CORS safe-by-default (empty origin list)
- Docs gating baseado em environment
- Password complexity (letter + digit)
- Container security (non-root, multi-stage, no dev-deps)
- Database port isolation (localhost only)
- Failed auth logging estruturado
- Comprehensive security documentation (SECURITY.md)

### Excluído (Deferred)

- JWT key rotation — Deferred até implementar refresh tokens
- API versioning policy — Documentado como deferred
- TLS termination — Out of scope (deployment concern)
- Secrets manager integration — Out of scope (Vault, AWS Secrets)
- WAF / DDoS protection — Deployment-time concern

## Benefícios

- **Security by Default** — Startup guard previne deployment inseguro
- **Brute-force Protection** — Rate limiting contra tentativas de login/registro
- **Attack Surface Reduction** — Headers, docs gating, non-root container
- **Data Isolation** — DB restricted to localhost, credenciais via .env
- **Audit Trail** — Failed auth events registrados com IP
- **Maintainability** — Comprehensive documentation via SECURITY.md
- **LLM-Friendly** — Todas as decisões documentadas para futuros developers/LLMs

## Riscos

| Risco | Mitigação | Severidade |
|-------|-----------|-----------|
| Startup guard quebra deploy se ENV vars não forem configuradas | Documentação clara em SECURITY.md com checklist | Médio |
| Rate limiter em-memory é single-process | Escalabilidade futura com Redis | Médio |
| Non-root user em container pode ter issues com bind-mount | Testar com docker compose up | Baixo |
| Mudança significativa do codebase | Testes abrangentes + git history preservado | Médio |

## Dependências

- Nenhuma dependência externa bloqueante
- Todos os testes devem passar localmente antes de merge

## Referências

- Security Audit Report (2026-08-13)
- DEVELOPMENT.md — Novo workflow padronizado
- SECURITY.md — Documentação de segurança
