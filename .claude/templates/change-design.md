# Design — [Título da Mudança]

## Resumo de Decisões

**Para leitores com pressa:** 1-3 decisões-chave tomadas e por quê.

## Decisões Arquiteturais

### 1. [Nome da Decisão]

**Escolha:**
- Opção A — Descrição, prós, contras
- Opção B — Descrição, prós, contras
- **Selecionada: Opção A**

**Rationale:**
- Por quê essa opção?
- Que trade-offs estamos aceitando?
- Que alternativas foram consideradas e por quê descartadas?

**Impacto:**
- Quais componentes/módulos são afetados?
- Há mudanças na API pública?
- Há mudanças no banco de dados?

**Reverso/Reverter:**
- Como desfazer essa decisão se necessário?

---

## Arquitetura & Fluxo

Diagrama(s) ou descrição textual do fluxo de dados / componentes afetados.

```
[Descrição visual ou texto do fluxo]
```

---

## Mudanças de Banco de Dados

- [ ] Migration necessária? **Sim / Não**
  - Se sim: descrever o que muda
  - Retrocompatibilidade mantida? Como?
  - Reversibilidade: como fazer rollback?

---

## Mudanças de API

Se houver mudanças em endpoints, schemas, ou versionamento:

### Novos Endpoints

```yaml
POST /api/v1/new-endpoint
  Request:
    - field1 (type): description
  Response:
    - field1 (type): description
  Status Codes:
    - 200: Success
    - 400: Validation error
    - 401: Unauthorized
```

### Endpoints Modificados

```yaml
PATCH /api/v1/existing-endpoint
  Changed Fields:
    - old_field → renamed_to_new_field
  Deprecation:
    - old_field deprecated, use new_field instead
    - Removal planned: 2026-12-31
```

### Endpoints Removidos

```yaml
DELETE /api/v1/deprecated-endpoint
  Removal Date: 2026-12-31
  Migration Path: Use POST /api/v1/new-endpoint instead
```

---

## Mudanças de Infraestrutura

### Variáveis de Ambiente

| Var | Novo/Mudado | Descrição | Padrão |
|-----|-------------|-----------|--------|
| NEW_VAR | Novo | Descrição | valor |
| OLD_VAR | Deprecated | Por quê? | N/A |

### Docker / Imagem

- [ ] Dockerfile mudou? Descrever
- [ ] docker-compose.yml mudou? Descrever
- [ ] Precisa de rebuild? Sim / Não

### Secrets / Credenciais

- [ ] Novos segredos necessários?
- [ ] Procedimento de rotação?

---

## Dependências

### Novas Dependências

| Lib | Versão | Por quê? | Alternativas |
|-----|--------|---------|--------------|
| lib-name | 1.2.3 | Razão | Foram consideradas X, Y, Z |

### Dependências Removidas

| Lib | Por quê? |
|-----|---------|
| old-lib | Já não é necessária após essa mudança |

---

## Performance

- [ ] Há implicações de performance?
  - Pior caso: O(n)? Queries N+1?
  - Mitigation: caching, índices, etc?

- [ ] Há impacto de memória / disco?

---

## Segurança

- [ ] Há novos vetores de ataque?
- [ ] Há exposição de dados sensíveis?
- [ ] Há autenticação/autorização adequada?
- [ ] Há validação de entrada?

---

## Testes

### O que será testado?

- [ ] Caso de sucesso
- [ ] Casos de erro
- [ ] Casos limítrofes
- [ ] Performance
- [ ] Segurança

### Estratégia de Teste

- Testes unitários onde?
- Testes de integração onde?
- Testes manuais necessários?

---

## Mudanças de Comportamento

### Compatibilidade

- [ ] Quebra compatibilidade? Sim / Não
- Se sim: qual é o plano de migração?

### Deprecação

- [ ] Algo será deprecated?
- Se sim: plano de comunicação e timeline de remoção?

---

## Rollback / Reverter

Se essa mudança tiver que ser desfeita rapidamente, o que fazer?

- Feature flag?
- Database rollback?
- Code revert?
- Data cleanup?

---

## Monitoramento & Alertas

- [ ] Novos logs estruturados?
- [ ] Novos contadores de métrica?
- [ ] Novos alertas necessários?

---

## Documentação Necessária

- [ ] README.md
- [ ] SECURITY.md
- [ ] API docs (Swagger/OpenAPI)
- [ ] DEVELOPMENT.md
- [ ] Guia de migração (se necessário)
- [ ] Change log / Release notes

---

## Abordagem de Implementação

Passo a passo de como implementar (para quando a tarefa começar):

1. Faça X
2. Faça Y
3. Teste Z
4. Comite e abra PR

---

## Questões em Aberto

- [ ] Pergunta 1?
- [ ] Pergunta 2?

(Estas devem ser respondidas antes de iniciar a implementação)
