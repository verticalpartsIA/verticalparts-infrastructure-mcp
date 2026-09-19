# 04 — SDD — VerticalParts Infrastructure MCP

Versão: 2026-09-19
Status: canônico
Objetivo: descrever arquitetura, componentes, fluxos, contratos técnicos, segurança, falhas e evolução.

---

## 1. Visão geral

O VerticalParts Infrastructure MCP é um control plane semântico para infraestrutura VerticalParts.

Arquitetura lógica:

~~~text
Claude / Claude Code / outro cliente MCP
                |
                | HTTPS + MCP Streamable HTTP
                v
        Nginx / Gateway público
        TLS + X-API-Key
                |
                | loopback
                v
VerticalParts Infrastructure MCP
                |
       +--------+---------+
       |                  |
       v                  v
Hostinger API          SSH Plane
       |                  |
       v                  v
VPS / Websites       Linux da VPS
Control Plane        systemd/Docker/Git
                     env/Nginx/APT/deploy
~~~

O componente MCP também carrega:
- policies;
- projects registry;
- infrastructure inventory;
- audit log.

---

## 2. Componentes

### 2.1 FastMCP server

Código:
src/verticalparts_infra_mcp/server.py

Responsabilidades:
- registrar tools;
- validar argumentos;
- aplicar guardrails;
- chamar Hostinger/SSH/deploy;
- escrever auditoria;
- executar Streamable HTTP.

Bind atual:
127.0.0.1:8020.

---

### 2.2 Settings

Código:
src/verticalparts_infra_mcp/config.py

Responsabilidades:
- carregar .env;
- Hostinger base/token/VM ID;
- SSH;
- projects file;
- inventory file;
- policies;
- audit;
- allowed paths;
- break-glass.

Segredos ficam no ambiente do host, não no Git.

---

### 2.3 Hostinger Client

Código:
src/verticalparts_infra_mcp/hostinger.py

Responsabilidades:
- autenticação Bearer;
- request genérico;
- list VPS;
- list websites e hosting orders;
- get VPS;
- metrics;
- start/stop/restart da VPS;
- listagem e leitura segura de arquivos do Shared Hosting;
- Git auto-deploy status;
- SSL status;
- bancos e cron jobs;
- Node.js settings, builds, build logs e runtime logs;
- listagem de nomes de env Node.js sem exposição de valores;
- vulnerabilidades Node.js;
- restart controlado do processo Node.js.

Design:
wrapper semântico para operações frequentes + fallback oficial. O fallback genérico não deve substituir uma tool semântica existente.

---

### 2.3A Docker privilege execution

Docker tools execute through the SSH plane using controlled privilege escalation:

- read: `sudo docker ps`, `sudo docker logs`, `sudo docker compose ... ps/logs`;
- mutation: `sudo docker restart`, `sudo docker compose pull/build/up/restart`;
- mutations remain protected by the MCP confirmation model.

Rationale:

- the service user `infra-mcp` does not need direct membership in the Docker group;
- membership in the Docker group is effectively root-equivalent and should not be the default fix;
- privilege stays explicit in the command path and auditable through MCP operations.

Homologated 2026-09-19 against `/docker/vpclick`: both `docker_ps` and Compose `ps` returned exit status 0.

### 2.3B External-deploy projects

A registered project may declare deployment as external, for example GitHub Actions. For such projects, `deploy_project` must refuse publication rather than bypass the declared external pipeline. Runtime inspection/control and deployment are separate responsibilities.

VPClick is the canonical current example, with deployment via `.github/workflows/deploy-vps.yml`.

---

### 2.4 SSH Plane

Código:
src/verticalparts_infra_mcp/ssh.py

Responsabilidades:
- conexão SSH;
- key auth;
- known_hosts;
- command execution;
- path allowlist (`assert_allowed_path`, rejeita qualquer `..` desde 2026-09-19 — ver T-008);
- leitura/escrita controlada.

Estado atual:
MCP e target estão na mesma VPS, então host é 127.0.0.1.

