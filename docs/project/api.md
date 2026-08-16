# 🔌 API

A referência completa dos endpoints, dos parâmetros de consulta, do envelope de erro e da documentação interativa gerada pelo FastAPI.

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

Com a aplicação em execução (veja [Quick Start](getting-started.md#-quick-start)):

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

Ambos são gerados automaticamente pelo FastAPI a partir dos schemas Pydantic e das rotas — não há um arquivo OpenAPI mantido manualmente.

**Para testar endpoints autenticados no Swagger:**

1. Execute `POST /api/v1/auth/register` (se ainda não tiver uma conta) e depois `POST /api/v1/auth/login` diretamente pela interface do Swagger.
2. Copie o valor de `access_token` da resposta.
3. Clique no botão **Authorize** (canto superior direito da página) e cole o token no campo (o Swagger adiciona o prefixo `Bearer` automaticamente).
4. A partir daí, qualquer endpoint protegido usará esse token automaticamente.

Bons pontos de partida para explorar a API pelo Swagger: `POST /api/v1/auth/register` → `POST /api/v1/auth/login` → `POST /api/v1/categories` → `POST /api/v1/transactions` → `GET /api/v1/summary`.

> Para subir a aplicação antes de chamar qualquer rota: [Primeiros passos](getting-started.md).


---

⬅️ [README](../../README.md) · 📚 [Índice da documentação](../README.md)
