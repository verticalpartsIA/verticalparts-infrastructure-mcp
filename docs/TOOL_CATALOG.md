# Catálogo de Tools

## Implementadas na v0.1

| Tool | Risco | Função |
|---|---|---|
| `infra_status` | leitura | uptime, memória, disco, load |
| `infra_list_projects` | leitura | projetos registrados |
| `hostinger_list_vps` | leitura | lista VPS da conta |
| `hostinger_vps_status` | leitura | estado/detalhes da VPS |
| `hostinger_vps_metrics` | leitura | métricas Hostinger |
| `hostinger_vps_start` | crítico | liga VPS |
| `hostinger_vps_stop` | crítico | desliga VPS |
| `hostinger_vps_restart` | crítico | reinicia VPS |
| `hostinger_api_call` | variável | fallback oficial Hostinger |
| `service_status` | leitura | status systemd |
| `service_logs` | leitura | journalctl |
| `service_start` | crítico | start systemd |
| `service_stop` | crítico | stop systemd |
| `service_restart` | crítico | restart systemd |
| `docker_ps` | leitura | lista containers |
| `docker_logs` | leitura | logs container |
| `docker_restart` | crítico | restart container |
| `docker_compose_action` | leitura/crítico | ps/logs/pull/build/up/restart |
| `git_status` | leitura | estado do repo |
| `git_log` | leitura | histórico |
| `git_fetch` | operacional | atualiza refs |
| `git_pull` | crítico | ff-only com working tree limpa |
| `file_read` | leitura | arquivo permitido, exceto .env |
| `file_write` | crítico | grava com backup |
| `env_list_keys` | leitura | nomes e configured=true/false |
| `env_set` | crítico | define variável com backup e redaction |
| `env_remove` | crítico | remove variável com backup |
| `nginx_test` | leitura | valida config |
| `nginx_reload` | crítico | test + reload |
| `apt_check_updates` | leitura | lista updates |
| `apt_upgrade` | crítico | instala updates, sem reboot automático |
| `deploy_project` | crítico | deploy + health + rollback |
| `infra_exec_command` | break-glass | shell arbitrário auditado |

## Próxima expansão semântica

- backups/snapshots Hostinger;
- firewall Hostinger;
- DNS;
- Docker Manager Hostinger;
- restore de backup;
- banco PostgreSQL/MySQL: backup, restore, migration e health;
- certificados TLS;
- renovação/checagem de domínio;
- gestão de usuários SSH;
- fail2ban/firewall Linux;
- rotação de logs;
- manutenção de disco;
- deploy por release imutável;
- rollback por release;
- inventário automático de serviços;
- análise de 502/504;
- verificação de dependências externas;
- criação de snapshot antes de ação destrutiva.

Enquanto uma operação oficial Hostinger ainda não tiver wrapper semântico, `hostinger_api_call` pode cobrir o endpoint com confirmação proporcional ao risco. Enquanto uma operação Linux não tiver wrapper, `infra_exec_command` pode cobri-la somente em break-glass.