Limitação conhecida desde 2026-09-19: as tools que passam por `ssh.write_text`/`assert_allowed_path` (`file_write`, `env_set`, `env_remove`, `git_pull`, `git_fetch`) rodam como usuário `infra-mcp` **sem sudo**. Isso bloqueia escrita em qualquer caminho `root:root`, incluindo o próprio `/opt/verticalparts-infrastructure-mcp`. Só `infra_exec_command` (break-glass, roda com `sudo`) consegue escrever ali. Ver 05_RUNBOOK PARTE G para o fluxo de auto-atualização real (inclui `git config --global --add safe.directory`, necessário por "dubious ownership" do Git ao operar um repositório de outro dono).

Arquitetura futura:
MCP externo -> SSH IP/hostname da VPS.

---

### 2.5 Registry

Código:
src/verticalparts_infra_mcp/registry.py

Dados:
- config/projects.yaml
- config/inventory.yaml

Responsabilidades:
- resolver projeto;
- carregar inventário;
- fornecer metadados operacionais.

Esses arquivos reais são privados/ignorados pelo Git.

---

### 2.6 Deploy Engine

Código:
src/verticalparts_infra_mcp/deploy.py

Responsabilidades esperadas:
- preflight;
- Git update;
- build;
- runtime restart;
- health;
- rollback.

Deploy deve ser declarativo, não shell ad hoc.

---

### 2.7 Safety

Código:
src/verticalparts_infra_mcp/safety.py

Responsabilidades:
- classes de risco;
- confirmation;
- Hostinger mutation classification;
- break-glass guard.

---

### 2.8 Audit

Código:
src/verticalparts_infra_mcp/audit.py

Destino atual:
 /opt/verticalparts-infrastructure-mcp/data/audit.jsonl

Requisito:
nenhum segredo em logs.

---

### 2.9 Gateway Nginx

Domínio:
infra-mcp.vpsistema.com

Responsabilidades:
- HTTPS;
- certificado;
- X-API-Key;
- proxy para 127.0.0.1:8020/mcp;
- impedir publicação direta da porta interna.

---

### 2.10 systemd

Service:
verticalparts-infra-mcp.service

Responsabilidades:
- lifecycle do processo;
- restart após boot;
- execução com usuário infra-mcp;
- ambiente;
- hardening.

Estado observado:
ProtectHome foi ajustado para read-only para permitir acesso SSH key/known-hosts necessários.

---

## 3. Dados de configuração

### 3.1 .env

Contém:
- transporte;
- bind;
- Hostinger;
- SSH;
- paths;
- flags.

Nunca versionar.

---

### 3.2 inventory.yaml

Objetivo:
mapa autoritativo de topologia operacional.

Não é catálogo de API. É decisão de onde a produção realmente está.

Exemplo:

~~~yaml
domains:
  vpclick.vpsistema.com:
    environment: vps
    status: production
    runtime: docker
    notes:
      - migrated_from_shared_hosting
~~~

---

### 3.3 projects.yaml

Objetivo:
permitir operações semânticas sobre projetos conhecidos.

Exemplo:

~~~yaml
projects:
  app:
    path: /opt/app
    branch: main
    runtime:
      type: systemd
      service: app.service
    health:
      url: https://app.example.com/health
      mode: http
~~~

---

### 3.4 policies.yaml

Contém:
- confirmation strings;
- deploy policy;
- secret policy;
- audit policy.

---

## 4. Fluxo MCP público

~~~text
Claude
  |
  | POST https://infra-mcp.vpsistema.com/mcp
  | Header X-API-Key
  v
Nginx
  |
  | se chave ausente/incorreta -> 401
  |
  | se válida
  v
127.0.0.1:8020/mcp
  |
  v
FastMCP
  |
  +-> initialize
  +-> tools/list
  +-> tools/call
~~~

401 no probe sem chave é comportamento de autenticação, não prova de indisponibilidade.

---

## 5. Sequence — inicialização MCP

~~~text
Client            Nginx             FastMCP
  | POST /mcp       |                  |
  |---------------->|                  |
  | X-API-Key       |                  |
  |                 | proxy            |
  |                 |----------------->|
  |                 |                  | initialize
  |                 |<-----------------|
  |<----------------| session/result   |
