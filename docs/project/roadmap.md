# 📈 Possíveis evoluções

Os limites de escopo desta versão — decisões deliberadas registradas no design da proposta original, não lacunas acidentais.

Estes pontos estão documentados como decisões deliberadas de escopo no `design.md` da proposta original (`openspec/changes/archive/2026-08-09-pocketledger-mvp/design.md`), não são lacunas acidentais:

- **Refresh token e logout/revogação de token.** A versão atual usa apenas um token de acesso de curta duração; um token válido não pode ser invalidado antes de expirar. Evoluir para um par access/refresh token com revogação server-side é o próximo passo natural caso o sistema precise de um fluxo de logout real.
- **Stack de observabilidade mais completa.** Hoje o ambiente local sobe apenas `app` + `db` + `jaeger`; métricas são expostas em `/metrics` mas não há um Prometheus nem um Grafana rodando localmente para consultá-las historicamente. Como as métricas já seguem o formato de exposição do Prometheus, um servidor Prometheus e dashboards no Grafana podem ser adicionados sem qualquer mudança na aplicação.
- **Sessão de banco síncrona sob handlers assíncronos.** O acesso ao banco usa `SQLAlchemy` síncrono dentro do threadpool do FastAPI — uma escolha deliberada para manter a simplicidade nesta escala. Migrar para SQLAlchemy assíncrono (`asyncpg`) só se justificaria se o sistema precisasse suportar uma carga de tráfego real e concorrente.
- **Segurança de segredos e deploy de produção.** O design documenta explicitamente que gerenciamento de segredos, TLS e topologia de deploy de produção estão fora do escopo desta versão, que roda apenas localmente via Docker Compose.
- **Rotação de chaves JWT.** A versão atual usa uma única chave estática para assinar todos os tokens; rotacionar a chave invalida todos os tokens outstanding. Para um serviço de produção com tokens de longa duração, implementar rotação gradual (múltiplas chaves ativas, rollover) seria necessário. Ver [SECURITY.md](../security/SECURITY.md) para detalhes.
- **Política de versionamento e deprecação de API.** Além do prefixo `/api/v1`, a aplicação não possui uma política formal de versionamento. A estratégia de migração da v1 para v2 fica para uma evolução futura. Ver [SECURITY.md](../security/SECURITY.md).

---

⬅️ [README](../../README.md) · 📚 [Índice da documentação](../README.md)
