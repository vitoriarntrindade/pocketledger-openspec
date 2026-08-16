# 📁 Estrutura do projeto

A árvore de diretórios, a responsabilidade de cada pacote da aplicação e a stack tecnológica que sustenta tudo isso.

---

## 📁 Estrutura do projeto

```text
.
├── app/
│   ├── main.py                         # ponto de entrada e composição da aplicação FastAPI
│   │
│   ├── api/
│   │   ├── deps.py                     # dependências da API, como autenticação do usuário
│   │   ├── middleware.py               # middleware de request ID, logging de acesso e tratamento de falhas
│   │   └── routers/                    # endpoints HTTP organizados por recurso/capacidade
│   │       ├── auth.py
│   │       ├── categories.py
│   │       ├── health.py
│   │       ├── summary.py
│   │       ├── transactions.py
│   │       └── users.py
│   │
│   ├── core/
│   │   ├── config.py                   # configurações e variáveis de ambiente
│   │   ├── errors.py                   # exceções de domínio
│   │   ├── logging.py                  # configuração de logging estruturado e correlação
│   │   └── security.py                 # hashing de senhas e geração/validação de JWT
│   │
│   ├── infrastructure/
│   │   ├── database.py                 # engine SQLAlchemy e gerenciamento de sessões
│   │   ├── metrics.py                  # métricas HTTP e de negócio em formato Prometheus
│   │   └── tracing.py                  # configuração do OpenTelemetry e exportação OTLP
│   │
│   ├── models/                         # modelos SQLAlchemy e entidades persistidas
│   │   ├── category.py
│   │   ├── enums.py
│   │   ├── transaction.py
│   │   └── user.py
│   │
│   ├── schemas/                        # schemas Pydantic de entrada e saída da API
│   │   ├── auth.py
│   │   ├── category.py
│   │   ├── error.py
│   │   ├── summary.py
│   │   ├── transaction.py
│   │   └── user.py
│   │
│   └── services/                       # regras de negócio organizadas por capacidade
│       ├── auth_service.py
│       ├── category_service.py
│       ├── summary_service.py
│       └── transaction_service.py
│
├── alembic/                            # migrations versionadas do schema do PostgreSQL
│   ├── env.py
│   └── versions/
│
├── tests/                              # suíte de testes automatizados com pytest
│   ├── test_auth.py
│   ├── test_categories.py
│   ├── test_errors.py
│   ├── test_health.py
│   ├── test_metrics.py
│   ├── test_observability.py
│   ├── test_summary.py
│   ├── test_transactions.py
│   └── test_users.py
│
├── openspec/                           # artefatos do processo de Spec-Driven Development
│   ├── specs/                          # especificações vigentes do sistema
│   │   ├── auth/
│   │   ├── categories/
│   │   ├── financial-summary/
│   │   ├── observability/
│   │   ├── transactions/
│   │   └── users/
│   │
│   └── changes/
│       └── archive/
│           └── 2026-08-09-pocketledger-mvp/
│               ├── proposal.md         # motivação e escopo da mudança
│               ├── design.md           # decisões e desenho técnico
│               ├── tasks.md            # tarefas planejadas para implementação
│               └── specs/              # especificações produzidas durante a mudança
│
├── docker-compose.yml                  # ambiente local: aplicação, PostgreSQL e Jaeger
├── Dockerfile                          # imagem da aplicação
├── requirements.txt                    # dependências de produção
├── requirements-dev.txt                # dependências de desenvolvimento e testes
└── .env.example                        # exemplo das variáveis de ambiente necessárias
```

### Organização da aplicação

A aplicação é organizada por responsabilidades:

* **`api/`** — camada HTTP e integração com o FastAPI.
* **`core/`** — configurações, segurança, erros e logging.
* **`infrastructure/`** — integrações com tecnologias externas, como PostgreSQL, Prometheus e OpenTelemetry.
* **`services/`** — regras e operações de negócio.
* **`models/`** — modelos de persistência SQLAlchemy.
* **`schemas/`** — contratos de entrada e saída da API.
* **`tests/`** — testes organizados de acordo com as principais capacidades do sistema.
* **`openspec/`** — especificações e artefatos utilizados no processo de Spec-Driven Development.

O fluxo principal de uma requisição segue aproximadamente:

```text
HTTP Request
     │
     ▼
   API
     │
     ▼
  Service
     │
     ▼
   Model
     │
     ▼
PostgreSQL
```

Enquanto preocupações transversais como **autenticação, logging, métricas, tracing, tratamento de erros e request correlation** são aplicadas ao redor desse fluxo.

---

## 🛠️ Stack tecnológica

| Categoria | Tecnologias |
| --- | --- |
| **Backend** | Python 3.12 · FastAPI · Uvicorn · Pydantic v2 / pydantic-settings |
| **Persistência** | PostgreSQL 16 · SQLAlchemy 2.x (estilo `Mapped`/`mapped_column`) · Alembic (migrations) · psycopg 3 |
| **Autenticação** | PyJWT (HS256) · bcrypt |
| **Observabilidade** | Logging estruturado em JSON (formatter próprio, sem dependência extra) · `prometheus-client` + `prometheus-fastapi-instrumentator` (métricas) · OpenTelemetry SDK + instrumentação para FastAPI e SQLAlchemy · Jaeger (visualização de traces) |
| **Testes** | pytest · `TestClient` do FastAPI (via `httpx`) · banco PostgreSQL real dedicado a testes |
| **Infraestrutura** | Docker · Docker Compose (`app` + `db` + `jaeger`) |
| **Documentação da API** | Swagger UI e ReDoc, gerados automaticamente pelo FastAPI a partir dos schemas e rotas |
| **Processo/Documentação do projeto** | OpenSpec — proposta, especificações por capacidade, design técnico e plano de tarefas em `openspec/` |

> O desenho das camadas e o papel de cada componente estão em [Arquitetura](../../README.md#-arquitetura).


---

⬅️ [README](../../README.md) · 📚 [Índice da documentação](../README.md)
