# Matriz de Risco

| Nível | Exemplos | Regra |
|---|---|---|
| READ | status, logs, métricas, git log | executar diretamente |
| OPERATIONAL | git fetch, diagnóstico | executar se solicitado |
| CRITICAL | restart serviço, deploy, alterar env, apt upgrade, reboot VPS | explicar efeito + `CONFIRMO` |
| DESTRUCTIVE | recreate VPS, delete, apagar volume/banco, reset irreversível | backup/snapshot quando possível + `CONFIRMO_DESTRUTIVO` |
| BREAK_GLASS | comando shell arbitrário | servidor habilitado + razão + `BREAK_GLASS` |

## Regras adicionais

- Stop de VPS é crítico mesmo que reversível porque causa indisponibilidade.
- Recreate de VPS é destrutivo.
- Alteração de firewall pode cortar o próprio acesso; tratar como crítico/destrutivo conforme regra.
- Restore de banco sobrescrevendo produção é destrutivo.
- `git reset --hard` só deve ocorrer automaticamente como rollback para commit registrado pelo próprio deploy, ou por confirmação destrutiva.
- Nunca fazer `apt autoremove`, limpeza agressiva de Docker ou exclusão de logs sem análise de impacto.
