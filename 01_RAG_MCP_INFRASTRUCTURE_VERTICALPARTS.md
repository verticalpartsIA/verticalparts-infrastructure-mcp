# 01 — RAG CANÔNICO — MCP Infrastructure VerticalParts

Versão: 2026-09-19
Classificação: conhecimento operacional canônico
Objetivo: recuperação contextual para LLMs, agentes MCP, Claude, Claude Code e automações.

---

## RAG-000 — Regra de uso

Este documento deve ser recuperado por intenção. Ele ensina a LLM a descobrir o estado real e a escolher a menor intervenção suficiente. Fatos de produção mudam; por isso a LLM deve usar o RAG para saber COMO descobrir a verdade viva, e não tratar cada snapshot como eterno.

Consultas que devem recuperar este RAG incluem: site caiu, MCP não conecta, Claude perdeu conexão, adicionar site, domínio, deploy, Hostinger, VPS, shared hosting, 502, 504, Nginx, Docker, systemd, Git, env, token, X-API-Key, Omie, WhatsApp MCP, Infrastructure MCP, inventário, DNS, SSL, migração e Claude Code MCP.

---

## RAG-001 — Missão

O VerticalParts Infrastructure MCP é a camada administrativa por LLM da infraestrutura VerticalParts.

Ele combina três planos:

1. Hostinger Control Plane
   - API Hostinger;
   - VPS;
   - hosting/websites;
   - recursos oficiais expostos pela API.

2. VPS Operations Plane
   - SSH;
   - systemd;
   - Docker;
   - Git;
   - arquivos;
   - variáveis;
   - Nginx;
   - APT;
   - deploy;
   - health;
   - auditoria.

3. Plano de conhecimento operacional
   - config/inventory.yaml;
   - config/projects.yaml;
   - documentação canônica;
   - estado vivo.

A missão não é executar comandos. A missão é transformar intenção operacional em ação segura, observável, verificável e reversível.

---

## RAG-002 — Hierarquia de verdade

Em caso de divergência:

1. Estado vivo observado.
2. config/inventory.yaml do runtime.
3. config/projects.yaml do runtime.
4. Código do MCP.
5. Documentação canônica numerada da raiz.
6. Documentação histórica em docs/ e rag/.
7. Memória de conversa.

Estado vivo inclui DNS, Hostinger API, systemd, Docker, Git, Nginx, health, TLS, portas e processos.

Nunca altere produção para “bater com a documentação” sem provar que a documentação representa a intenção atual.

---

## RAG-002A — Homologação viva de Docker e VPClick em 2026-09-19

Evidência operacional validada depois da correção:

- `infra_list_projects` retorna `omie-mcp`, `whatsapp-mcp` e `vpclick`;
- `vpclick.path = /docker/vpclick`;
- `vpclick.runtime.type = docker_compose`;
- `vpclick.runtime.container = vpclick-vpclick-1`;
- `vpclick.deploy.mode = external`;
- `vpclick.deploy.provider = github_actions`;
- `vpclick.deploy.workflow = .github/workflows/deploy-vps.yml`;
- `docker_ps` executou com sucesso via `sudo docker`, `exit_status: 0`;
- `docker_compose_action("/docker/vpclick", "ps")` executou com sucesso;
- container `vpclick-vpclick-1` observado `running`;
- publicação observada: `127.0.0.1:8091->80/tcp`.

Interpretação obrigatória para LLM:

- não chamar o erro antigo de socket Docker de "intermitente" sem nova evidência;
- o estado atual conhecido é "corrigido e homologado";
- se `permission denied` reaparecer, isso é regressão a investigar;
- não adicionar `infra-mcp` ao grupo `docker` automaticamente;
- preferir o caminho controlado `sudo docker` já previsto pela política de privilégio da VPS;
- não executar `deploy_project("vpclick")`: seu deploy é externo e deve ser tratado pelo GitHub Actions;
- Infrastructure MCP pode inspecionar/reiniciar o runtime Docker quando autorizado, mas não deve substituir silenciosamente o pipeline de publicação do VPClick.

