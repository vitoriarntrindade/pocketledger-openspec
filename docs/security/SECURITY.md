# Security & Remediation

This document summarizes the security audit findings for PocketLedger and the steps taken to remediate them.

## Findings Addressed

### Critical

1. **Hardcoded JWT secret placeholder** — The application previously defaulted `JWT_SECRET` to `"change-me-in-production"`. Fixed by adding a **fail-closed startup guard** in `app/core/config.py` (`assert_production_ready()`) that raises `RuntimeError` if the application starts in any environment other than `development`/`test` while the JWT secret still holds its placeholder value. The guard is invoked from `app/main.py` at import time, before the FastAPI app is constructed.

2. **Hardcoded database credentials** — The application previously defaulted to `pocketledger:pocketledger` in the database URL. Fixed alongside #1 by the same startup guard, which blocks startup if `"pocketledger:pocketledger"` appears in `DATABASE_URL` outside `development`/`test`. Additional hardening: `docker-compose.yml` now uses environment variable interpolation (`${DB_USER:-...}`, `${DB_PASSWORD:-...}`, `${DB_NAME:-...}`), allowing credentials to be overridden via `.env` file (which is git-ignored) rather than being committed in the compose file itself.

### High

3. **Database server exposed on all network interfaces** — PostgreSQL was bound to `0.0.0.0:5433` in `docker-compose.yml`. Fixed by binding to `127.0.0.1:5433` instead, restricting access to localhost only. This remains accessible for local development and testing but is no longer exposed to the network.

4. **Container runs as root** — The Dockerfile previously had no `USER` directive. Fixed by restructuring the Dockerfile into multi-stage builds: a `runtime` stage that creates a non-root user `appuser` (uid 1000), `chown`s the `/srv` directory, and runs as that user. The separate `test` stage allows development workflows to keep pytest/dev dependencies without bloating the production image.

5. **Development dependencies in production image** — The Dockerfile previously installed `requirements-dev.txt` in the final image. Fixed by the multi-stage Dockerfile split above: only the `runtime` stage is shipped; the `test` stage is used via `docker compose run --rm app-test pytest` and never deployed.

6. **No password complexity requirements** — The password validation only enforced a minimum length. Fixed by adding a `field_validator` on `RegisterRequest.password` in `app/schemas/auth.py` that requires at least one letter and one digit. This is deliberately proportionate (not enforcing uppercase/lowercase/special characters) for a learning project.

7. **No CORS configuration** — The API had no explicit CORS middleware. Fixed by adding `fastapi.middleware.cors.CORSMiddleware` in `app/main.py`, configured via a new `cors_allowed_origins: str = ""` setting in `app/core/config.py`. The default (empty string) denies all cross-origin requests, which is a safe-by-default posture until a specific frontend needs to be integrated.

### Medium

8. **Plaintext database URL in docker-compose environment block** — Database credentials were visible in `docker-compose.yml`'s environment variables. Fixed by adopting environment variable interpolation (see #2) so real secrets live in a git-ignored `.env` file rather than being committed in the compose file.

9. **No TLS/HTTPS** — The application serves only plain HTTP with no reverse proxy or TLS termination. This is a deployment-topology decision out of scope for this codebase (see "Before deploying to production" checklist below). Documented for visibility.

10. **No rate limiting on authentication endpoints** — Login and registration endpoints had no protection against brute-force attempts. Fixed by adding a hand-rolled `AuthRateLimitMiddleware` in `app/api/middleware.py` that implements fixed-window rate limiting in memory. Default: 5 attempts per 60-second window per `(client_ip, endpoint)` pair. Returns HTTP 429 when the limit is exceeded. Configurable via `RATE_LIMIT_MAX_ATTEMPTS` and `RATE_LIMIT_WINDOW_SECONDS` environment variables.

11. **Swagger UI and ReDoc always enabled** — The API documentation was accessible regardless of environment. Fixed by gating `docs_url`, `redoc_url`, and `openapi_url` in the `FastAPI()` constructor: they are only enabled when `environment != "production"`. Keeps documentation available during development and testing, hidden in production.

