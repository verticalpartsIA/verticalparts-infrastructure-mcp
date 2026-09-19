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

## Regras adicionais

- Stop de VPS é crítico mesmo sendo reversível porque causa indisponibilidade.
- Recreate de VPS é destrutivo.
- Alteração de firewall pode cortar o próprio acesso.
- Restore de banco sobrescrevendo produção é destrutivo.
- `git reset --hard` não é rotina operacional. Rollback deve usar o mecanismo declarativo do deploy quando disponível.
- Não fazer `apt autoremove`, prune agressivo de Docker ou remoção de logs/volumes sem análise.
- Timeout de mutação não autoriza retry automático; primeiro verificar estado.
- O registro Hostinger legado do VPClick não deve ser deletado apenas porque a produção está na VPS.