~~~

Cliente deve usar Accept compatível com JSON e text/event-stream conforme MCP.

---

## 6. Sequence — tools/list

1. initialize;
2. capturar Mcp-Session-Id;
3. POST tools/list com session id;
4. validar catálogo.

Esse teste é obrigatório após upgrade do MCP.

---

## 7. Sequence — infra_inventory

~~~text
Claude
  |
  | tools/call infra_inventory
  v
FastMCP
  |
  v
registry.load_inventory
  |
  v
config/inventory.yaml
  |
  v
structuredContent
~~~

O inventário não chama DNS automaticamente; ele é registro autoritativo operacional. Drift deve ser verificado separadamente.

---

## 8. Sequence — leitura Hostinger

~~~text
Claude
  |
  | hostinger_list_websites
  v
MCP
  |
  | Bearer HOSTINGER_API_TOKEN
  v
Hostinger API
  |
  v
website list
~~~

Token nunca retorna à LLM.

---

## 9. Sequence — service restart

~~~text
User request
   |
LLM service_status
   |
LLM service_logs
   |
LLM explica impacto
   |
User confirma CONFIRMO
   |
service_restart
   |
systemctl restart
   |
systemctl is-active
   |
health externo
   |
audit
~~~

---

## 10. Sequence — deploy

~~~text
request
  |
resolve project
  |
git status
  |
dirty? ---- yes ---> abort
  |
 no
  v
record old SHA
  |
CONFIRMO
  |
fetch/pull ff-only
  |
build
  |
restart runtime
  |
health
  |
  +-- OK -> success + audit
  |
  +-- FAIL -> rollback old SHA -> restart -> health -> report
~~~

---

## 11. Sequence — Hostinger VPS restart

~~~text
hostinger_vps_status
  |
explain downtime
  |
CONFIRMO
  |
Hostinger restart API
  |
poll state
  |
SSH returns
  |
critical services
  |
public health
~~~

Limitação atual:
se MCP roda na própria VPS, a conexão cai durante restart. Isso é esperado.

---

## 12. Sequence — novo site no shared hosting

~~~text
requirements
  |
hostinger_list_websites
  |
target classification = shared_hosting
  |
create/configure website via supported plane
  |
repo/deploy pipeline
  |
env
  |
build
  |
DNS
  |
TLS
  |
health
  |
inventory update
~~~

Não passa por Docker da VPS.

---

## 13. Sequence — novo site na VPS systemd

~~~text
requirements
  |
classification = vps/systemd
  |
repo -> path
  |
runtime/deps
  |
env
  |
build
  |
systemd unit
  |
bind 127.0.0.1:PORT
  |
Nginx server block
  |
DNS A/AAAA
  |
TLS
  |
health
  |
projects.yaml
  |
inventory.yaml
~~~

---

## 14. Sequence — novo site Docker

Somente se arquitetura exigir.

~~~text
requirements
  |
explicit Docker decision
  |
compose/image
  |
volumes
  |
env
  |
network
  |
loopback port
  |
health
  |
Nginx/TLS
  |
inventory
~~~

VPClick é referência atual.

---

## 15. Sequence — migração shared -> VPS

~~~text
shared production
  |
prepare VPS target
  |
internal health
  |
TLS readiness
  |
DNS cutover
  |
external health
  |
inventory: vps + migrated_from_shared
  |
rollback window
  |
legacy cleanup later
~~~

O registro antigo no shared hosting pode permanecer durante transição.

---

## 16. Segurança em camadas

Camada 1:
HTTPS.

Camada 2:
X-API-Key no gateway.

Camada 3:
MCP tool permissions.

Camada 4:
risk confirmation.

Camada 5:
allowed paths.

Camada 6:
SSH key + known_hosts.

Camada 7:
sudo policy.

Camada 8:
audit.

Camada 9:
backup/rollback.

---

## 17. Threat model

### T-001 — token vazado

Risco:
acesso ao MCP público.