---

## RAG-003 — Topologia conhecida

Snapshot em 2026-09-19. Validar antes de mutações.

Infrastructure MCP:
- endpoint: https://infra-mcp.vpsistema.com/mcp
- transporte: Streamable HTTP
- autenticação pública: header X-API-Key no gateway/Nginx
- bind interno: 127.0.0.1:8020
- serviço: verticalparts-infra-mcp.service
- instalação: /opt/verticalparts-infrastructure-mcp
- usuário: infra-mcp
- break-glass: desligado por padrão.

VPS atual:
- Hostinger VM ID: 1510643
- hostname: srv1510643.hstgr.cloud
- IPv4: 72.61.48.156
- SO observado: Ubuntu 24.04 LTS.

SSH operacional:
- host atual: 127.0.0.1 durante homologação na própria VPS;
- usuário: infra-mcp;
- chave: /opt/verticalparts-infrastructure-mcp/secrets/id_ed25519;
- known_hosts: /opt/verticalparts-infrastructure-mcp/secrets/known_hosts.

Limitação: hoje o Infrastructure MCP roda na VPS que administra. Se a máquina cair totalmente, o próprio MCP também cai. Produção resiliente deve mover o control plane para outro host.

---

## RAG-004 — MCPs relacionados

Omie remoto:
- endpoint: https://mcp.vpsistema.com/omie/mcp
- serviço: omie-mcp.service
- upstream observado: 127.0.0.1:8000
- diretório observado: /root/omie-mcp.

WhatsApp remoto:
- endpoint: https://whatsapp-mcp.vpsistema.com/mcp
- health: https://whatsapp-mcp.vpsistema.com/health
- serviço: whatsapp-mcp.service
- upstream: 127.0.0.1:8010
- diretório: /root/whatsapp-mcp-hub/whatsapp-mcp
- autenticação pública: X-API-Key
- arquivo autorizado de recuperação da chave: /root/whatsapp-mcp-auth-token.

Infrastructure remoto:
- endpoint: https://infra-mcp.vpsistema.com/mcp
- serviço: verticalparts-infra-mcp.service
- autenticação pública: X-API-Key
- arquivo autorizado de recuperação da chave: /root/infra-mcp-auth-token.

vpprd-mcp (não é um dos 3 MCPs canônicos do Claude, é interno da VPS):
- servidor MCP "vpprd-browser", systemd `vpprd-mcp.service`, porta 3100;
- exposto via `mcp.vpsistema.com` no `location /` (fora de `/omie/`), protegido por `X-API-Key` desde 2026-09-19 — arquivo `/root/vpprd-mcp-auth-token`;
- também tem autenticação própria via Bearer token na aplicação (camada adicional, independente do gateway).

Omie local:
- nome Claude Code: omie-verticalparts
- launcher Windows: C:\Users\gelso\omie-mcp\omie-mcp-global.cmd
- é um processo local; não confundir com o Omie remoto.

---

## RAG-005 — Matriz Claude

Claude.ai Corporativo Web:
- Omie remoto;
- WhatsApp remoto;
- Infrastructure remoto.

Claude Gelson Simões Desktop/Web:
- Omie remoto;
- WhatsApp remoto;
- Infrastructure remoto.

Claude Code:
- MCPs remotos quando desejado;
- Omie local omie-verticalparts para desenvolvimento/teste;
- Infrastructure remoto quando desejado.

Conectores remotos do Claude são acessados pela infraestrutura em nuvem da Anthropic. O endpoint precisa estar publicamente acessível por HTTPS.

---

## RAG-006 — Como conectar Claude

VerticalParts Infrastructure:
- URL: https://infra-mcp.vpsistema.com/mcp
- autenticação: Sem login
- header: X-API-Key
- valor obtido no host autorizado com: cat /root/infra-mcp-auth-token

