# 🧭 Visão geral

Por que o PocketLedger existe e como ele é usado na prática — o problema que ele resolve e o caminho que um usuário percorre da conta ao resumo financeiro.

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

> Os endpoints citados aqui estão detalhados em [API](api.md); as garantias que o sistema impõe estão em [Regras de negócio](../../README.md#-regras-de-negócio).


---

⬅️ [README](../../README.md) · 📚 [Índice da documentação](../README.md)