Mitigação:
- rotação;
- não versionar;
- secret files chmod 600;
- logs redigidos;
- futura autenticação OAuth/identity gateway.

### T-002 — Hostinger token vazado

Risco:
control plane do provedor.

Mitigação:
- env;
- nunca retornar;
- rotação;
- scope mínimo se disponível.

### T-003 — SSH key vazada

Mitigação:
- chave dedicada;
- file permissions;
- known_hosts;
- revogar authorized_keys;
- nova chave.

### T-004 — prompt injection via conteúdo operacional

Mitigação:
- tools têm guardrails server-side;
- confirmação server-side;
- segredo não retornado;
- allowed paths;
- break-glass off.

### T-005 — LLM escolhe target errado

Mitigação:
- inventory;
- discovery;
- tool semantic;
- confirmação;
- não inventar IDs.

### T-006 — mutação repetida após timeout

Mitigação:
- state verification before retry.

### T-007 — deploy ruim

Mitigação:
- dirty block;
- old SHA;
- health;
- rollback.

### T-008 — firewall/serviços de rede não auditados no host

Risco observado em 2026-09-19: firewall totalmente inativo (deixava toda porta em `0.0.0.0` acessível pela internet) e um proxy Tor SOCKS aberto (`0.0.0.0:9050`) com evidência real de abuso (~15 mil conexões).

Mitigação:
- `ufw` ativo por padrão, `default deny incoming`, revisar antes de liberar porta nova (`firewall_status`/`firewall_allow`);
- `infra_listening_ports` (`ss -tlnp`) para auditar o que está de fato escutando e em qual interface;
- serviços instalados mas não usados (ex.: WARP nunca configurado) devem ser desabilitados, não só ignorados;
- qualquer novo domínio/serviço exposto via Nginx deve ter autenticação na camada de gateway (X-API-Key ou equivalente), não só na aplicação.

### T-009 — path traversal em tools de arquivo

Risco corrigido em 2026-09-19 (achado de review automatizado): `assert_allowed_path` fazia checagem léxica por prefixo de string, então um caminho como `/opt/../etc/hostname` passava por começar com `/opt/`, mas o shell remoto resolvia fora da raiz permitida — explorável especialmente via `file_delete` (`sudo rm -rf`).

Mitigação:
- `assert_allowed_path` rejeita qualquer caminho com segmento `..`;
- `file_delete` adicionalmente resolve o caminho real via `realpath -m` no host remoto (segue symlinks) e revalida contra as raízes permitidas antes de montar o comando destrutivo.

---

## 18. Sudo

Estado atual conhecido:
infra-mcp possui sudo amplo NOPASSWD: ALL para homologação.

Isso é risco aceito temporariamente, não alvo ideal de produção.

Evolução recomendada:
- allowlist de systemctl;
- journalctl;
- nginx;
- apt;
- Docker necessário;
- comandos específicos.

A redução de sudo deve ser testada contra todas as tools.

---

## 19. Persistência e segredos

Arquivos ignorados:
- .env
- config/projects.yaml
- config/inventory.yaml
- secrets/
- data/

Git deve conter apenas exemplos sem valores secretos.

---

## 20. GitHub access

A VPS usa chave SSH dedicada para GitHub.

Objetivo:
evitar PAT em remote URLs.

Não documentar private key.

---

## 21. Estado de runtimes conhecidos

systemd ativos observados em 2026-09-19 (sessão 2):
- nginx
- omie-mcp
- stt-service (transcrição de áudio local, faster-whisper, para o pv360)
- telegram-claude (ponte Telegram <-> Claude/Fable 5)
- verticalparts-infra-mcp
- vpprd-mcp (MCP "vpprd-browser", porta 3100, ver §23 sobre exposição via mcp.vpsistema.com)
- whatsapp-mcp
- docker
- ssh

Desativados deliberadamente em 2026-09-19: `tor@default.service`, `tor.service`, `warp-svc.service` (ver RAG-009B / T-008). Removido: container `hermes-agent-god7` (não é serviço systemd, era Docker Compose — ver §22).

