# 🚀 Primeiros passos

Como subir o ambiente completo, rodar a aplicação fora do Docker e configurar cada variável de ambiente.

---

## 🚀 Quick Start

### Pré-requisitos

- Docker e Docker Compose (única dependência obrigatória para rodar o projeto).
- Opcionalmente, Python 3.12+ e `pip`, caso prefira rodar a aplicação fora de container.

### Subindo o ambiente completo

```bash
docker compose up -d
```

Isso inicia três serviços:

| Serviço | Descrição |
| --- | --- |
| `app` | API FastAPI em `http://localhost:8000`. Executa `alembic upgrade head` automaticamente antes de começar a servir. |
| `db` | PostgreSQL 16, exposto em `localhost:5433` (a porta do host foi deslocada de 5432 para 5433 para não conflitar com um Postgres local). |
| `jaeger` | Jaeger all-in-one, com UI em `http://localhost:16686`. |

Depois de subir, acesse `http://localhost:8000/docs` para o Swagger.

### Rodando fora do Docker (opcional)

```bash
cp .env.example .env
# edite .env: aponte DATABASE_URL e OTEL_EXPORTER_OTLP_ENDPOINT para localhost
pip install -r requirements-dev.txt
alembic upgrade head
uvicorn app.main:app --reload
```

### Parando o ambiente

```bash
docker compose down       # mantém os dados (volume do Postgres)
docker compose down -v    # remove também o volume de dados
```

---

## ⚙️ Configuração

Todas as variáveis são lidas pela classe `Settings` (`app/core/config.py`), com valores padrão sensatos para desenvolvimento local. Em produção, `JWT_SECRET` e `DATABASE_URL` **devem** ser sobrescritos — a aplicação recusará iniciar se qualquer um deles ainda usar seu valor placeholder quando `ENVIRONMENT` não for `development` ou `test`.

| Variável | Obrigatória | Descrição | Exemplo |
| --- | --- | --- | --- |
| `SERVICE_NAME` | Não | Nome do serviço, usado nos logs estruturados. | `pocketledger` |
| `ENVIRONMENT` | Não | Ambiente de execução (`development`, `test`, `production`). Ativa a validação de segredos. | `development` |
| `LOG_LEVEL` | Não | Nível mínimo de log. | `INFO` |
| `DATABASE_URL` | **Obrigatória fora de desenvolvimento** | URL de conexão SQLAlchemy com o PostgreSQL (não use credenciais padrão em produção). | `postgresql+psycopg://pocketledger:pocketledger@db:5432/pocketledger` |
| `DB_USER` | Não | Nome de usuário do PostgreSQL, usado em interpolação de `docker-compose.yml`. | `pocketledger` |
| `DB_PASSWORD` | Não | Senha do PostgreSQL, usada em interpolação de `docker-compose.yml`. | `pocketledger` |
| `DB_NAME` | Não | Nome do banco de dados, usado em interpolação de `docker-compose.yml`. | `pocketledger` |
| `JWT_SECRET` | **Obrigatória fora de desenvolvimento** | Segredo usado para assinar/validar os tokens JWT (HS256). Gere com `openssl rand -hex 32` ou similar. | Valor aleatório (nunca `change-me-in-production`) |
| `JWT_ALGORITHM` | Não | Algoritmo de assinatura do JWT. | `HS256` |
| `JWT_EXPIRES_MINUTES` | Não | Tempo de vida do token de acesso, em minutos. | `60` |
| `PASSWORD_MIN_LENGTH` | Não | Tamanho mínimo exigido para senhas no registro. | `8` |
| `DEFAULT_PAGE_SIZE` | Não | Tamanho de página padrão na listagem de transações. | `20` |
| `MAX_PAGE_SIZE` | Não | Tamanho de página máximo permitido. | `100` |
| `CORS_ALLOWED_ORIGINS` | Não | Lista de origens CORS permitidas (comma-separated), vazia por padrão (nega todos os cross-origin requests). | `https://app.example.com,https://app-staging.example.com` |
| `RATE_LIMIT_MAX_ATTEMPTS` | Não | Número máximo de tentativas de login/registro por janela de tempo. | `5` |
| `RATE_LIMIT_WINDOW_SECONDS` | Não | Tamanho da janela de tempo (segundos) para rate limiting. | `60` |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | Não | Endpoint OTLP (gRPC) para exportação de traces. | `jaeger:4317` |
| `OTEL_ENABLED` | Não | Liga/desliga a instrumentação de tracing. | `true` |
| `TEST_DATABASE_URL` | Não (apenas testes) | URL do banco de dados dedicado usado pela suíte de testes. | `postgresql+psycopg://pocketledger:pocketledger@db:5432/pocketledger_test` |

Um exemplo completo está em [`.env.example`](../../.env.example) — nenhum segredo real está commitado; os valores ali são placeholders explicitamente marcados como "dev-only" / "change-me".

> Com o ambiente de pé, siga para [API](api.md) ou para [Testes](testing.md).


---

⬅️ [README](../../README.md) · 📚 [Índice da documentação](../README.md)
