# SDD — VerticalParts Infrastructure MCP

Versão: 2026-09-19
Status: resumo complementar; o SDD canônico é `04_SDD_MCP_INFRASTRUCTURE_VERTICALPARTS.md`

## 1. Arquitetura atual

```text
Claude / cliente MCP
        |
        | HTTPS + X-API-Key
        v
Nginx / gateway
        |
        v
VerticalParts Infrastructure MCP
        |
        +-----------------------------+
        |                             |
        v                             v
Hostinger API                  SSH Operations Plane
        |                             |
        +--> VPS lifecycle            +--> systemd
        +--> Websites/orders          +--> Docker
        +--> Files                    +--> Git
        +--> SSL                      +--> files/env
        +--> DB / cron                +--> Nginx
        +--> Node builds/logs         +--> APT
        +--> Git auto-deploy          +--> deploy
```

## 2. Local de execução

Estado atual:
- MCP e VPS alvo estão co-localizados;
- isso foi homologado e funciona;
- é um ponto único de falha.

Target futuro:
- control plane independente da VPS alvo.

## 3. Plano Hostinger Shared Hosting

O Shared Hosting é operado semanticamente por API sempre que possível.

Tools cobrem:
- inventory de websites/orders;
- files e safe read;
- Git auto-deploy status;
- SSL;
- DB;
- cron;
- Node.js settings/builds/build logs/runtime logs/env keys/vulnerabilities;
- restart Node.js com confirmação.

Isso reduz a necessidade de SSH em hosting compartilhado.

## 4. Plano VPS

O plano SSH usa:
- chave dedicada;
- known_hosts;
- usuário `infra-mcp`;
- allowed paths (rejeita `..` desde 2026-09-19 — achado de review automatizado, ver `docs/SECURITY.md` §13);
- sudo para operações privilegiadas.

Docker usa `sudo docker` e `sudo docker compose`. O erro antigo de socket Docker foi corrigido e não é estado normal.

Limitação conhecida desde 2026-09-19: as tools estruturadas que escrevem via SSH (`file_write`, `env_set`, `env_remove`, `git_pull`, `git_fetch`) rodam como `infra-mcp` **sem sudo**, então falham em qualquer caminho `root:root` — inclusive o próprio `/opt/verticalparts-infrastructure-mcp`. Auto-atualização do MCP exige o fluxo break-glass documentado em `05_RUNBOOK` PARTE G.

## 5. VPClick

`vpclick.vpsistema.com`:
- produção: VPS;
- runtime: Docker Compose;
- container: `vpclick-vpclick-1`;
- deploy: GitHub Actions;
- registro Hostinger Node.js: legado ainda ativo.

O MCP pode inspecionar/reiniciar runtime autorizado, mas `deploy_project` deve recusar substituir o pipeline externo.

## 6. Fluxo de diagnóstico

```text
pedido
 -> identificar ambiente real
 -> inventory
 -> estado vivo
 -> classificar falha
 -> menor intervenção
 -> confirmação se necessária
 -> executar
 -> validar
 -> reconciliar docs/inventory
```

## 7. Fluxo de deploy

```text
resolve project
 -> deploy.mode?
 -> external => não publicar pelo deploy_project
 -> managed => git status
 -> dirty? abort
 -> old SHA
 -> CONFIRMO
 -> ff-only/build/restart
 -> health
 -> rollback se necessário
```

## 8. Segurança

Camadas:
1. HTTPS;
2. X-API-Key;
3. firewall de host (`ufw`, `default deny incoming` desde 2026-09-19 — estava totalmente inativo antes);
4. tool semântica;
5. classificação de risco;
6. confirmação;
7. path validation (rejeita `..` desde 2026-09-19);
8. SSH key/known_hosts;
9. sudo;
10. audit;
11. rollback.

## 9. Homologação

Em 2026-09-19 (sessão 1):
- service ativo;
- 49 tools listadas;
- Hostinger Shared Hosting descoberto;
- SSL semantic tool testada end-to-end;
- Docker read/Compose homologados;
- docs reconciliados.

Em 2026-09-19 (sessão 2, auditoria de segurança — ver `docs/HOMOLOGATION.md` e `docs/SECURITY.md` para detalhes):
- firewall corrigido (estava inativo);
- Tor/WARP desativados (Tor com evidência real de abuso como proxy aberto);
- `hermes-agent-god7` removido;
- `vpprd-mcp` autenticado no gateway;
- 62 tools listadas e validadas via protocolo MCP real;
- 4 achados de review automatizado (path traversal, vazamento de `pm2_env`, backup quebrado, cron.d incompleto) corrigidos e redeployados.

Não confundir “tool listada” com “todas as combinações de argumentos foram testadas”.
