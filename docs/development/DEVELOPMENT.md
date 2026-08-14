# Guia de Desenvolvimento — PocketLedger

Este documento descreve o fluxo de desenvolvimento padronizado para o PocketLedger, garantindo que todas as mudanças sejam bem documentadas e rastreáveis.

## Visão Geral

Todo trabalho no PocketLedger segue o modelo **Spec-Driven Development (SDD)** usando o **OpenSpec**. Cada mudança — seja feature, bugfix, security patch, ou refactoring — é:

1. **Proposta** em um arquivo estruturado
2. **Planejada** com design e tarefas
3. **Implementada** em uma feature branch
4. **Testada** localmente
5. **Revisada** via Pull Request
6. **Arquivada** como histórico

---

## Estrutura de Mudanças

Todas as mudanças vivem em `openspec/changes/`:

```
openspec/changes/
├── active/              # Mudanças em progresso
│   └── YYYY-MM-DD-{tipo}-{slug}/
│       ├── proposal.md  # Motivação, contexto, requisitos
│       ├── design.md    # Decisões técnicas, trade-offs
│       ├── tasks.md     # Plano de trabalho (checklist)
│       └── specs/       # Especificações (se aplicável)
│
└── archive/             # Mudanças finalizadas
    └── YYYY-MM-DD-{tipo}-{slug}/
        └── [mesmos arquivos]
```

### Tipos de Mudança

Use um destes prefixos no diretório:

- **`feature`** — Nova funcionalidade (ex: `2026-08-14-feature-audit-logging`)
- **`bugfix`** — Correção de bug (ex: `2026-08-14-bugfix-rate-limit-persistence`)
- **`security`** — Patch de segurança (ex: `2026-08-14-security-jwt-rotation`)
- **`refactor`** — Refatoração técnica (ex: `2026-08-14-refactor-error-handling`)
- **`docs`** — Melhorias em documentação (ex: `2026-08-14-docs-api-guide`)
- **`perf`** — Otimização de performance (ex: `2026-08-14-perf-query-optimization`)

---

## Fluxo de Trabalho

### 1. Criar uma Mudança

```bash
# Crie o diretório da mudança (data + tipo + slug descritivo)
mkdir -p openspec/changes/active/2026-08-14-feature-audit-logging

# Crie os arquivos iniciais
touch openspec/changes/active/2026-08-14-feature-audit-logging/{proposal,design,tasks}.md

# Crie a branch correspondente
git checkout -b feature/audit-logging
```

### 2. Escrever a Proposta (`proposal.md`)

Template:

```markdown
# [Título da Mudança]

## Motivação

Por que essa mudança é necessária? Qual problema resolve?

## Contexto

Informação de fundo, requisitos do usuário, decisões anteriores que levam a isso.

## Escopo

O que **está incluído** e o que **está explicitamente fora de escopo**.

## Benefícios

Quais são os benefícios? Métricas de sucesso?

## Riscos / Trade-offs

Que compromissos estamos fazendo? Que riscos existem?

## Referências

Links para issues, discussões, especificações relacionadas.
```

### 3. Escrever o Design (`design.md`)

Template:

```markdown
# Design — [Título da Mudança]

## Decisões Arquiteturais

### 1. [Decisão]

**Escolha:** Opção A vs. Opção B → escolhemos **Opção A**

**Rationale:** Por quê? Que trade-offs? Que alternativas foram consideradas?

**Impacto:** Quais componentes são afetados?

## Mudanças de Banco de Dados

- [ ] Migration necessária? (descrever)
- [ ] Retrocompatibilidade mantida?

## Mudanças de API

Se houver mudanças em endpoints, schemas, versioning:

```yaml
POST /api/v1/new-endpoint
  - Request: {...}
  - Response: {...}
  - Status codes: 200, 400, 401
```

## Mudanças de Infraestrutura

Docker, env vars, configuração, secrets, etc.

## Dependências Novas

Alguma lib nova será adicionada? Por quê?

## Testes

Como isso será testado? Novos testes necessários?

## Deprecação / Migração

Se mudanças quebram compatibilidade, qual é o plano de migração?

## Abordagem Implementação

Passo a passo de como implementar.
```

