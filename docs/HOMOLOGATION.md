# Homologação

Não liberar administração irrestrita antes de completar esta sequência.

## Fase 1 — somente leitura

- conectar MCP;
- `infra_status`;
- `hostinger_list_vps`;
- `hostinger_vps_status`;
- `hostinger_vps_metrics`;
- `service_status` em Omie e WhatsApp;
- `service_logs`;
- `docker_ps`;
- `git_status`;
- `env_list_keys` sem vazamento de valores.

## Fase 2 — mutações controladas

- restart de serviço de teste;
- alteração de variável não sensível e rollback pelo backup;
- `nginx_test`;
- reload Nginx após configuração válida;
- Docker restart em container de teste.

## Fase 3 — deploy

- projeto de teste;
- working tree limpa;
- deploy de commit conhecido;
- health success;
- simular health failure e confirmar rollback.

## Fase 4 — Hostinger control plane

- confirmar VM ID correta;
- validar métricas;
- testar restart em janela autorizada;
- confirmar retorno da VPS;
- reconectar SSH;
- validar serviços críticos.

## Fase 5 — break-glass

- manter desabilitado em produção inicialmente;
- habilitar somente para teste controlado;
- executar comando inofensivo;
- validar auditoria;
- desabilitar novamente.

## Critério de pronto

- autenticação externa ativa;
- segredos fora do Git;
- known_hosts validado;
- auditoria funcionando;
- política de confirmação validada;
- rollback testado;
- recuperação por Hostinger API testada;
- documentação de projetos preenchida com dados reais.
