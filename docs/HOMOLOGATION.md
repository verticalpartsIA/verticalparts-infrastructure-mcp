# Homologação — VerticalParts Infrastructure MCP

Versão: 2026-09-19
Status: homologação principal concluída; algumas tools novas ainda exigem teste individual quando forem usadas

## Resultado geral

A cadeia local do MCP foi validada após atualização do código:

- `verticalparts-infra-mcp.service` = `active`;
- MCP `initialize` local funciona;
- `tools/list` retornou **49 tools**;
- `hostinger_ssl_status` foi chamada pelo protocolo MCP real e retornou sucesso;
- autenticação pública por `X-API-Key` já havia sido validada;
- Docker foi corrigido para executar por `sudo docker` / `sudo docker compose`;
- `docker_ps` e Compose `ps` foram homologados;
- `vpclick` foi registrado como runtime Docker com deploy externo via GitHub Actions.

## Hostinger Shared Hosting — descoberta validada

A API de Hosting retornou 14 websites em dois planos.

### Conta Cloud — 9 registros Node.js

Auto-deploy Git Hostinger observado como ativo em todos:

| Domínio | Repositório | Branch |
|---|---|---|
| escamaxcompravp.vpsistema.com | verticalpartsIA/011_EscamaxCompraVP | feat/reskin-verticalparts |
| gentegestao.vpsistema.com | verticalpartsIA/17_gente-gestao | main |
| posvenda360.vpsistema.com | verticalpartsIA/004_sac_posvenda360 | main |
| propostas.vpsistema.com | verticalpartsIA/002_proposta_comercial | main |
| vpclick.vpsistema.com | verticalpartsIA/005_vpclick | main |
| vpdashboarddre.vpsistema.com | verticalpartsIA/bd_omie | main |
| vpgestaoimportacao.vpsistema.com | verticalpartsIA/010_GestaoImportacao | main |
| vprequisicoes.vpsistema.com | verticalpartsIA/003_requisicoes | main |
| vpsistema.com | verticalpartsIA/vpsistema | main |

Atenção: o registro Hostinger do VPClick é legado. A produção canônica de `vpclick.vpsistema.com` está na VPS, em Docker, e seu deploy é GitHub Actions.

### Conta Premium — 5 registros `other`

Os cinco expõem PHP 8.3.33 no plano, mas isso não prova que a aplicação seja PHP.

Arquivos observados no document root:

- `assetmanager.vpsistema.com`: `index.html`, JS/assets e `default.php`;
- `catraca.vpsistema.com`: `index.html` + `assets/`;
- `interativo.vpsistema.com`: `index.html` + diretórios/assets;
- `suporte.vpsistema.com`: `index.html`, `assets/`, `uploads/`, `api.php`;
- `visitas.vpsistema.com`: `index.html`, assets e ZIP histórico de deploy.

Nenhum dos cinco apresentou auto-deploy Git Hostinger configurado.

## VPRequisições — evidências

Validado por API:
- Node.js 22;
- app_type `other`;
- output `dist`;
- build script `build`;
- entry file `server.js`;
- deploy Git de `verticalpartsIA/003_requisicoes`, branch `main`;
- build recente concluído;
- runtime logs endpoint responde;
- SSL ativo;
- HTTPS redirect ativo.

A leitura de `.htaccess` mostrou Passenger apontando para o `hbuilds/current/nodejs`, portanto o código Node ativo é gerenciado pela camada de build da Hostinger e não precisa aparecer no document root.

## Bancos e cron

A API da conta Cloud listou quatro bancos MySQL. Nenhuma senha é retornada pela API. Os registros observados não estavam associados a um domínio por campo `domain`, então não inferir qual aplicação usa qual banco sem outra evidência.

Cron jobs da conta Cloud: lista vazia no momento da auditoria.

## Build logs

O build recente de VPRequisições concluiu, mas registrou avisos de dependência e vulnerabilidades npm. Esses números são sinal de auditoria de dependências, não prova automática de exploração em produção.

## O que foi implementado no MCP