### 4. Escrever o Plano (`tasks.md`)

Template:

```markdown
# Plano de Tarefas — [Título da Mudança]

## Resumo

1 ou 2 linhas do que será feito.

## Tarefas

- [ ] **Tarefa 1** — Descrição breve
- [ ] **Tarefa 2** — Descrição breve
- [ ] **Testes** — Novos testes para Tarefa 1 e 2
- [ ] **Documentação** — README, SECURITY.md, etc.
- [ ] **Code review interno** — Validar escolhas
- [ ] **Merge** — Integrar na main

## Estimativa

Quanto tempo leva? (para planejamento)

## Bloqueadores

Existe algo que impede iniciar?

## Critério de Aceitação

Como saber que está pronto?
```

### 5. Implementar em Feature Branch

```bash
# Certifique-se de estar na branch correta
git checkout feature/audit-logging

# Faça as mudanças, commit frequentemente
git add .
git commit -m "Add audit logging middleware

Co-Authored-By: Claude <noreply@anthropic.com>"

# Atualize o tasks.md conforme completa as tarefas
# ex: - [x] **Middleware implementado**
```

### 6. Testar Localmente

```bash
# Execute testes
docker compose run --rm app-test pytest -v

# Teste manual
docker compose up -d
curl http://localhost:8000/api/v1/...

# Se tudo passar, comite a mudança
git add openspec/changes/active/2026-08-14-feature-audit-logging/
git commit -m "Update tasks: mark audit logging middleware as done"
```

### 7. Solicitar Revisão (PRi)

```bash
# Push a feature branch
git push origin feature/audit-logging

# Crie um rascunho de PR (NÃO o mescle ainda)
gh pr create --draft \
  --title "Feature: Audit logging" \
  --body "$(cat openspec/changes/active/2026-08-14-feature-audit-logging/proposal.md)"
```

**Importante:** Deixe o PR em **rascunho** até você (ou o time) revisarem e aprovarem.

### 8. Revisar & Aprovar

Revise:
- [ ] Código segue as convenções do projeto?
- [ ] Testes cobrem os cenários?
- [ ] Documentação está atualizada?
- [ ] Tasks.md está 100% completo?
- [ ] Não há dependências bloqueadas?

Se tudo estiver bem:

```bash
# Converta de rascunho para "ready for review"
gh pr ready {PR_NUMBER}

# Ou apenas comente "APPROVED" no PR
```

### 9. Mesclar na Main

```bash
# Quando aprovado, mescle o PR
gh pr merge {PR_NUMBER} --squash

# Delete a feature branch
git branch -D feature/audit-logging
git push origin --delete feature/audit-logging
```

### 10. Arquivar a Mudança

Após mesclar:

```bash
# Mova de active para archive
mv openspec/changes/active/2026-08-14-feature-audit-logging \
   openspec/changes/archive/2026-08-14-feature-audit-logging

# Commit o arquivo
git add openspec/changes/archive/
git commit -m "Archive change: feature-audit-logging"

git push origin main
```

---

## Convenções de Commit

Cada commit deve ter um prefixo que indica o tipo:

```
feat:     Nova feature
fix:      Correção de bug
security: Patch de segurança
docs:     Documentação
test:     Testes
refactor: Refatoração
perf:     Performance
ci:       CI/CD
chore:    Tarefas administrativas (deps, etc)
```

Exemplo:

