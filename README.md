# PocketLedger

Um backend de controle financeiro pessoal construído com **FastAPI**, **PostgreSQL** e **SQLAlchemy 2.x**, com autenticação via JWT, isolamento total de dados entre usuários e uma stack de observabilidade completa (logs estruturados, métricas Prometheus e tracing distribuído com OpenTelemetry/Jaeger).

O projeto nasceu como um exercício prático de **Spec-Driven Development (SDD)** usando o [OpenSpec](https://github.com) — toda a especificação, o design técnico e o plano de implementação que originaram este código estão preservados em `openspec/` (veja a seção [OpenSpec e o processo de especificação](#-openspec-e-o-processo-de-especificação)).

> 📚 **Documentação completa** em [`/docs`](./docs/README.md)  
> 🚀 **Começar a desenvolver**: [`docs/agentic-development.md`](./docs/agentic-development.md) — gates de qualidade, ciclo de vida de uma mudança e desenvolvimento autônomo  
> 📜 **Regras do projeto**: [`CLAUDE.md`](./CLAUDE.md)  
> 🔐 **Segurança**: [`docs/security/SECURITY.md`](./docs/security/SECURITY.md)

> **Definition of done:** `make quality` — formatação, lint, tipagem, testes,
> cobertura ≥ 95%, varredura de segredos, scan de segurança e validação
> OpenSpec. É o mesmo comando que roda localmente e na CI.

---

## 📌 Sobre o projeto

O **PocketLedger** é uma API backend (sem frontend) que permite que cada usuário registre suas próprias receitas e despesas, organize essas transações em categorias e consulte, a qualquer momento, um resumo fiel da sua situação financeira em um período.

O sistema foi desenhado em torno de três conceitos centrais:

- **Usuário** — dono de todos os seus dados. Autentica-se via e-mail e senha e recebe um token JWT.
- **Categoria** — um rótulo pertencente a um único usuário, com um tipo fixo (`income` ou `expense`), usado para classificar transações (ex.: *Alimentação*, *Salário*, *Transporte*).
- **Transação** — um lançamento de receita ou despesa, com valor, data, descrição e uma categoria associada.

A partir dessas três entidades, a API responde perguntas como "quanto recebi este mês?", "quanto gastei em uma categoria?", "qual foi meu saldo?" e "quais foram minhas maiores despesas?" — sempre com os dados de um único usuário, nunca misturando informações entre contas.

**Funcionalidades principais:**

- Cadastro e login de usuários com autenticação JWT.
- CRUD de categorias, com tipo imutável e proteção contra exclusão de categorias em uso.
- CRUD de transações, com validação de valores monetários, filtros combináveis, ordenação e paginação.
- Resumo financeiro por período, com saldo sempre calculado (nunca armazenado) a partir das transações reais.
- Observabilidade de ponta a ponta: cada requisição pode ser rastreada por logs, métricas e trace de forma correlacionada.

---

## 🎯 Problema que o projeto resolve

Controlar receitas e despesas pessoais em planilhas ou anotações soltas tem problemas conhecidos:

- **Inconsistência de dados**: nada impede que um valor negativo, um centavo perdido por arredondamento de `float`, ou uma categoria inexistente entre nos registros.
- **Falta de isolamento**: em soluções caseiras compartilhadas, é fácil um dado de uma pessoa se misturar com o de outra.
- **Saldo "solto"**: quando o saldo é digitado manualmente em vez de calculado a partir dos lançamentos, ele pode ficar desatualizado ou incoerente com o histórico real.
- **Dificuldade de investigar problemas**: quando algo dá errado, não há como saber o que aconteceu sem reproduzir o cenário manualmente.

O PocketLedger resolve isso impondo, na própria API e no banco de dados, as regras que uma planilha não consegue garantir:

- valores monetários são sempre `Decimal`/`NUMERIC(12,2)`, nunca `float`;
- toda consulta é automaticamente restrita ao usuário autenticado — não existe *nenhum* caminho de código que leia dados de outro usuário;
- o saldo do resumo financeiro é **sempre** `total_income - total_expenses`, calculado no momento da consulta, nunca armazenado como um valor independente;
- uma categoria em uso não pode ser excluída (a integridade referencial é garantida pelo próprio banco);
- cada requisição pode ser encontrada nos logs, nas métricas e no trace correspondente através de um único identificador (`request_id`).

**Quem se beneficia:** desenvolvedores que querem uma base de referência de uma API bem especificada, testada e observável; e, no domínio do produto, qualquer pessoa que precise de um controle financeiro pessoal simples, correto e auditável.

---

## 💡 Como o sistema funciona

Na prática, o fluxo de uso é:

1. O usuário se registra (`POST /api/v1/auth/register`) e faz login (`POST /api/v1/auth/login`), recebendo um token JWT de curta duração (60 minutos por padrão).
2. Com o token, o usuário cria suas próprias categorias (`POST /api/v1/categories`), cada uma com um tipo fixo — receita ou despesa.
3. O usuário registra transações (`POST /api/v1/transactions`), associando cada uma a uma de suas categorias. A API garante que o tipo da transação corresponda ao tipo da categoria.
4. O usuário consulta suas transações com filtros por período, tipo e categoria, ordenação por data ou valor, e paginação (`GET /api/v1/transactions`).
5. O usuário consulta um resumo financeiro de qualquer período (`GET /api/v1/summary`), obtendo totais, contagens, saldo e a distribuição de despesas por categoria — tudo calculado em tempo real a partir das transações existentes.

Por trás de cada requisição, uma camada de middleware atribui (ou propaga) um `request_id`, mede a duração da chamada, e — em caso de erro — garante uma resposta padronizada e um log detalhado, sem nunca expor detalhes internos ao cliente.

---

## 🏗️ Arquitetura

O PocketLedger segue uma arquitetura em camadas simples e direta: **rotas → serviços → modelos → banco de dados**, com um middleware transversal cuidando de correlação de requisições e tratamento de erros, e três canais de observabilidade (logs, métricas e tracing) alimentados a partir do mesmo ciclo de vida da requisição.

```mermaid
flowchart LR
    Client(["Cliente HTTP<br/>Swagger UI / curl / apps"])

    subgraph API["API PocketLedger (FastAPI)"]
        direction TB
        MW["RequestIdMiddleware<br/>request_id · duração · captura de erros não tratados"]
        Routers["Routers<br/>auth · users · categories · transactions · summary · health"]
        Services["Camada de serviço<br/>auth_service · category_service · transaction_service · summary_service"]
        Models["Modelos SQLAlchemy 2.x<br/>User · Category · Transaction"]
        MW --> Routers --> Services --> Models
    end

    DB[("PostgreSQL 16")]
    Jaeger[["Jaeger<br/>tracing distribuído"]]
    Metrics["/metrics<br/>formato Prometheus/"]
    Logs[["stdout<br/>logs JSON estruturados"]]

    Client -->|"HTTP + Authorization: Bearer &lt;JWT&gt;"| MW
    Models -->|"psycopg 3"| DB

    MW -.->|"OTLP (gRPC)"| Jaeger
    MW -.->|"logging"| Logs
    API -.->|"instrumentação HTTP + contadores de negócio"| Metrics
```

### Responsabilidade de cada componente

| Componente | Responsabilidade |
| --- | --- |
| **Routers** (`app/routers/`) | Tradução HTTP ↔ Python: recebem o request, validam o payload via schemas Pydantic e delegam a regra de negócio à camada de serviço. Não contêm lógica de negócio. |
| **Services** (`app/services/`) | Onde vivem as regras de negócio: validações cruzadas (ex.: tipo da transação vs. tipo da categoria), isolamento por usuário, cálculo do resumo financeiro. Levantam exceções de domínio (`app/errors.py`) em vez de retornar códigos HTTP diretamente. |
| **Models** (`app/models/`) | Entidades SQLAlchemy 2.x (`User`, `Category`, `Transaction`) e o enum compartilhado `TransactionType`. |
| **RequestIdMiddleware** (`app/middleware.py`) | Gera ou propaga o `request_id`, mede a duração da requisição, emite o log de acesso estruturado e — de forma central — captura qualquer exceção não tratada, convertendo-a em uma resposta 500 consistente. |
| **Exception handlers** (`app/error_handlers.py`) | Convertem exceções de domínio (`NotFoundError`, `ConflictError`, `ValidationError`, `UnauthorizedError`) e erros de validação do Pydantic em um envelope de erro JSON padronizado. |
| **PostgreSQL** | Fonte da verdade dos dados, com as regras de integridade (unicidade, chaves estrangeiras, `ON DELETE RESTRICT`) reforçadas no próprio schema, não apenas na aplicação. |
| **Jaeger** | Recebe os traces exportados via OTLP e permite visualizar o caminho completo de uma requisição, incluindo as consultas ao banco. |
| **`/metrics`** | Endpoint no formato de exposição do Prometheus, com métricas HTTP (via `prometheus-fastapi-instrumentator`) e contadores de negócio customizados. |

---

## 🗄️ Modelo de dados

O modelo de dados tem três tabelas. Não há hierarquia de categorias, múltiplas contas bancárias ou qualquer entidade além destas três.

```mermaid
erDiagram
    USERS ||--o{ CATEGORIES : "possui"
    USERS ||--o{ TRANSACTIONS : "possui"
    CATEGORIES ||--o{ TRANSACTIONS : "classifica"

    USERS {
        int id PK
        string name
        string email "unique"
        string hashed_password
        datetime created_at
    }

    CATEGORIES {
        int id PK
        int user_id FK
        string name
        enum type "income | expense"
        datetime created_at
    }

    TRANSACTIONS {
        int id PK
        int user_id FK
        int category_id FK "ON DELETE RESTRICT"
        enum type "income | expense"
        text description
        decimal amount "NUMERIC(12,2)"
        date transaction_date
        datetime created_at
    }
```

### Relacionamentos, em linguagem natural

- **Um usuário possui várias categorias.** Cada categoria pertence a exatamente um usuário (`categories.user_id → users.id`). Não existe categoria compartilhada entre contas.
- **Um usuário possui várias transações.** Cada transação pertence a exatamente um usuário (`transactions.user_id → users.id`), independentemente da categoria usada.
- **Uma categoria pode ser referenciada por várias transações; uma transação referencia exatamente uma categoria.** Esse relacionamento (`transactions.category_id → categories.id`) usa `ON DELETE RESTRICT`: o banco recusa a exclusão de qualquer categoria que ainda tenha ao menos uma transação apontando para ela. A API traduz essa recusa em uma resposta `409 Conflict`.
- **O tipo (`income`/`expense`) é um único enum do PostgreSQL (`transaction_type`), compartilhado entre `categories.type` e `transactions.type`.** A regra "o tipo da transação deve ser igual ao tipo da categoria usada" não é imposta por uma constraint de banco entre as duas tabelas — é validada explicitamente na camada de serviço, tanto na criação quanto na edição de uma transação (ver [Regras de negócio](#-regras-de-negócio)).

---

## 📚 Dicionário das entidades

### `users`

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `id` | `int` (PK) | — | Identificador único, gerado pelo banco. |
| `name` | `string(255)` | Sim | Nome do usuário. |
| `email` | `string(255)` | Sim | E-mail do usuário. Único em todo o sistema (índice único). |
| `hashed_password` | `string(255)` | Sim | Hash bcrypt da senha. **Nunca** é retornado em nenhuma resposta da API. |
| `created_at` | `datetime` (com timezone) | — | Data/hora de criação da conta, definida automaticamente. |

### `categories`

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `id` | `int` (PK) | — | Identificador único. |
| `user_id` | `int` (FK → `users.id`) | Sim | Dono da categoria. |
| `name` | `string(100)` | Sim | Nome da categoria (ex.: "Alimentação"). |
| `type` | `enum` (`income` \| `expense`) | Sim | Tipo fixo, definido na criação e **imutável** depois disso. |
| `created_at` | `datetime` (com timezone) | — | Data/hora de criação. |

Restrição de unicidade: `(user_id, name, type)` — o mesmo usuário não pode ter duas categorias com o mesmo nome **e** o mesmo tipo, mas pode reaproveitar um nome em tipos diferentes (ex.: "Outros" como receita e "Outros" como despesa são categorias distintas e válidas).

### `transactions`

| Campo | Tipo | Obrigatório | Descrição |
| --- | --- | --- | --- |
| `id` | `int` (PK) | — | Identificador único. |
| `user_id` | `int` (FK → `users.id`) | Sim | Dono da transação. |
| `category_id` | `int` (FK → `categories.id`, `ON DELETE RESTRICT`) | Sim | Categoria usada para classificar a transação. Deve pertencer ao mesmo usuário e ter o mesmo `type` da transação. |
| `type` | `enum` (`income` \| `expense`) | Sim | Tipo da transação. |
| `description` | `text` | Sim | Descrição livre (até 1000 caracteres na validação da API). |
| `amount` | `numeric(12,2)` | Sim | Valor monetário. Deve ser estritamente maior que zero e ter no máximo 2 casas decimais. Representado como `Decimal` em toda a aplicação — nunca `float`. |
| `transaction_date` | `date` | Sim | Data do lançamento financeiro, informada pelo usuário e independente de `created_at` (permite lançar uma transação retroativamente). |
| `created_at` | `datetime` (com timezone) | — | Momento em que o registro foi efetivamente criado no sistema. |

---

## 🔄 Principais fluxos

### 1. Registro, login e acesso autenticado

Quem inicia: um novo usuário. Endpoints: `POST /api/v1/auth/register`, `POST /api/v1/auth/login`, `GET /api/v1/users/me`.

```mermaid
sequenceDiagram
    actor U as Usuário
    participant Auth as /api/v1/auth
    participant Users as /api/v1/users/me
    participant DB as PostgreSQL

    U->>Auth: POST /register {name, email, password}
    Auth->>DB: INSERT em users (senha com hash bcrypt)
    DB-->>Auth: usuário criado
    Auth-->>U: 201 {id, name, email}

    U->>Auth: POST /login {email, password}
    Auth->>DB: SELECT usuário por email
    Auth->>Auth: verifica hash da senha (bcrypt)
    Auth-->>U: 200 {access_token, token_type: "bearer"}

    U->>Users: GET /me (Authorization: Bearer <token>)
    Users->>Users: decodifica e valida o JWT
    Users-->>U: 200 {id, name, email}
```

Resultado: um token JWT válido por 60 minutos (sem refresh token — expirado, o único caminho é logar novamente).

### 2. Criar transação com validação de categoria

Quem inicia: um usuário autenticado. Endpoint: `POST /api/v1/transactions`. Entidades afetadas: `Transaction` (criada), `Category` (apenas consultada).

```mermaid
sequenceDiagram
    actor U as Usuário autenticado
    participant R as router (transactions)
    participant S as transaction_service
    participant CS as category_service
    participant DB as PostgreSQL

    U->>R: POST /api/v1/transactions {type, category_id, amount, ...}
    R->>S: create_transaction(...)
    S->>CS: get_owned_category(category_id)
    CS->>DB: SELECT categoria WHERE id=? AND user_id=?
    DB-->>CS: categoria (ou nenhuma linha)

    alt categoria não existe ou é de outro usuário
        CS-->>S: NotFoundError
        S-->>R: propaga erro
        R-->>U: 404 Not Found
    else tipo da transação ≠ tipo da categoria
        S-->>R: ValidationError
        R-->>U: 400 Bad Request
    else válido
        S->>DB: INSERT em transactions
        DB-->>S: transação criada
        S-->>R: Transaction
        R-->>U: 201 Created
    end
```

### 3. Excluir categoria em uso (bloqueio de integridade)

Quem inicia: um usuário autenticado. Endpoint: `DELETE /api/v1/categories/{category_id}`. Entidade afetada: `Category` (a exclusão é recusada).

```mermaid
sequenceDiagram
    actor U as Usuário autenticado
    participant R as router (categories)
    participant S as category_service
    participant DB as PostgreSQL

    U->>R: DELETE /api/v1/categories/{id}
    R->>S: delete_category(id)
    S->>DB: DELETE FROM categories WHERE id=?
    DB-->>S: IntegrityError (FK RESTRICT: existem transações usando essa categoria)
    S->>S: converte IntegrityError em ConflictError
    S-->>R: ConflictError
    R-->>U: 409 Conflict
```

Resultado: a categoria permanece intacta. Ela só pode ser excluída depois que todas as transações que a referenciam forem removidas ou reatribuídas a outra categoria.

### 4. Resumo financeiro de um período

Quem inicia: um usuário autenticado. Endpoint: `GET /api/v1/summary`. Entidades afetadas: nenhuma é alterada — apenas `Transaction` e `Category` são lidas.

O serviço filtra as transações do usuário autenticado dentro do intervalo `[start_date, end_date]`, soma receitas e despesas separadamente, conta os lançamentos de cada tipo, agrupa as despesas por categoria e calcula `balance = total_income - total_expenses` — tudo na mesma consulta, sem nenhum valor de saldo armazenado previamente.

---

## 🔌 API

A API é versionada sob o prefixo `/api/v1`. Os endpoints operacionais (`/health`, `/ready`, `/metrics`) ficam na raiz, fora da versão.

Todos os endpoints, exceto registro e login, exigem o header `Authorization: Bearer <token>`.

### Autenticação — `/api/v1/auth`

| Método | Rota | Objetivo |
| --- | --- | --- |
| `POST` | `/api/v1/auth/register` | Cria uma nova conta de usuário. |
| `POST` | `/api/v1/auth/login` | Autentica e retorna um token de acesso JWT. |

**`POST /api/v1/auth/register`**

Body:
```json
{
  "name": "Alice",
  "email": "alice@example.com",
  "password": "supersecret123"
}
```

Resposta `201 Created`:
```json
{
  "id": 1,
  "name": "Alice",
  "email": "alice@example.com"
}
```

Códigos importantes: `409 Conflict` se o e-mail já existir; `422 Unprocessable Entity` se a senha tiver menos que o mínimo configurado (8 caracteres por padrão) ou o e-mail for inválido.

**`POST /api/v1/auth/login`**

Body:
```json
{ "email": "alice@example.com", "password": "supersecret123" }
```

Resposta `200 OK`:
```json
{ "access_token": "eyJhbGciOiJIUzI1NiIs...", "token_type": "bearer" }
```

Código importante: `401 Unauthorized` para e-mail inexistente **ou** senha incorreta — a resposta é idêntica nos dois casos, para não revelar qual dado estava errado.

### Usuário — `/api/v1/users`

| Método | Rota | Objetivo |
| --- | --- | --- |
| `GET` | `/api/v1/users/me` | Retorna o perfil do usuário autenticado. |

Não existe (e não deve existir) nenhuma rota que aceite o id de outro usuário — o próprio token define de quem são os dados retornados.

### Categorias — `/api/v1/categories`

| Método | Rota | Objetivo |
| --- | --- | --- |
| `POST` | `/api/v1/categories` | Cria uma categoria. |
| `GET` | `/api/v1/categories` | Lista as categorias do usuário autenticado. |
| `PATCH` | `/api/v1/categories/{category_id}` | Renomeia uma categoria (o `type` não pode ser alterado). |
| `DELETE` | `/api/v1/categories/{category_id}` | Exclui uma categoria, se ela não estiver em uso. |

### Transações — `/api/v1/transactions`

| Método | Rota | Objetivo |
| --- | --- | --- |
| `POST` | `/api/v1/transactions` | Cria uma transação. |
| `GET` | `/api/v1/transactions` | Lista transações, com filtros, ordenação e paginação. |
| `GET` | `/api/v1/transactions/{transaction_id}` | Consulta uma transação específica. |
| `PATCH` | `/api/v1/transactions/{transaction_id}` | Edita uma transação. |
| `DELETE` | `/api/v1/transactions/{transaction_id}` | Exclui uma transação. |

Parâmetros de consulta de `GET /api/v1/transactions` (todos opcionais e combináveis):

| Parâmetro | Valores | Padrão | Descrição |
| --- | --- | --- | --- |
| `start_date` / `end_date` | data (`YYYY-MM-DD`) | — | Filtra por intervalo de `transaction_date`. |
| `type` | `income` \| `expense` | — | Filtra por tipo. |
| `category_id` | inteiro | — | Filtra por categoria. |
| `sort_by` | `date` \| `amount` | `date` | Campo de ordenação. |
| `order` | `asc` \| `desc` | `desc` | Direção da ordenação. |
| `page` | inteiro ≥ 1 | `1` | Página da listagem. |
| `page_size` | inteiro (1–100) | `20` | Itens por página. |

### Resumo financeiro — `/api/v1/summary`

| Método | Rota | Objetivo |
| --- | --- | --- |
| `GET` | `/api/v1/summary?start_date=&end_date=` | Retorna o resumo financeiro do período informado (ambos os parâmetros são obrigatórios). |

### Operacionais (sem prefixo de versão)

| Método | Rota | Objetivo |
| --- | --- | --- |
| `GET` | `/health` | Verifica se o processo da aplicação está de pé. |
| `GET` | `/ready` | Verifica também a conectividade com o banco de dados (retorna `503` se o banco estiver inacessível). |
| `GET` | `/metrics` | Métricas no formato de exposição do Prometheus. |

### Formato de erro

Todo erro da API segue o mesmo envelope, com o `request_id` da requisição (o mesmo valor do header `X-Request-ID` da resposta):

```json
{
  "error": {
    "code": "validation_error",
    "message": "Transaction type must match the category's type.",
    "request_id": "74410f3e-3138-4c72-b8b4-96c6f4920bb0"
  }
}
```

| Código HTTP | `code` | Quando ocorre |
| --- | --- | --- |
| `400` | `validation_error` | Regra de negócio violada (ex.: tipo da transação incompatível com a categoria). |
| `401` | `unauthorized` | Token ausente, malformado, expirado, ou credenciais de login inválidas. |
| `404` | `not_found` | Recurso inexistente, ou pertencente a outro usuário (tratado como inexistente). |
| `409` | `conflict` | Conflito com o estado atual (e-mail/categoria duplicados, categoria em uso). |
| `422` | `validation_error` | Payload inválido segundo o schema Pydantic (campo faltando, tipo errado, valor fora das regras). |
| `500` | `internal_error` | Falha inesperada. A resposta nunca inclui stack trace ou detalhes internos. |

### Exemplo prático: ciclo completo de categoria + transação

```bash
# 1. Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","password":"supersecret123"}' \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

# 2. Criar uma categoria de despesa
curl -s -X POST http://localhost:8000/api/v1/categories \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"name":"Alimentacao","type":"expense"}'
# -> 201 {"id":1,"name":"Alimentacao","type":"expense"}

# 3. Listar categorias
curl -s http://localhost:8000/api/v1/categories -H "Authorization: Bearer $TOKEN"

# 4. Criar uma transação usando essa categoria
curl -s -X POST http://localhost:8000/api/v1/transactions \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"type":"expense","description":"Almoco","amount":"45.50","transaction_date":"2026-01-15","category_id":1}'
# -> 201 {"id":1,"type":"expense","description":"Almoco","amount":"45.50", ...}

# 5. Consultar o resumo do período
curl -s "http://localhost:8000/api/v1/summary?start_date=2026-01-01&end_date=2026-01-31" \
  -H "Authorization: Bearer $TOKEN"
# -> {"total_income":"0","total_expenses":"45.50","balance":"-45.50", ...}

# 6. Tentar excluir a categoria em uso (é bloqueado)
curl -s -i -X DELETE http://localhost:8000/api/v1/categories/1 -H "Authorization: Bearer $TOKEN"
# -> 409 Conflict

# 7. Excluir a transação e, então, a categoria
curl -s -X DELETE http://localhost:8000/api/v1/transactions/1 -H "Authorization: Bearer $TOKEN"
curl -s -i -X DELETE http://localhost:8000/api/v1/categories/1 -H "Authorization: Bearer $TOKEN"
# -> 204 No Content
```

---

## 📖 Swagger / OpenAPI

Com a aplicação em execução (veja [Quick Start](#-quick-start)):

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

Ambos são gerados automaticamente pelo FastAPI a partir dos schemas Pydantic e das rotas — não há um arquivo OpenAPI mantido manualmente.

**Para testar endpoints autenticados no Swagger:**

1. Execute `POST /api/v1/auth/register` (se ainda não tiver uma conta) e depois `POST /api/v1/auth/login` diretamente pela interface do Swagger.
2. Copie o valor de `access_token` da resposta.
3. Clique no botão **Authorize** (canto superior direito da página) e cole o token no campo (o Swagger adiciona o prefixo `Bearer` automaticamente).
4. A partir daí, qualquer endpoint protegido usará esse token automaticamente.

Bons pontos de partida para explorar a API pelo Swagger: `POST /api/v1/auth/register` → `POST /api/v1/auth/login` → `POST /api/v1/categories` → `POST /api/v1/transactions` → `GET /api/v1/summary`.

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

Um exemplo completo está em [`.env.example`](.env.example) — nenhum segredo real está commitado; os valores ali são placeholders explicitamente marcados como "dev-only" / "change-me".

---

## 🧪 Testes

A suíte de testes usa **pytest** + o `TestClient` do FastAPI (baseado em `httpx`), executando contra um banco PostgreSQL real dedicado a testes (`pocketledger_test`) — não contra SQLite ou mocks — porque várias regras de negócio dependem de comportamento real do banco (constraint de unicidade, `ON DELETE RESTRICT`).

### Executando dentro do Docker Compose

```bash
# na primeira vez, crie o banco de testes:
docker compose exec db psql -U pocketledger -d pocketledger \
  -c "CREATE DATABASE pocketledger_test;"

docker compose run --rm app-test pytest
```

### Executando localmente (fora do Docker)

```bash
pip install -r requirements-dev.txt
TEST_DATABASE_URL="postgresql+psycopg://pocketledger:pocketledger@localhost:5433/pocketledger_test" pytest
```

### O que está cobrito

A suíte tem 81 testes de aplicação, organizados por capacidade (mesma divisão usada nas especificações em `openspec/specs/`):

| Arquivo | Foco |
| --- | --- |
| `tests/test_auth.py` | Registro, login, validação de token (ausente/expirado/malformado). |
| `tests/test_users.py` | Perfil próprio e ausência de rota para outro usuário. |
| `tests/test_categories.py` | Criação, unicidade por nome+tipo, imutabilidade do tipo, renomeação, bloqueio de exclusão em uso, isolamento entre usuários. |
| `tests/test_transactions.py` | Criação, validação de valor e tipo, edição, exclusão, isolamento, filtros combinados, ordenação, paginação. |
| `tests/test_summary.py` | Cálculo do resumo, saldo derivado, período vazio, isolamento entre usuários. |
| `tests/test_errors.py` | Mapeamento de cada exceção de domínio para o código HTTP e envelope de erro correspondente; resposta genérica e sem fuga de detalhes em erros inesperados. |
| `tests/test_observability.py` | Formato JSON dos logs, correlação de `request_id`/`trace_id`, ausência de dados sensíveis nos logs, nível de log correto para erros esperados vs. inesperados. |
| `tests/test_metrics.py` | Métricas HTTP e contadores de negócio (`pocketledger_transactions_created_total`, `pocketledger_summaries_requested_total`). |
| `tests/test_health.py` | `/health` e `/ready` (incluindo o cenário de banco indisponível). |

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

## 🔐 Regras de negócio

Regras impostas pela camada de serviço, pelos schemas Pydantic e/ou pelo schema do banco de dados:

- **Senhas** são armazenadas apenas como hash bcrypt e nunca aparecem em nenhuma resposta da API (nem no registro, nem no login).
- **E-mail** é único em todo o sistema — uma segunda tentativa de registro com o mesmo e-mail é recusada (`409`).
- O **token de acesso** expira em 60 minutos (configurável) e não pode ser renovado nem revogado nesta versão: expirado, o usuário precisa logar novamente.
- **Toda categoria pertence a exatamente um usuário**, e seu nome só precisa ser único combinado com o tipo (`user_id + name + type`) — o mesmo nome pode existir como receita e como despesa.
- **O tipo de uma categoria é imutável** após a criação: o schema de atualização (`CategoryUpdate`) só aceita o campo `name`.
- **Uma categoria referenciada por ao menos uma transação não pode ser excluída** — a constraint `ON DELETE RESTRICT` no banco garante isso mesmo contra um acesso direto ao banco, e a API traduz a falha em `409 Conflict`.
- **O tipo de uma transação deve ser igual ao tipo da categoria usada.** Essa verificação ocorre tanto na criação quanto na edição, validando o par (tipo final, categoria final) *antes* de qualquer alteração — uma edição rejeitada não modifica nada.
- **Uma categoria só pode ser usada por transações do mesmo usuário que a criou.** Referenciar uma categoria de outro usuário resulta em `404`, como se ela não existisse.
- **O valor de uma transação deve ser estritamente maior que zero e ter no máximo duas casas decimais**, representado como `Decimal` (nunca `float`) tanto no código Python quanto no tipo `NUMERIC(12,2)` do PostgreSQL.
- **A data da transação é independente da data de criação** — é possível registrar hoje uma transação com data no passado.
- **Nenhum usuário acessa, edita ou exclui categorias ou transações de outro usuário.** Todas as consultas filtram por `user_id`; um acesso cruzado sempre retorna `404`, nunca `403` (o recurso "não existe" do ponto de vista de quem não é o dono).
- **O saldo do resumo financeiro nunca é armazenado.** Ele é sempre `total_income - total_expenses`, recalculado a partir das transações no momento da consulta — criar ou excluir uma transação reflete imediatamente no próximo resumo, sem nenhuma etapa de sincronização.
- **Um período sem transações retorna zeros e uma lista vazia**, não um erro.
- **A listagem de transações é sempre paginada** (20 itens por padrão, no máximo 100), retornando também a contagem total de itens que atendem aos filtros.
- **Falhas de negócio esperadas (400/401/404/409/422) nunca são registradas como `ERROR` nos logs** — apenas falhas inesperadas (500) recebem esse nível, com stack trace completo.
- **Toda resposta, de sucesso ou de erro, carrega o header `X-Request-ID`**, que também aparece nos logs e é correlacionável com o `trace_id` do OpenTelemetry.

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

---

## 📈 Possíveis evoluções

Estes pontos estão documentados como decisões deliberadas de escopo no `design.md` da proposta original (`openspec/changes/archive/2026-08-09-pocketledger-mvp/design.md`), não são lacunas acidentais:

- **Refresh token e logout/revogação de token.** A versão atual usa apenas um token de acesso de curta duração; um token válido não pode ser invalidado antes de expirar. Evoluir para um par access/refresh token com revogação server-side é o próximo passo natural caso o sistema precise de um fluxo de logout real.
- **Stack de observabilidade mais completa.** Hoje o ambiente local sobe apenas `app` + `db` + `jaeger`; métricas são expostas em `/metrics` mas não há um Prometheus nem um Grafana rodando localmente para consultá-las historicamente. Como as métricas já seguem o formato de exposição do Prometheus, um servidor Prometheus e dashboards no Grafana podem ser adicionados sem qualquer mudança na aplicação.
- **Sessão de banco síncrona sob handlers assíncronos.** O acesso ao banco usa `SQLAlchemy` síncrono dentro do threadpool do FastAPI — uma escolha deliberada para manter a simplicidade nesta escala. Migrar para SQLAlchemy assíncrono (`asyncpg`) só se justificaria se o sistema precisasse suportar uma carga de tráfego real e concorrente.
- **Segurança de segredos e deploy de produção.** O design documenta explicitamente que gerenciamento de segredos, TLS e topologia de deploy de produção estão fora do escopo desta versão, que roda apenas localmente via Docker Compose.
- **Rotação de chaves JWT.** A versão atual usa uma única chave estática para assinar todos os tokens; rotacionar a chave invalida todos os tokens outstanding. Para um serviço de produção com tokens de longa duração, implementar rotação gradual (múltiplas chaves ativas, rollover) seria necessário. Ver [SECURITY.md](SECURITY.md) para detalhes.
- **Política de versionamento e deprecação de API.** Além do prefixo `/api/v1`, a aplicação não possui uma política formal de versionamento. A estratégia de migração da v1 para v2 fica para uma evolução futura. Ver [SECURITY.md](SECURITY.md).

---

## 📄 Licença

Este repositório não contém um arquivo de licença. Até que uma seja adicionada, todos os direitos permanecem reservados ao autor do projeto.

---

## 📐 OpenSpec e o processo de especificação

Este projeto foi construído de ponta a ponta seguindo Spec-Driven Development: primeiro a proposta e as especificações de comportamento, depois o design técnico, depois o plano de tarefas, e só então a implementação.

- **Especificações vigentes**, por capacidade: `openspec/specs/{auth,users,categories,transactions,financial-summary,observability}/spec.md`.
- **Histórico completo da proposta original** (motivação, decisões de design, lista de tarefas): `openspec/changes/archive/2026-08-09-pocketledger-mvp/`.

Cada requisito nas especificações segue o formato `SHALL` + cenários `WHEN`/`THEN`, e cada cenário corresponde a pelo menos um teste automatizado na suíte pytest.