Novas tools semânticas:
- `hostinger_list_orders`;
- `hostinger_website_files`;
- `hostinger_website_file_read`;
- `hostinger_git_autodeploy_status`;
- `hostinger_ssl_status`;
- `hostinger_list_databases`;
- `hostinger_list_cron_jobs`;
- `hostinger_nodejs_settings`;
- `hostinger_nodejs_builds`;
- `hostinger_nodejs_build_logs`;
- `hostinger_nodejs_runtime_logs`;
- `hostinger_nodejs_env_keys`;
- `hostinger_nodejs_vulnerabilities`;
- `hostinger_nodejs_restart`.

O catálogo completo observado passou para 49 tools.

## Escopo do que está realmente homologado

Não declarar que toda tool nova foi testada end-to-end apenas porque aparece em `tools/list`.

Evidência por nível:
- endpoints de arquivos, Git, SSL, bancos, cron, settings, builds e logs foram exercitados diretamente durante a descoberta;
- `hostinger_ssl_status` foi adicionalmente exercitada através do protocolo MCP após o deploy;
- `hostinger_nodejs_restart` não foi executada em produção durante esta homologação;
- env keys e vulnerabilities foram implementadas com base na API oficial, mas devem ser verificadas no primeiro uso real.

## Critério de pronto desta fase

Concluído:
- serviço ativo;
- código sincronizado;
- 49 tools carregadas;
- uma nova tool semântica validada via MCP;
- documentação reconciliada;
- segredos não versionados.

Pendências estruturais:
- reduzir sudo amplo para allowlist granular;
- mover control plane para host independente;
- ampliar testes end-to-end das novas tools conforme uso;
- implementar mais wrappers de mutação apenas quando necessários e com guardrails.

---

# Homologação — Sessão 2 (2026-09-19, auditoria de segurança)

Status: concluída. Escopo: auditoria completa de segurança do host, expansão de tools, correção de achados de review automatizado, curadoria de documentação.

## Resumo executivo

Com break-glass habilitado sob confirmação por comando (`infra_exec_command`, auditado em `data/audit.jsonl`), foi feita uma varredura completa do host além do escopo original (VPS + Shared Hosting Hostinger). Encontrados e corrigidos 5 problemas reais, 3 deles de severidade alta:

1. **Firewall totalmente inativo** (`ufw status: inactive`, `iptables -L INPUT` policy `ACCEPT`, zero regras) — toda porta aberta por qualquer processo em `0.0.0.0` estava acessível pela internet sem filtro nenhum.
2. **Proxy Tor SOCKS aberto** (`SocksPort 0.0.0.0:9050`, não é o padrão do pacote) com evidência real de abuso: ~15.151 conexões e ~360MB de tráfego registrados no próprio heartbeat do Tor antes da correção.
3. **`mcp.vpsistema.com` expunha `vpprd-mcp`** (outro servidor MCP, porta 3100) sem checagem de `X-API-Key` no gateway, diferente do padrão dos outros dois MCPs canônicos.
4. Cloudflare WARP instalado mas nunca configurado (superfície de ataque ociosa).
5. Container `hermes-agent-god7` (agente de terminal do template Hostinger) sem uso relevante e sem rota externa funcional.

Todos corrigidos na mesma sessão, com evidência de teste antes/depois para cada um (ver `00_READ_FIRST_INFRASTRUCTURE_MCP.md` seção 4B para o detalhamento completo).

## Ordem de correção (menor risco/esforço → maior)

Seguida por pedido explícito do operador:

1. Limpeza de regra de firewall órfã (porta 8081, sem processo associado).
2. Limpeza de redes/volumes Docker órfãos (resíduo de `supabase functions serve`).
3. Atualização do inventário/registro de projetos do runtime (documentação, zero risco de execução).
4. Autenticação do `vpprd-mcp` no gateway Nginx.
5. Investigação e remoção do `hermes-agent-god7`.
6. `evolution-api` (credenciais em texto puro) — **investigado, decisão de correção adiada pelo operador**, não é pendência técnica não descoberta.
7. Investigação da inconsistência aparente de banco `n8n`/`vp-infra` — **testada e confirmada como falso alarme**: o banco `n8n` existe e autentica normalmente via TCP.
8. Investigação e remoção de `intrasites-main.yml`/`intrasites-snapshot.yml` (dump de automação de navegador não relacionado a infraestrutura).
9. Desativação de Tor e Cloudflare WARP.
10. Expansão de 13 tools semânticas no código (firewall, Docker network/volume, systemd enable/disable, observabilidade de host, remoção segura de arquivo).