Categoria adicional descoberta em 2026-09-19: PM2 (`/root/.pm2`), sem processos ativos no momento da auditoria; `/opt/vp-bot` é um bot WhatsApp Node.js dormente que usaria essa categoria se reativado. `infra_pm2_list` cobre essa categoria agora.

Falha observada:
- privoxy.service failed

Regra:
registrar estado, não “consertar” serviço desconhecido sem entender necessidade.

---

## 22. Docker conhecido

Containers observados em 2026-09-19 (sessão 2), com detalhamento completo em `config/projects.yaml`:
- `vpclick-vpclick-1` — produção, ver §2.3B;
- `evolution-api` (+ `evolution-postgres`, `evolution-redis`) — backend WhatsApp da instância `pv360`/posvenda360;
- `n8n` — automação de workflows, parado (SIGTERM limpo, não crash; banco `n8n` existe e autentica normalmente — testado);
- `postgres`/`redis` do projeto `vp-infra` — compartilhados, usados pelo n8n;
- `traefik-traefik-1` — reverse proxy do template Hostinger; uso real limitado (sem porta mapeada ao host, nenhum outro serviço tem labels de roteamento);
- ~~`hermes-agent-god7`~~ — **removido em 2026-09-19** (agente de terminal do template Hostinger, não confundir com "Hermes AI Agent"/NousResearch; sem uso relevante, sem rota externa funcional). Backup em `/root/hermes-agent-god7-backup-*.tar.gz`.

Redes/volumes Docker órfãos do Supabase (`supabase_network_*`, ligados a `/opt/vprequisicoes/supabase/functions`) foram removidos por limpeza em 2026-09-19 — resíduo de `supabase functions serve`, sem containers ativos.

Regra específica:
não inferir que todo container stopped é lixo.
Preservar volumes usados por serviços ainda relevantes.
Antes de remover rede/volume, usar `docker_network_rm`/`docker_volume_rm` (recusam automaticamente se houver container anexado/referenciando).

---

## 23. Nginx

Domínios conhecidos na VPS podem incluir:
- infra-mcp.vpsistema.com
- mcp.vpsistema.com — `location /omie/` -> omie-mcp (127.0.0.1:8000); `location /` (catch-all) -> vpprd-mcp (127.0.0.1:3100), protegido por X-API-Key desde 2026-09-19
- whatsapp-mcp.vpsistema.com
- vpclick.vpsistema.com
- requisicoes.vpsistema.com
- configs legadas: `visitas` e `vpsistema.com` (este com `default_server`) servem estático local de `/var/www/verticalparts/VerticalParts_Fix/...` — confirmado existente em 2026-09-19, não removido, só documentado (produção real desses domínios é shared hosting).

DNS determina produção real em conjunto com inventory.

---

## 24. Shared hosting

A Hostinger API listou múltiplos websites.

Dois conceitos não podem ser confundidos:

website cadastrado/enabled:
recurso no plano Hostinger.

produção:
destino efetivo do DNS + runtime + health.

O inventory representa a decisão operacional reconciliada.

---

### 24.1 Homologação Shared Hosting — 2026-09-19

A API Hosting foi validada nos dois planos atualmente acessíveis.

Conta Cloud:
- 9 websites Node.js;
- todos com integração Git/auto-deploy Hostinger ativa;
- builds e commits podem ser observados semanticamente;
- VPRequisições foi validado com Node.js 22 e SSL ativo;
- VPClick aparece nessa superfície, mas deve ser tratado como registro legado porque produção canônica é Docker na VPS.

Conta Premium:
- 5 websites `other`;
- PHP 8.3.33 disponível para os cinco;
- nenhum com auto-deploy Git Hostinger;
- inspeção de arquivos mostrou mistura de estático e PHP/híbrido, então `other` não deve ser convertido automaticamente em `php`.

Após o deploy do código do Infrastructure MCP:
- service `verticalparts-infra-mcp.service` = active;
- `tools/list` local retornou 49 tools (sessão 1); **62 tools** após a expansão de 2026-09-19 sessão 2 (ver §21/RAG-009A2), validado end-to-end via `https://infra-mcp.vpsistema.com/mcp` real (401 sem chave, 200 com chave no `initialize`);
- `hostinger_ssl_status` foi executado pelo protocolo MCP real e retornou sucesso.