VerticalParts WhatsApp:
- URL: https://whatsapp-mcp.vpsistema.com/mcp
- autenticação: Sem login
- header: X-API-Key
- valor obtido com: cat /root/whatsapp-mcp-auth-token

VerticalParts Omie:
- URL: https://mcp.vpsistema.com/omie/mcp
- configuração atual: sem header adicional no conector.

Se o Claude marcar login detectado para Infrastructure/WhatsApp, isso pode ser o probe sem chave recebendo 401. Selecionar Sem login e configurar X-API-Key.

Nunca colar a chave em documentação ou chat.

---

## RAG-007 — Inventário de produção

A primeira consulta lógica deve ser infra_inventory.

Snapshot de 2026-09-19:

Produção na VPS:
- infra-mcp.vpsistema.com
- mcp.vpsistema.com
- whatsapp-mcp.vpsistema.com
- vpclick.vpsistema.com

Redirect legado:
- requisicoes.vpsistema.com -> vprequisicoes.vpsistema.com

Produção no shared hosting:
- vprequisicoes.vpsistema.com
- assetmanager.vpsistema.com
- gentegestao.vpsistema.com
- escamaxcompravp.vpsistema.com
- vpgestaoimportacao.vpsistema.com
- interativo.vpsistema.com
- propostas.vpsistema.com
- vpdashboarddre.vpsistema.com
- posvenda360.vpsistema.com
- vpsistema.com
- www.vpsistema.com
- visitas.vpsistema.com
- suporte.vpsistema.com
- catraca.vpsistema.com

Observações:
- vpclick.vpsistema.com pode continuar cadastrado na API de Websites da Hostinger, mas produção está na VPS.
- vpsistema.com e visitas.vpsistema.com podem ter Nginx obsoleto na VPS enquanto o DNS público aponta para shared hosting.
- cadastro Hostinger ativo não prova que o tráfego de produção vai para aquele ambiente.

---

## RAG-008 — Regra Docker

Estado atual: VPClick é o projeto de aplicação intencionalmente em Docker na VPS.

Não inferir que “site na VPS = Docker”.

VPRequisições está no shared hosting Node.js.

Para novo site, classificar antes:
1. shared hosting;
2. VPS com systemd/processo nativo;
3. VPS estático;
4. Docker apenas quando a arquitetura exigir.

Nunca converter projeto para Docker apenas por conveniência.

---

## RAG-009 — Catálogo atual de tools

Inventário:
- infra_status
- infra_list_projects
- infra_inventory

Hostinger:
- hostinger_list_vps
- hostinger_list_websites
- hostinger_list_orders
- hostinger_vps_status
- hostinger_vps_metrics
- hostinger_vps_start
- hostinger_vps_stop
- hostinger_vps_restart
- hostinger_website_files
- hostinger_website_file_read
- hostinger_git_autodeploy_status
- hostinger_ssl_status
- hostinger_list_databases
- hostinger_list_cron_jobs
- hostinger_nodejs_settings
- hostinger_nodejs_builds
- hostinger_nodejs_build_logs
- hostinger_nodejs_runtime_logs
- hostinger_nodejs_env_keys
- hostinger_nodejs_vulnerabilities
- hostinger_nodejs_restart
- hostinger_api_call

systemd:
- service_status
- service_logs
- service_start
- service_stop
- service_restart

Docker:
- docker_ps
- docker_logs
- docker_restart
- docker_compose_action

Git:
- git_status
- git_log
- git_fetch
- git_pull

Arquivos/env:
- file_read
- file_write
- env_list_keys
- env_set
- env_remove

Nginx:
- nginx_test
- nginx_reload

Sistema:
- apt_check_updates
- apt_upgrade

Deploy:
- deploy_project

Break-glass:
- infra_exec_command

Total observado em homologação em 2026-09-19 (sessão 1): 49 tools.

---

## RAG-009A — Shared Hosting Hostinger homologado em 2026-09-19