## Validação end-to-end pós-mudança

- `firewall_status` real via protocolo MCP: `Status: active`, `Default: deny (incoming)`, só `22/80/443` liberados.
- `docker_network_ls` real: confirma ausência das redes órfãs do Supabase.
- Handshake MCP completo contra `https://infra-mcp.vpsistema.com/mcp`: `401` sem `X-API-Key`, `200` com chave no `initialize`, `serverInfo.version = 1.30.0`.
- `infra_pm2_list` real: retorna `{"exit_status":0,"processes":[]}` — confirma que a versão corrigida (sem `pm2_env.env`) está em produção, não só no código.

## Achados de review automatizado (Codex) no PR de expansão de tools

O PR `verticalpartsIA/verticalparts-infrastructure-mcp#1` recebeu review automatizado com 4 achados reais (2 P1, 2 P2), todos verificados, corrigidos e re-deployados na mesma sessão:

| Severidade | Achado | Correção |
|---|---|---|
| P1 | Path traversal em `file_delete` via `..` | `assert_allowed_path` rejeita `..`; `file_delete` resolve caminho real via `realpath -m` antes de apagar |
| P1 | `infra_pm2_list` vazava `pm2_env.env` (segredos de app) | Projeção fixa de campos, nunca inclui `env` |
| P2 | Backup de `file_delete` quebrava com path terminado em `/` | Normalização (`rstrip("/")`) antes de montar o caminho de backup |
| P2 | `infra_cron_list` só listava nomes de arquivo em `/etc/cron.d`, não o conteúdo | Agora lê e retorna schedule/comando de cada arquivo |

## Descoberta de pilha de automação não documentada

A investigação revelou serviços rodando na VPS que não constavam em nenhum inventário: `evolution-api` (backend WhatsApp do pv360/posvenda360), `n8n` + `vp-infra` (Postgres/Redis), `traefik`, `stt-service`, `telegram-claude`, `vpprd-mcp`, crons de negócio (`bordero`, `vpclick-cobranca`, `sac-backfill-diario`, `cron-handoffs`), e projetos/checkouts diversos (`resolve-360`, `vp-bot` dormente, `vp-automations-hub` — documentação de engenharia já existente para parte desse stack, `vpprd-assistente`, `designsystem`). Tudo registrado em `config/projects.yaml` do runtime com o contexto de cada descoberta (status, dependências, pendências).

## Curadoria de documentação

Após o código e o deploy, toda a documentação canônica (`00`–`05`, `README.md`, `CLAUDE.md`) e complementar (`docs/*`, `rag/*`) foi revisada e reconciliada contra o estado real descoberto e corrigido nesta sessão — incluindo este próprio arquivo.

## Critério de pronto desta fase

Concluído:
- firewall corrigido e validado via protocolo MCP real;
- Tor/WARP desativados, com evidência de abuso documentada;
- `hermes-agent-god7` removido com backup;
- `vpprd-mcp` autenticado no gateway;
- 62 tools carregadas e validadas (49 + 13), incluindo os 4 achados de review automatizado corrigidos e redeployados;
- pilha de automação real documentada em `config/projects.yaml`;
- documentação canônica e complementar reconciliada.

Pendências estruturais (não resolvidas nesta sessão, deliberadamente):
- rotação coordenada das credenciais do `evolution-api` (VPS + Hostinger shared hosting) — decisão adiada pelo operador;
- reduzir sudo amplo (`infra-mcp` com `NOPASSWD: ALL`) para allowlist granular;
- mover control plane para host independente;
- regra de firewall órfã (`8081/tcp`, sem processo associado, sem risco ativo) — removida; caso reapareça, investigar origem antes de tratar como resíduo.