## 25. Failure modes

### FM-001 — service inactive
Use logs/status, depois restart.

### FM-002 — public 502
Nginx -> upstream -> process.

### FM-003 — public 401
Auth.

### FM-004 — MCP local OK, public fail
Gateway/TLS/auth.

### FM-005 — public OK, Claude fail
configuração Claude/session/account.

### FM-006 — Hostinger API fail
token/base/API/provider.

### FM-007 — SSH fail
host/user/key/known_hosts/network.

### FM-008 — inventory missing
reconstruct read-only, não inventar.

### FM-009 — shared hosting site down
não diagnosticar pela VPS.

### FM-010 — VPS reboot
MCP atual cai temporariamente por co-location.

---

## 26. Observabilidade

Obrigatório:
- service status;
- journal;
- audit;
- health;
- Hostinger metrics;
- infra_status;
- Git SHA;
- endpoint tests.

Recomendado futuro:
- uptime monitoring externo;
- alertas;
- central logs;
- SLOs.

---

## 27. Health design

Tipos:

systemd:
active state.

HTTP:
2xx/expected body.

MCP:
initialize + tools/list ou endpoint semantics.

Docker:
container state + healthcheck.

Functional:
consulta mínima de negócio.

Para componentes críticos, preferir mais de uma camada.

---

## 28. Drift detection

Drifts importantes:
- DNS != inventory;
- Website Hostinger != produção;
- Nginx stale;
- service registrado != existente;
- branch != expected;
- container != inventory.

Futura tool recomendada:
infra_detect_drift.

---

## 29. Arquitetura resiliente futura

Target:

~~~text
Claude
  |
External Control Host
  |
  +-> Hostinger API
  |
  +-> SSH -> VPS target
~~~

Benefícios:
- restart da VPS sem perder control plane;
- recuperação durante outage;
- separação de blast radius.

---

## 30. Autenticação futura

Atual:
X-API-Key no Nginx.

Evolução:
- OAuth;
- identity-aware proxy;
- secret manager;
- per-user authorization;
- key rotation sem downtime.

Até lá:
- API key forte;
- TLS;
- arquivos root-only;
- rotação.

---

## 31. Onboarding design contract

Todo novo recurso deve gerar quatro registros:

1. runtime real;
2. DNS/TLS;
3. projects.yaml se operável;
4. inventory.yaml.

Se qualquer um ficar faltando, a operação futura perde contexto.

---

## 32. Change management

Mudança deve ter:
- reason;
- target;
- pre-state;
- action;
- confirmation quando aplicável;
- post-state;
- rollback;
- docs/inventory update.

---

## 33. Compatibilidade MCP

O servidor usa FastMCP e Streamable HTTP.

Após upgrades de mcp package:
- reiniciar;
- initialize;
- tools/list;
- tools/call infra_inventory;
- teste Claude.

Pin de major version deve evitar upgrade surpresa.

---

## 34. Recovery priority

P0:
acesso ao control plane e inventário.

P1:
MCP público.

P2:
serviços de negócio críticos.

P3:
deploy/inventory consistency.

P4:
limpeza de legado.

Nunca limpar legado durante incidente antes de restaurar serviço.

---

## 35. Definition of healthy Infrastructure MCP

Healthy significa:
- systemd active;
- loopback MCP funciona;
- public HTTPS funciona;
- auth funciona;
- tools/list funciona;
- infra_inventory funciona;
- Hostinger API funciona;
- SSH funciona;
- audit gravável;
- break-glass off.

---

## 36. Referências

MCP/Claude:
https://support.claude.com/pt/articles/11175166-comece-com-conectores-personalizados-usando-mcp-remoto

Hostinger:
https://developers.hostinger.com/
https://www.hostinger.com/support/11079316-hostinger-api-mcp-server/
https://mcp.hostinger.com

Código:
src/verticalparts_infra_mcp/