Estado vivo observado:

- 14 websites acessíveis pela API Hosting;
- dois planos/ordens: um Cloud e um Premium;
- 9 sites classificados pela Hostinger como `nodejs` na conta Cloud, todos com auto-deploy Git ativo;
- 5 sites classificados como `other` na conta Premium, todos com PHP 8.3.33 disponível, mas sem auto-deploy Git Hostinger;
- classificação `other` não prova aplicação PHP: observar arquivos reais e runtime antes de concluir;
- `vprequisicoes.vpsistema.com` usa Node.js 22, build Hostinger/Passenger e integração Git com `verticalpartsIA/003_requisicoes` branch `main`;
- SSL de `vprequisicoes.vpsistema.com` foi testado pela própria tool MCP `hostinger_ssl_status` e retornou ativo com redirect HTTPS;
- `vpclick.vpsistema.com` continua cadastrado como Node.js no Shared Hosting e com auto-deploy Git, mas essa superfície é legado. Produção canônica permanece Docker na VPS.

Regra: preferir as tools semânticas acima ao `hostinger_api_call`. O fallback genérico fica para endpoints oficiais ainda não encapsulados.

---

## RAG-009A2 — Tools adicionadas em 2026-09-19 (sessão 2, auditoria de segurança)

Firewall (ufw):
- firewall_status (read)
- firewall_allow (CRITICAL)
- firewall_delete_rule (CRITICAL)

systemd:
- service_enable (CRITICAL)
- service_disable (CRITICAL)

Docker:
- docker_network_ls (read)
- docker_volume_ls (read)
- docker_network_rm (DESTRUCTIVE — recusa se houver container anexado)
- docker_volume_rm (DESTRUCTIVE — recusa se algum container referenciar o volume)
- docker_compose_action: nova ação `down` (DESTRUCTIVE, distinta de pull/build/up/restart que são CRITICAL)

Observabilidade de host:
- infra_listening_ports (read — `ss -tlnp`)
- infra_pm2_list (read — processos PM2 sob root; nunca retorna `pm2_env.env`, que carregaria segredos)
- infra_cron_list (read — crontab root + conteúdo de `/etc/cron.d`)

Arquivos:
- file_delete (DESTRUCTIVE — backup `.tar.gz` automático antes; resolve o caminho real via `realpath -m` e revalida contra as raízes permitidas antes de apagar, para não ser enganado por `..` ou symlink)

Total observado em homologação em 2026-09-19 (sessão 2): **62 tools**. PR de origem: `verticalpartsIA/verticalparts-infrastructure-mcp#1`.

---

## RAG-009B — Segurança do host: achados e correções de 2026-09-19 (sessão 2)

Com break-glass habilitado (confirmação por comando, auditado), uma varredura do host encontrou:

- firewall (`ufw`) totalmente inativo, corrigido: ativo desde 2026-09-19, `default deny incoming`, liberado apenas `22/tcp`, `80/tcp`, `443/tcp` (+ IPv6). Use `firewall_status` para conferir o estado real antes de assumir que uma porta está acessível ou bloqueada;
- Tor com `SocksPort 0.0.0.0:9050` (não é o padrão) e evidência real de abuso como proxy aberto — desativado;
- Cloudflare WARP instalado mas nunca configurado — desativado;
- `hermes-agent-god7` (terminal remoto do template Hostinger, não confundir com "Hermes AI Agent"/NousResearch) sem uso real relevante e sem rota externa funcional (Traefik sem porta mapeada) — removido com backup;
- `mcp.vpsistema.com` expunha `vpprd-mcp` (porta 3100) via `location /` sem `X-API-Key` — corrigido, mesmo padrão dos outros MCPs;
- usuário `infra-mcp` tem `sudo (ALL) NOPASSWD: ALL` — o break-glass é root irrestrito, não só Docker;
- `/opt/verticalparts-infrastructure-mcp` é `root:root`, o que bloqueia as tools estruturadas de escrita (`git_pull`, `file_write`, `env_set`) nesse diretório especificamente — usar break-glass para auto-atualização (ver `05_RUNBOOK` PARTE G).

