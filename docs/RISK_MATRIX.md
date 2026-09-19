# Matriz de Risco

Versão: 2026-09-19

| Nível | Exemplos | Regra |
|---|---|---|
| READ | status, logs, métricas, inventory, Git log, Hostinger websites/orders/files/SSL/builds | executar diretamente |
| OPERATIONAL | git fetch, diagnóstico sem mutação | executar quando útil |
| CRITICAL | restart de serviço/container/Node.js, deploy, alterar env, apt upgrade, VPS start/stop/restart | explicar efeito + `CONFIRMO` |
| DESTRUCTIVE | delete website/DB, apagar volume, recreate, restore sobrescrevendo produção | recuperação/backup quando possível + `CONFIRMO_DESTRUTIVO` |
| BREAK_GLASS | shell arbitrário | flag habilitada + razão + `BREAK_GLASS` |

## Hostinger Shared Hosting

Leitura sem confirmação:
- list orders/websites;
- list/read arquivos permitidos;
- Git auto-deploy status;
- SSL status;
- bancos;
- cron;
- Node.js settings/builds/logs/runtime/env keys/vulnerabilities.

Crítico:
- restart Node.js.

Não expostos semanticamente nesta versão, mas se usados por fallback:
- substituir conjunto inteiro de env Node.js: crítico e de alto risco; nunca reutilizar valores `********`;
- iniciar build que sobrescreve conteúdo publicado: tratar como crítico com forte confirmação e preflight;
- alterar Git auto-deploy, PHP, cache, redirects ou SSL: crítico;
- deletar website, banco ou SSL: destrutivo.

## Firewall, Docker network/volume e observabilidade (adicionado 2026-09-19)

| Tool | Risco | Regra |
|---|---|---|
| `firewall_status` | leitura | sem confirmação |
| `firewall_allow` / `firewall_delete_rule` | crítico | `CONFIRMO` — alteração de firewall pode cortar o próprio acesso (ver regra abaixo, agora com tool dedicada) |
| `service_enable` / `service_disable` | crítico | `CONFIRMO` |
| `docker_network_ls` / `docker_volume_ls` | leitura | sem confirmação |
| `docker_network_rm` / `docker_volume_rm` | destrutivo | `CONFIRMO_DESTRUTIVO`; a tool já recusa sozinha se houver container anexado/referenciando — não depender só da confirmação humana para essa checagem |
| `docker_compose_action(action="down")` | destrutivo | `CONFIRMO_DESTRUTIVO`, diferente das demais ações do mesmo tool (pull/build/up/restart = crítico) |
| `infra_listening_ports` / `infra_pm2_list` / `infra_cron_list` | leitura | sem confirmação; `infra_pm2_list` nunca deve vazar `pm2_env.env` |
| `file_delete` | destrutivo | `CONFIRMO_DESTRUTIVO`; backup automático antes; resolve caminho real (`realpath -m`) e revalida raiz permitida antes de apagar |

## Regras adicionais

- Stop de VPS é crítico mesmo sendo reversível porque causa indisponibilidade.
- Recreate de VPS é destrutivo.
- Alteração de firewall pode cortar o próprio acesso — achado real de 2026-09-19: o firewall estava totalmente inativo (nenhuma regra, policy ACCEPT); ao corrigir, garantir a liberação de SSH (22) *antes* de aplicar `default deny incoming`, nessa ordem exata, para não perder acesso remoto.
- Restore de banco sobrescrevendo produção é destrutivo.
- `git reset --hard` não é rotina operacional. Rollback deve usar o mecanismo declarativo do deploy quando disponível.
- Não fazer `apt autoremove`, prune agressivo de Docker ou remoção de logs/volumes sem análise.
- Remoção de container/rede/volume Docker: preferir investigar evidência de uso real (logs, histórico de acesso) antes de classificar algo como "lixo" — um serviço parado não é necessariamente descartável.
- Caminho para `file_delete`/`file_write`/leitura de arquivo: nunca confiar só na checagem textual de prefixo — um `..` ou symlink pode escapar da raiz permitida; resolver o caminho real no host antes de agir quando a operação for destrutiva.
- Timeout de mutação não autoriza retry automático; primeiro verificar estado.
- O registro Hostinger legado do VPClick não deve ser deletado apenas porque a produção está na VPS.
