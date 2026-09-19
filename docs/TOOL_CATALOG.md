# Catálogo de Tools

Versão observada: 2026-09-19
Total homologado em `tools/list`: **49 tools**

## Inventário

| Tool | Risco | Função |
|---|---|---|
| `infra_status` | leitura | uptime, memória, disco e load |
| `infra_list_projects` | leitura | projetos registrados sem segredos |
| `infra_inventory` | leitura | topologia operacional autoritativa |

## Hostinger

| Tool | Risco | Função |
|---|---|---|
| `hostinger_list_vps` | leitura | lista VPS |
| `hostinger_list_websites` | leitura | lista websites de hosting |
| `hostinger_list_orders` | leitura | lista planos/ordens de hosting |
| `hostinger_vps_status` | leitura | estado/detalhes da VPS |
| `hostinger_vps_metrics` | leitura | métricas VPS |
| `hostinger_vps_start` | crítico | liga VPS |
| `hostinger_vps_stop` | crítico | desliga VPS |
| `hostinger_vps_restart` | crítico | reinicia VPS |
| `hostinger_website_files` | leitura | lista arquivos do document root |
| `hostinger_website_file_read` | leitura | lê arquivo texto permitido com guardrails |
| `hostinger_git_autodeploy_status` | leitura | repo/branch/estado do auto-deploy |
| `hostinger_ssl_status` | leitura | status SSL/HTTPS redirect |
| `hostinger_list_databases` | leitura | lista bancos sem password |
| `hostinger_list_cron_jobs` | leitura | lista cron jobs |
| `hostinger_nodejs_settings` | leitura | Node/build/output/entry settings |
| `hostinger_nodejs_builds` | leitura | histórico de builds |
| `hostinger_nodejs_build_logs` | leitura | log de build |
| `hostinger_nodejs_runtime_logs` | leitura | logs de runtime |
| `hostinger_nodejs_env_keys` | leitura | nomes de env, nunca valores |
| `hostinger_nodejs_vulnerabilities` | leitura | vulnerabilidades detectadas pela Hostinger |
| `hostinger_nodejs_restart` | crítico | restart do processo Node.js sem rebuild |
| `hostinger_api_call` | variável | fallback para endpoint oficial sem wrapper |

## systemd

| Tool | Risco | Função |
|---|---|---|
| `service_status` | leitura | status systemd |
| `service_logs` | leitura | journal |
| `service_start` | crítico | start |
| `service_stop` | crítico | stop |
| `service_restart` | crítico | restart |

## Docker

| Tool | Risco | Função |
|---|---|---|
| `docker_ps` | leitura | lista containers via sudo docker |
| `docker_logs` | leitura | logs |
| `docker_restart` | crítico | restart |
| `docker_compose_action` | leitura/crítico | ps/logs ou pull/build/up/restart |

## Git

| Tool | Risco | Função |
|---|---|---|
| `git_status` | leitura | branch/status/SHA |
| `git_log` | leitura | histórico |
| `git_fetch` | operacional | atualiza refs |
| `git_pull` | crítico | ff-only com working tree limpa |

## Arquivos e env VPS

| Tool | Risco | Função |
|---|---|---|
| `file_read` | leitura | arquivo permitido, exceto env |
| `file_write` | crítico | grava com backup |
| `env_list_keys` | leitura | nomes e configured |
| `env_set` | crítico | define valor sem retorná-lo |
| `env_remove` | crítico | remove variável |

## Nginx

| Tool | Risco | Função |
|---|---|---|
| `nginx_test` | leitura | valida config |
| `nginx_reload` | crítico | test + reload |

## Sistema

| Tool | Risco | Função |
|---|---|---|
| `apt_check_updates` | leitura | consulta updates |
| `apt_upgrade` | crítico | instala updates sem reboot |

## Deploy e contingência

| Tool | Risco | Função |
|---|---|---|
| `deploy_project` | crítico | deploy declarativo + health/rollback; recusa deploy externo |
| `infra_exec_command` | break-glass | shell arbitrário, desabilitado por padrão |

## Regras do catálogo

- ferramenta listada não significa que toda combinação de argumentos foi homologada;
- `hostinger_ssl_status` foi validada end-to-end via MCP;
- vários endpoints de Shared Hosting foram validados diretamente durante a descoberta antes dos wrappers;
- `hostinger_nodejs_restart` não foi acionada em produção na auditoria;
- prefira tool semântica a `hostinger_api_call`;
- use `infra_exec_command` somente como último recurso.

## Próxima expansão

Prioridades úteis:
- DNS semântico;
- backups/snapshots;
- firewall;
- health orchestration;
- drift detection;
- mutations Shared Hosting específicas com guardrails;
- redução de sudo;
- control plane externo à VPS.
