# 🧪 Testes

Como a suíte é executada, dentro e fora do Docker, e o que cada arquivo de teste cobre.

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

> A definition of done do repositório é `make quality`, descrita em [agentic-development.md](../agentic-development.md).

---

⬅️ [README](../../README.md) · 📚 [Índice da documentação](../README.md)