```
feat: add audit logging middleware

- Track all authentication events with client IP
- Log to structured JSON format
- Include in trace correlation

Fixes #42
Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## Hooks Git Automáticos

Para automatizar partes do fluxo, coloque scripts em `.claude/hooks/`:

### `.claude/hooks/pre-commit`

Valida que `tasks.md` está atualizado antes de commitar.

### `.claude/hooks/post-merge`

Move mudança para archive se todas as tarefas estão marcadas.

**Nota:** Esses hooks são opcionais; você controla o fluxo manualmente.

---

## Entendimento para LLMs (e Futuros Desenvolvedores)

Cada mudança em `openspec/changes/` tem **tudo** necessário para um LLM (ou pessoa nova) entender:

1. **Por quê** (proposal.md) — Contexto e motivação
2. **Como** (design.md) — Decisões arquiteturais e trade-offs
3. **O quê** (tasks.md) — Exatamente o que foi feito
4. **Código** (commits na branch) — Implementação real

Isso significa que futuros LLMs (ou desenvolvedores) podem:
- Ler `openspec/changes/archive/` para histórico completo
- Entender por que decisões foram tomadas
- Aprender as convenções do projeto
- Reproduzir mudanças similares

---

## Exemplo Real: Security Patch Recente

```
openspec/changes/archive/2026-08-14-security-jwt-hardening/
├── proposal.md
│   └── "Endereçar 14 findings de auditoria de segurança"
├── design.md
│   └── "Startup guard, rate limiting, CORS, security headers..."
├── tasks.md
│   └── "✓ Todos os tópicos marcados como completos"
└── specs/
    └── "Se houver specs de segurança"
```

Quando alguém quiser entender por que o JWT tem um startup guard, ele lê:
- `proposal.md` → "Por que: placeholder secrets eram perigosos em produção"
- `design.md` → "Como: fail-closed RuntimeError fora de dev/test"
- Commits na branch → "O código exato"
- `SECURITY.md` → "Como usar em produção"

---

## Checklist para Qualidade

Antes de marcar uma mudança como "pronta", verifique:

- [ ] `proposal.md` está claro e completo?
- [ ] `design.md` explica todas as decisões?
- [ ] `tasks.md` tem todos os itens marcados como ✓?
- [ ] Código passou em `pytest`?
- [ ] Documentação (README, SECURITY, etc.) foi atualizada?
- [ ] Não há TODO/FIXME comentários não intencionais?
- [ ] Logs e errors são úteis e seguem o padrão?
- [ ] Security review foi feito (mesmo que internamente)?

---

## Ferramentas Recomendadas

Para tornar isso mais fluido, considere usar:

1. **Claude Code** — Uso de `/plan` para designs
2. **OpenSpec CLI** — `openspec new change`, `openspec status`, etc.
3. **GitHub CLI** — `gh pr create`, `gh pr merge`, etc.
4. **Git Hooks** — `.git/hooks/pre-commit`, etc. para automação

---

## FAQ

### P: E se for uma mudança muito pequena (typo, pequeno bugfix)?

**R:** Mesmo typos devem ter um `proposal.md` mínimo (1-2 linhas) para rastreabilidade. A documentação é barata; perder contexto é caro.

### P: Posso fazer múltiplas features ao mesmo tempo?

**R:** Sim, crie branches separadas para cada mudança. Mantenha-as independentes.

### P: E se a proposta mudar durante a implementação?

**R:** Atualize `proposal.md`, `design.md`, ou `tasks.md` conforme necessário. Commit essas mudanças na feature branch. Isso é normal.

### P: Como evitar merge conflicts em `openspec/changes/`?

**R:** Cada feature tem seu próprio diretório com data única (YYYY-MM-DD), então não há conflitos. Diferentes features podem ser desenvolvidas em paralelo.

### P: Posso descartar uma mudança sem arquivar?

**R:** Sim. Simplesmente delete o diretório em `openspec/changes/active/` e a branch. Nenhuma mudança foi mesclada, então não há histórico para manter.

---

## Resumo

| Etapa | Comando | Saída |
|-------|---------|-------|
| **Criar** | `mkdir openspec/changes/active/DATE-TYPE-slug && git checkout -b type/slug` | Branch pronta |
| **Planejar** | Escrever `proposal.md`, `design.md`, `tasks.md` | Design validado |
| **Implementar** | Fazer commits, atualizar `tasks.md` | Branch com código |
| **Testar** | `pytest`, testes manuais | Código validado |
| **Revisar** | `gh pr create --draft` | PR em rascunho |
| **Aprovar** | `gh pr ready` e revisão completa | PR aprovado |
| **Mesclar** | `gh pr merge --squash` | Main atualizada |
| **Arquivar** | `mv active/ archive/` | Histórico preservado |