A pilha de automação da VPS é maior do que os projetos historicamente registrados (`omie-mcp`, `whatsapp-mcp`, `vpclick`): inclui `evolution-api`, `n8n`, `vp-infra`, `traefik`, `stt-service`, `telegram-claude`, `vpprd-mcp`, crons de negócio (`bordero`, `vpclick-cobranca`, `sac-backfill-diario`, `cron-handoffs`) e checkouts diversos. O roster completo e atualizado vive em `config/projects.yaml` do runtime — não duplicado aqui de propósito.

---

## RAG-010 — Política de risco

Leitura: sem confirmação.

Crítico/reversível: CONFIRMO.
Exemplos: restart, deploy, env_set, env_remove, file_write, nginx_reload, apt_upgrade e ciclo de vida da VPS.

Destrutivo: CONFIRMO_DESTRUTIVO e estratégia de recuperação.
Exemplos: delete, remoção de volume, restore sobrescrevendo produção, recreate, limpeza irreversível.

Break-glass:
- INFRA_ALLOW_BREAK_GLASS=true;
- confirmation BREAK_GLASS;
- reason;
- nenhuma tool semântica adequada disponível.

---

## RAG-011 — Diagnóstico de MCP desconectado

Sintomas: Reconectar, tools sumiram, custom connector falha, Claude não chama tool.

Ordem:

1. Identificar qual Claude.
2. Identificar qual MCP.
3. Testar endpoint público.
4. Testar autenticação.
5. Testar DNS e TLS.
6. Testar Nginx.
7. Testar serviço local.
8. Testar MCP em loopback.
9. Só então alterar ou reiniciar.

Nunca concluir que “Claude quebrou” ou “VPS caiu” sem evidência.

---

## RAG-012 — Significado de HTTP

401:
- geralmente endpoint vivo;
- credencial ausente ou incorreta;
- para Infrastructure/WhatsApp, revisar X-API-Key.

403:
- policy, firewall ou autorização.

404:
- path incorreto ou route/location incorreta;
- endpoints MCP canônicos terminam em /mcp.

502:
- proxy está vivo;
- upstream provavelmente não respondeu;
- verificar serviço, porta, processo.

504:
- upstream lento/travado, timeout ou dependência.

---

## RAG-013 — Diagnóstico 502/504

Sequência:
1. DNS;
2. HTTPS/TLS;
3. ambiente real;
4. Nginx;
5. upstream/porta;
6. serviço/container;
7. logs;
8. CPU/RAM/disco;
9. banco/dependências;
10. mudança mínima.

Restart é consequência de diagnóstico, não primeiro passo.

---

## RAG-014 — systemd

Fluxo:
1. service_status;
2. service_logs;
3. identificar erro;
4. pedir CONFIRMO se restart;
5. service_restart;
6. status novamente;
7. health externo.

Active não significa saudável. Validar aplicação.

---

## RAG-015 — Git e deploy

Preferir deploy_project para projetos registrados.

Preflight:
- projeto cadastrado;
- path real;
- repo real;
- branch real;
- working tree limpa;
- old SHA conhecido;
- build conhecido;
- runtime conhecido;
- health conhecido.

Política:
- pull --ff-only;
- sem merge implícito;
- sem reset --hard automático;
- repo sujo bloqueia deploy.

Se health falhar:
- rollback para old SHA quando configurado;
- restart;
- revalidar;
- relatar novo estado e estado recuperado.

---

## RAG-016 — Shared Hosting Hostinger

Shared hosting é outro plano operacional; não é “a VPS”.

Ao operar shared hosting:
- não usar SSH da VPS por reflexo;
- usar Hostinger API/hPanel/pipeline do site;
- descobrir website real;
- validar DNS;
- validar deploy e URL pública.

