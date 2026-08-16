# 🔄 Principais fluxos

Os quatro caminhos que atravessam o sistema de ponta a ponta, do request HTTP até o PostgreSQL.

## 1. Registro, login e acesso autenticado

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

## 2. Criar transação com validação de categoria

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

## 3. Excluir categoria em uso (bloqueio de integridade)

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

## 4. Resumo financeiro de um período

Quem inicia: um usuário autenticado. Endpoint: `GET /api/v1/summary`. Entidades afetadas: nenhuma é alterada — apenas `Transaction` e `Category` são lidas.

O serviço filtra as transações do usuário autenticado dentro do intervalo `[start_date, end_date]`, soma receitas e despesas separadamente, conta os lançamentos de cada tipo, agrupa as despesas por categoria e calcula `balance = total_income - total_expenses` — tudo na mesma consulta, sem nenhum valor de saldo armazenado previamente.

> As entidades envolvidas estão descritas em [Modelo de dados](data-model.md); o contrato HTTP correspondente, em [API](api.md).

---

⬅️ [README](../../README.md) · 📚 [Índice da documentação](../README.md)