12. **Missing security response headers** — The API did not set headers like `X-Content-Type-Options: nosniff`. Fixed by adding `SecurityHeadersMiddleware` in `app/api/middleware.py`, which adds the following headers to every response:
    - `X-Content-Type-Options: nosniff` — prevent MIME-type sniffing in older browsers.
    - `X-Frame-Options: DENY` — prevent clickjacking by disallowing embedding in frames.
    - `Referrer-Policy: no-referrer` — reduce information leakage in referrer headers.

    Note: `Strict-Transport-Security` (HSTS) is not included because it only makes sense behind TLS termination, which this project does not provide (see #9). Add it when deploying behind a TLS-terminating reverse proxy.

13. **No security-relevant logging for failed authentication** — Failed login attempts were not logged with context like client IP. Fixed by adding structured logging in `app/api/error_handlers.py`: when an `UnauthorizedError` is encountered (which covers failed logins), the handler logs `logger.info("auth_failed", extra={"client_ip": ..., "path": ...})` with the client's IP and the endpoint that was targeted. This maintains the existing convention (services raise errors, handlers log) without coupling security logging to the service layer.

### Low

14. **No security-related infrastructure documentation** — Covered by this file and the "Before deploying to production" section below.

---

## Accepted Risk / Deferred Items

The following findings were reviewed and documented as acceptable for this project's current scope (a learning/reference implementation, not a production service):

- **No JWT key rotation strategy** — The application uses a single `JWT_SECRET` to sign/verify all tokens. Rotating this secret invalidates all outstanding tokens (including valid ones not yet expired). For a production service with long-lived tokens and a large user base, implementing a key rotation scheme (multiple active keys, gradual rollover) would be necessary. For PocketLedger, this is acceptable because: (1) tokens are short-lived (60 minutes by default), and (2) there is no refresh-token flow, so users simply re-login when needed. A future evolution can add refresh tokens and key rotation together.

- **No formal API versioning / deprecation policy beyond the `/api/v1` prefix** — Documented for visibility. As the API evolves, the `/api/v1` → `/api/v2` migration path exists but is not formally defined yet.

- **In-memory rate limiter is single-process, non-distributed** — The `AuthRateLimitMiddleware` uses a process-local dictionary to track attempt timestamps. It resets on process restart and does not coordinate across multiple uvicorn worker processes or replicas. This is appropriate for the current single-process `docker-compose up` workflow; if the application is scaled to multiple workers or instances, the rate limiter should be upgraded to use a distributed store (e.g., Redis) via a library like `slowapi`.

---

## Before Deploying to Production

Follow this checklist before running PocketLedger in a production environment:

- [ ] **Generate and set a strong random `JWT_SECRET`**
  - Example: `openssl rand -hex 32` or `python -c "import secrets; print(secrets.token_urlsafe(32))"`
  - Set via environment variable or `.env` file: `JWT_SECRET=<random_value>`
  - Never use the default `"change-me-in-production"` or `"dev-only-secret-change-me"`

- [ ] **Generate and set non-default database credentials**
  - Set `DB_USER`, `DB_PASSWORD`, and `DB_NAME` via environment variables or `.env`
  - Ensure `DATABASE_URL` no longer contains `pocketledger:pocketledger`

- [ ] **Configure CORS allowed origins if you have a web frontend**
  - Set `CORS_ALLOWED_ORIGINS` to a comma-separated list of frontend origins, e.g., `"https://app.example.com"`
  - If no frontend is needed, leave it empty (default deny-all)

- [ ] **Set `ENVIRONMENT=production`**
  - This activates the startup guard (verifies JWT_SECRET and DATABASE_URL are not placeholders)
  - This also disables `/docs` (Swagger) and `/redoc` endpoints

- [ ] **Deploy behind a TLS-terminating reverse proxy**
  - Do not expose the application's HTTP port directly to the internet
  - Use nginx, Caddy, Apache, a cloud load balancer (AWS ALB, GCP Cloud Load Balancer, etc.), or similar
  - Obtain a TLS certificate (e.g., via Let's Encrypt) and terminate HTTPS at the proxy
  - The proxy forwards plain HTTP to the app on an internal network
  - Once deployed behind TLS, consider adding the `Strict-Transport-Security` header in the proxy config

- [ ] **Do not reuse the bundled `docker-compose.yml` Postgres service in production**
  - The `db` service is configured for local development (single-instance, no backup, no resource limits)
  - Use a managed PostgreSQL service (AWS RDS, GCP Cloud SQL, etc.) or a properly-configured dedicated database cluster
  - Ensure database backups and high availability are in place

- [ ] **Verify `.env` was never committed**
  - Confirm `.env` is in `.gitignore` and was never pushed to the repository
  - Rotate all secrets if there's any doubt about exposure

- [ ] **Review and monitor logs**
  - Structured logs are output to stdout in JSON format, including `request_id`, `trace_id`, and (for auth failures) `client_ip`
  - Aggregate logs to a central system (ELK stack, Datadog, CloudWatch, etc.) for monitoring and alerting

---

## Additional Security Measures to Consider (Future Work)

While not in scope for this release, these are recommended for a production system:

- **Refresh token flow and token revocation** — Implement a refresh-token mechanism for long-running sessions, with server-side token revocation (blocklist or database-backed invalidation).
- **Distributed rate limiting** — Scale the rate limiter to Redis or similar if running multiple instances.
- **Secrets management** — Adopt a secrets management service (HashiCorp Vault, AWS Secrets Manager, etc.) instead of `.env` files for production credentials.
- **Web application firewall (WAF)** — Deploy a WAF in front of the proxy to detect and block malicious requests.
- **Regular dependency scanning** — Integrate automated vulnerability scanning (`dependabot`, `snyk`, etc.) into the CI/CD pipeline.
- **Security testing in CI/CD** — Add automated security testing (SAST, DAST) to the build pipeline.