Se GitHub Actions é o mecanismo de deploy, preservar esse fluxo.

VPRequisições é exemplo de projeto que não deve ser iniciado na VPS só porque existe código antigo lá.

---

## RAG-017 — Novo site

Pedido “coloque este site no ar” exige descobrir:
- domínio;
- repo;
- branch;
- stack;
- build;
- start;
- porta se houver;
- env;
- banco/dependências;
- destino;
- estratégia de deploy;
- health;
- TLS;
- DNS.

Classificar destino antes de implementar.

Ao finalizar:
- atualizar inventory.yaml;
- atualizar projects.yaml quando operável pelo MCP;
- testar URL externa;
- registrar runtime;
- documentar mudança.

---

## RAG-018 — Migração entre ambientes

Nunca mudar DNS primeiro.

Fluxo:
1. mapear origem;
2. preparar destino;
3. deploy;
4. health interno;
5. TLS;
6. cutover DNS;
7. health externo;
8. preservar rollback;
9. marcar origem legacy/migrated;
10. remover legado somente após validação e janela segura.

---

## RAG-019 — Nginx e TLS

Nginx:
- sempre nginx -t antes de reload;
- se test falhar, não reload;
- portas internas devem ficar em loopback quando possível;
- proxy público deve terminar TLS e autenticação.

TLS:
1. DNS correto;
2. HTTP alcançável;
3. certificado;
4. renovação;
5. HTTPS;
6. redirect adequado.

Não remover certificado necessário para redirect legado sem checar impacto.

---

## RAG-020 — Segredos

Segredo nunca é conteúdo de RAG.

Pode documentar nome, localização e comando de recuperação. Nunca o valor.

Infrastructure MCP:
cat /root/infra-mcp-auth-token

WhatsApp MCP:
cat /root/whatsapp-mcp-auth-token

Hostinger API token:
fica no ambiente do Infrastructure MCP; não retornar ao modelo.

GitHub:
preferir SSH/GitHub App; não embutir PAT em remote URL.

---

## RAG-021 — Rotação de X-API-Key

1. gerar nova chave;
2. atualizar gateway de forma segura;
3. nginx -t;
4. reload;
5. atualizar clientes Claude;
6. testar;
7. revogar/remover chave antiga;
8. nunca versionar o valor.

Se houver vários clientes, planejar coexistência temporária de duas chaves quando possível.

---

## RAG-022 — Hostinger API

Base observada: https://developers.hostinger.com

A API evolui.

Regras:
- wrapper semântico primeiro;
- hostinger_api_call apenas para endpoint oficial ainda não encapsulado;
- nunca inventar path;
- consultar documentação atual;
- aplicar classificação de risco.

O MCP oficial da Hostinger é complemento, não substituto do VerticalParts Infrastructure MCP. O MCP VerticalParts adiciona SSH, inventário, deploy, políticas e contexto específico.

---

## RAG-023 — Timeout de mutação

Timeout não prova falha.

Após timeout:
1. não repetir;
2. consultar estado;
3. verificar logs;
4. confirmar se efeito ocorreu;
5. repetir apenas se necessário.

Aplicar a restart, deploy, API Hostinger, Nginx, Git e updates.

---

## RAG-024 — Atualização e reboot

apt_upgrade não implica reboot.

Fluxo:
1. apt_check_updates;
2. explicar impacto;
3. CONFIRMO;
4. apt_upgrade;
5. verificar necessidade de reboot;
6. tratar reboot como ação separada;
7. validar serviços após retorno.

---

## RAG-025 — Auditoria e rollback

Toda mutação deve produzir evidência auditável sem segredo.

Auditoria atual:
 /opt/verticalparts-infrastructure-mcp/data/audit.jsonl

Reversibilidade:
- arquivo -> backup;
- env -> backup;
- Git -> old SHA;
- deploy -> rollback;
- Nginx -> test + backup;
- destrutivo -> snapshot/backup quando viável.

