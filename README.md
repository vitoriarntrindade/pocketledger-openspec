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

Os detalhes de cada uma dessas capacidades — o problema de fundo, o modelo de
dados, os fluxos e o contrato da API — estão na
[documentação do projeto](./docs/project/), indexada mais abaixo.

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
| **Routers** (`app/api/routers/`) | Tradução HTTP ↔ Python: recebem o request, validam o payload via schemas Pydantic e delegam a regra de negócio à camada de serviço. Não contêm lógica de negócio. |
| **Services** (`app/services/`) | Onde vivem as regras de negócio: validações cruzadas (ex.: tipo da transação vs. tipo da categoria), isolamento por usuário, cálculo do resumo financeiro. Levantam exceções de domínio (`app/core/errors.py`) em vez de retornar códigos HTTP diretamente. |
| **Models** (`app/models/`) | Entidades SQLAlchemy 2.x (`User`, `Category`, `Transaction`) e o enum compartilhado `TransactionType`. |
| **RequestIdMiddleware** (`app/api/middleware.py`) | Gera ou propaga o `request_id`, mede a duração da requisição, emite o log de acesso estruturado e — de forma central — captura qualquer exceção não tratada, convertendo-a em uma resposta 500 consistente. |
| **Exception handlers** (`app/api/error_handlers.py`) | Convertem exceções de domínio (`NotFoundError`, `ConflictError`, `ValidationError`, `UnauthorizedError`) e erros de validação do Pydantic em um envelope de erro JSON padronizado. |
| **PostgreSQL** | Fonte da verdade dos dados, com as regras de integridade (unicidade, chaves estrangeiras, `ON DELETE RESTRICT`) reforçadas no próprio schema, não apenas na aplicação. |
| **Jaeger** | Recebe os traces exportados via OTLP e permite visualizar o caminho completo de uma requisição, incluindo as consultas ao banco. |
| **`/metrics`** | Endpoint no formato de exposição do Prometheus, com métricas HTTP (via `prometheus-fastapi-instrumentator`) e contadores de negócio customizados. |

A árvore de diretórios que materializa essas camadas, a responsabilidade de
cada pacote e a stack tecnológica completa estão em
[Estrutura do projeto](./docs/project/project-structure.md).

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

## 📚 Documentação

A documentação de produto deste repositório vive em
[`docs/project/`](./docs/project/); o processo de desenvolvimento com agentes
vive em [`docs/`](./docs/README.md).

| Documento | O que você encontra lá |
| --- | --- |
| [🧭 Visão geral](./docs/project/overview.md) | O problema que o projeto resolve e como o sistema funciona do registro ao resumo financeiro. |
| [🚀 Primeiros passos](./docs/project/getting-started.md) | Quick start com Docker Compose, execução fora do Docker e a tabela completa de variáveis de ambiente. |
| [🗄️ Modelo de dados](./docs/project/data-model.md) | O diagrama ER das três tabelas, os relacionamentos em linguagem natural e o dicionário de cada campo. |
| [🔄 Principais fluxos](./docs/project/flows.md) | Os quatro fluxos ponta a ponta, com diagramas de sequência: autenticação, criação de transação, exclusão bloqueada e resumo. |
| [🔌 API](./docs/project/api.md) | Todos os endpoints, filtros, envelope de erro, um exemplo completo em `curl` e como usar o Swagger. |
| [🧪 Testes](./docs/project/testing.md) | Como rodar a suíte dentro e fora do Docker, e o que cada arquivo de teste cobre. |
| [📁 Estrutura do projeto](./docs/project/project-structure.md) | A árvore de diretórios, a responsabilidade de cada pacote e a stack tecnológica. |
| [📈 Possíveis evoluções](./docs/project/roadmap.md) | Os limites de escopo desta versão e o que viria a seguir. |

---

## 📐 OpenSpec e o processo de especificação

Este projeto foi construído de ponta a ponta seguindo Spec-Driven Development: primeiro a proposta e as especificações de comportamento, depois o design técnico, depois o plano de tarefas, e só então a implementação.

- **Especificações vigentes**, por capacidade: `openspec/specs/{auth,users,categories,transactions,financial-summary,observability}/spec.md`.
- **Histórico completo da proposta original** (motivação, decisões de design, lista de tarefas): `openspec/changes/archive/2026-08-09-pocketledger-mvp/`.

Cada requisito nas especificações segue o formato `SHALL` + cenários `WHEN`/`THEN`, e cada cenário corresponde a pelo menos um teste automatizado na suíte pytest.

### Por que o processo importa mais que o app

O PocketLedger é, antes de tudo, um laboratório: o objetivo com este
repositório é **aprender a usar modelos de linguagem de forma otimizada** —
projetar agentes especializados, montar workflows que se sustentam sozinhos,
tratar contexto como recurso escasso e chegar perto da potencialidade real do
desenvolvimento assistido por IA. O backend financeiro é o veículo; o método é
o objeto de estudo.

Na prática, isso aparece em coisas concretas:

- **Especificação antes de código.** Comportamento que existe só na conversa
  não existe. A spec é o que dá a um agente um alvo verificável em vez de uma
  instrução vaga.
- **Um gate determinístico como definition of done.** `make quality` decide o
  que está pronto — não a impressão de um modelo. Ferramenta barata responde o
  que ferramenta barata sabe responder; o modelo fica para julgamento.
- **Agentes especializados com roteamento de modelo por custo.** Cada agente em
  [`.claude/agents/`](./.claude/agents/) e [`.codex/agents/`](./.codex/agents/)
  tem escopo estreito e o modelo mais barato capaz de responder à sua pergunta.
- **Skills compartilhadas e carregadas sob demanda.** O conhecimento do projeto
  fica em [`.claude/skills/`](./.claude/skills/), entrando no contexto quando é
  necessário, em vez de ocupar espaço em toda interação.

O funcionamento completo desse pipeline — gates, hooks, agentes e o ciclo de
vida de uma mudança — está em
[`docs/agentic-development.md`](./docs/agentic-development.md).

---

## 📄 Licença

Este repositório não contém um arquivo de licença. Até que uma seja adicionada, todos os direitos permanecem reservados ao autor do projeto.
