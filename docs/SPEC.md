# SPEC — VerticalParts Infrastructure MCP

Versão: 2026-09-19
Status: resumo complementar; a SPEC canônica é `02_SPEC_MCP_INFRASTRUCTURE_VERTICALPARTS.md`

## 1. Objetivo

Permitir que uma LLM administre infraestrutura VerticalParts por intenção, usando tools semânticas, confirmação proporcional ao risco, auditoria, health e rollback.

O escopo cobre três planos:

- Hostinger VPS Control Plane;
- Hostinger Shared Hosting Control Plane;
- VPS Linux Operations Plane.

## 2. Estado mínimo esperado

O servidor homologado deve:
- rodar como `verticalparts-infra-mcp.service`;
- expor Streamable HTTP em loopback;
- ficar atrás de HTTPS + `X-API-Key`;
- expor o catálogo atual de **62 tools** (49 da homologação inicial + 13 da auditoria de segurança de 2026-09-19, sessão 2);
- ficar atrás de firewall de host ativo (`ufw`, `default deny incoming` desde 2026-09-19);
- carregar inventory/projects privados;
- manter break-glass desligado por padrão.

## 3. Requisitos funcionais

### FR-001 — Descoberta
Identificar ambiente real antes de qualquer mutação.

### FR-002 — Inventário
Usar `infra_inventory` para mapa operacional e reconciliar com DNS/runtime/health.

### FR-003 — VPS Hostinger
List/status/metrics/start/stop/restart, com confirmação para mutações.

### FR-004 — Shared Hosting Hostinger
Suportar semanticamente:
- orders/websites;
- file list/read seguro;
- Git auto-deploy status;
- SSL status;
- databases;
- cron jobs;
- Node.js settings/builds/build logs/runtime logs/env keys/vulnerabilities;
- Node.js restart com `CONFIRMO`.

### FR-005 — Fallback Hostinger
`hostinger_api_call` somente para endpoint oficial ainda sem wrapper. Tool semântica tem precedência.

### FR-006 — SSH seguro
Chave, known_hosts, usuário dedicado e path allowlist.

### FR-007 — systemd
Status/logs/start/stop/restart; mutações exigem confirmação.

### FR-008 — Docker
List/logs/restart/Compose. Docker não é default. VPClick é o caso de produção Docker conhecido.

### FR-009 — Deploy externo
Projeto com `deploy.mode=external` deve ser recusado por `deploy_project`. VPClick publica via GitHub Actions.

### FR-010 — Git
Status/log/fetch/pull ff-only; working tree suja bloqueia pull/deploy.

### FR-011 — Env e arquivos
Nunca retornar valores secretos. Escritas criam backup quando aplicável.

### FR-012 — Nginx
`nginx_test` antes de reload.

### FR-013 — APT
Check sem confirmação; upgrade com `CONFIRMO`; reboot separado.

### FR-014 — Auditoria
Toda mutação rastreável sem segredo.

### FR-015 — Confirmação
- READ: sem confirmação;
- CRITICAL: `CONFIRMO`;
- DESTRUCTIVE: `CONFIRMO_DESTRUTIVO`;
- BREAK_GLASS: flag + razão + `BREAK_GLASS`.

### FR-016 — Timeout
Verificar estado antes de retry.

### FR-017 — Não inventar
Não inventar IDs, paths, endpoints, branches, serviços, bancos, credenciais ou associações.

### FR-018 — Classificação Hostinger
`website_type=other` não deve ser convertido automaticamente em “PHP”.
Website listado na Hostinger não prova destino de produção.

### FR-019 — VPClick legado
O registro Shared Hosting do VPClick deve ser tratado como legado vivo; não deletar/desativar sem análise explícita.

### FR-020 — Firewall (adicionado 2026-09-19)
Status sem confirmação; allow/delete rule com `CONFIRMO`. Achado real: host ficou meses com firewall totalmente inativo sem que isso fosse detectado — auditar não é opcional.

### FR-021 — Docker network/volume (adicionado 2026-09-19)
List sem confirmação; remove com `CONFIRMO_DESTRUTIVO` e recusa automática se houver container anexado/referenciando. `docker_compose_action(down)` é destrutivo, diferente das demais ações do mesmo tool.

### FR-022 — Observabilidade de host (adicionado 2026-09-19)
Portas em escuta, processos PM2, cron.d — leitura sem confirmação. PM2 nunca deve retornar variáveis de ambiente do processo (`pm2_env.env`).

### FR-023 — Remoção segura de arquivo (adicionado 2026-09-19)
`file_delete`: backup automático, caminho resolvido (`realpath -m`) e revalidado contra raízes permitidas antes de apagar, `CONFIRMO_DESTRUTIVO`.

### FR-024 — Canonicalização de path (adicionado 2026-09-19, achado de review automatizado)
Toda validação de caminho (`assert_allowed_path`) deve rejeitar segmentos `..`, não só checar prefixo textual. Checagem por prefixo sozinha é insuficiente porque não reflete como o shell remoto resolve o caminho.

## 4. Requisitos não funcionais

- segurança;
- auditabilidade;
- reversibilidade;
- observabilidade;
- compatibilidade MCP;
- documentação reconciliada;
- resiliência futura com control plane externo.

## 5. Critério de aceite

Após upgrade:
1. service active;
2. initialize;
3. tools/list;
4. `infra_inventory`;
5. uma tool de leitura real;
6. auth pública;
7. nenhum segredo exposto.