Antes de mudar, responder: “como volto se falhar?”

---

## RAG-026 — Saúde em camadas

1. provider;
2. VPS;
3. rede;
4. DNS;
5. TLS;
6. proxy;
7. runtime;
8. aplicação;
9. banco;
10. dependências;
11. funcionalidade externa.

Não reduzir “saúde” a systemctl active.

---

## RAG-027 — Quando parar

Pedir clarificação se:
- dois targets são plausíveis e leitura não resolve;
- operação destrutiva não tem alvo exato;
- não existe estratégia mínima de recuperação;
- credencial necessária está ausente;
- branch/runtime desconhecido;
- pedido contradiz inventário e estado vivo sem evidência suficiente.

Não perguntar o que pode ser descoberto por leitura segura.

---

## RAG-028 — Anti-padrões

Nunca como padrão:
- reiniciar tudo;
- mostrar arquivo .env;
- colar token;
- Docker prune agressivo;
- apagar volume;
- git reset --hard automático;
- nginx reload sem nginx -t;
- inventar endpoint Hostinger;
- assumir shared hosting porque aparece na API;
- assumir VPS porque existe config local;
- assumir Docker;
- confundir Omie local/remoto;
- reiniciar VPS para falha local do Claude Code;
- declarar deploy concluído sem health.

---

## RAG-029 — Testes de compreensão

A LLM deve saber responder:

1. Onde está o VPClick e por que pode aparecer no shared hosting?
2. Onde está VPRequisições?
3. Qual domínio legado redireciona para VPRequisições?
4. Qual serviço publica o Infrastructure MCP?
5. Como recuperar a X-API-Key sem versioná-la?
6. Por que 401 pode indicar endpoint vivo?
7. Qual a diferença entre Omie remoto e local?
8. Por que mover o control plane para outro host é desejável?
9. Como adicionar novo site sem assumir Docker?
10. Como reconciliar DNS, Hostinger Websites e inventário?

---

## RAG-030 — Prompt canônico

~~~text
Você opera a infraestrutura VerticalParts por meio do VerticalParts Infrastructure MCP.

OBJETIVO
Resolver a necessidade com a menor intervenção suficiente, preservando disponibilidade, segurança, auditabilidade e rollback.

REGRAS
1. Identifique ambiente e alvo antes de mutar.
2. Consulte inventory e estado vivo.
3. Não confunda cadastro com produção.
4. Prefira tools semânticas.
5. Não invente identificadores.
6. Nunca revele segredos.
7. Operações críticas exigem CONFIRMO.
8. Destrutivas exigem CONFIRMO_DESTRUTIVO e recuperação planejada.
9. Break-glass exige BREAK_GLASS, reason e flag habilitada.
10. Timeout exige verificação de estado antes de retry.
11. Deploy exige preflight, health e rollback.
12. Nginx exige test antes de reload.
13. Novo site exige classificação de ambiente; Docker não é default.
14. Depois de mutação, valide interna e externamente.
15. Mudança de topologia exige atualização de inventário/documentação.
~~~

---

## RAG-031 — Fontes oficiais

Anthropic:
https://support.claude.com/pt/articles/11175166-comece-com-conectores-personalizados-usando-mcp-remoto

https://support.claude.com/pt/articles/11176164-use-conectores-para-estender-os-recursos-do-claude

Hostinger:
https://developers.hostinger.com/

https://www.hostinger.com/support/11079316-hostinger-api-mcp-server/

https://mcp.hostinger.com

Projeto:
- código deste repositório;
- inventário privado do runtime;
- registry privado de projetos.

---

## RAG-032 — Critério de incidente encerrado

O incidente só termina quando:
- serviço restaurado ou causa identificada;
- endpoint público testado;
- autenticação testada;
- tools listáveis quando aplicável;
- inventário coerente;
- nenhum segredo exposto;
- rollback concluído ou desnecessário;
- estado final comunicado.
