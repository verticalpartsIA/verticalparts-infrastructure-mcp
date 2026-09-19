# VerticalParts Infrastructure MCP

MCP corporativo para administração, recuperação e evolução da infraestrutura VerticalParts por LLMs.

Endpoint remoto atual:

https://infra-mcp.vpsistema.com/mcp

O projeto combina:

1. Hostinger Control Plane
   - VPS;
   - Websites/shared hosting;
   - métricas;
   - lifecycle;
   - fallback para endpoints oficiais Hostinger.

2. VPS Operations Plane
   - SSH;
   - systemd;
   - Docker;
   - Git;
   - arquivos;
   - env;
   - Nginx;
   - APT;
   - deploy;
   - health;
   - auditoria.

3. Operational Knowledge Plane
   - inventário;
   - registry de projetos;
   - RAG;
   - SPEC;
   - Instructions;
   - SDD;
   - runbook de recovery/onboarding.

---

## Leia primeiro

A documentação canônica está na raiz, em ordem:

1. [00_READ_FIRST_INFRASTRUCTURE_MCP.md](./00_READ_FIRST_INFRASTRUCTURE_MCP.md)
2. [03_INSTRUCTIONS_LLM_MCP_INFRASTRUCTURE_VERTICALPARTS.md](./03_INSTRUCTIONS_LLM_MCP_INFRASTRUCTURE_VERTICALPARTS.md)
3. [01_RAG_MCP_INFRASTRUCTURE_VERTICALPARTS.md](./01_RAG_MCP_INFRASTRUCTURE_VERTICALPARTS.md)
4. [02_SPEC_MCP_INFRASTRUCTURE_VERTICALPARTS.md](./02_SPEC_MCP_INFRASTRUCTURE_VERTICALPARTS.md)
5. [04_SDD_MCP_INFRASTRUCTURE_VERTICALPARTS.md](./04_SDD_MCP_INFRASTRUCTURE_VERTICALPARTS.md)
6. [05_RUNBOOK_COPY_PASTE_RECOVERY_AND_ONBOARDING.md](./05_RUNBOOK_COPY_PASTE_RECOVERY_AND_ONBOARDING.md)

O runbook contém comandos de copy/paste para:
- reconectar Claude;
- recuperar tokens sem versioná-los;
- diagnosticar MCP;
- atualizar o próprio servidor;
- DNS/TLS/Nginx;
- systemd;
- Docker;
- Git;
- Hostinger;
- onboarding de novo site;
- migração shared hosting <-> VPS;
- reconstrução de inventário.

---

## Regra central

A LLM deve operar por estado, não por suposição.

Hierarquia de verdade:

1. estado vivo;
2. config/inventory.yaml;
3. config/projects.yaml;
4. código;
5. documentação canônica;
6. documentação histórica;
7. memória.

Cadastro de um website na Hostinger não prova que ele recebe tráfego de produção. Produção é determinada por DNS + runtime + health + inventário reconciliado.

---

## Estado operacional conhecido em 2026-09-19

Infrastructure MCP:
- serviço: verticalparts-infra-mcp.service
- bind: 127.0.0.1:8020
- instalação: /opt/verticalparts-infrastructure-mcp
- autenticação pública: X-API-Key
- transporte: Streamable HTTP

VPS:
- Hostinger VM ID: 1510643
- hostname: srv1510643.hstgr.cloud
- IPv4: 72.61.48.156

Arquitetura atual:
o Infrastructure MCP ainda roda na VPS que administra. Isso funciona, mas uma arquitetura de recuperação total futura deve mover o control plane para outro host.

---

## Domínios

A fonte autoritativa operacional é infra_inventory.

Snapshot atual:

VPS:
- infra-mcp.vpsistema.com
- mcp.vpsistema.com
- whatsapp-mcp.vpsistema.com
- vpclick.vpsistema.com

Shared hosting:
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

Legacy redirect:
- requisicoes.vpsistema.com -> vprequisicoes.vpsistema.com

VPClick foi migrado do shared hosting para VPS. O cadastro antigo no shared hosting pode continuar existindo.

Homologação do Shared Hosting em 2026-09-19:
- 9 websites Node.js na conta Cloud com auto-deploy Git ativo;
- 5 websites `other` na conta Premium sem auto-deploy Git Hostinger;
- PHP 8.3.33 está disponível para os cinco `other`, mas a classificação real deve considerar os arquivos/runtime;
- `hostinger_ssl_status` foi validada pelo protocolo MCP real contra VPRequisições;
- o catálogo carregado após restart contém 49 tools (sessão 1); **62 tools** após a auditoria de segurança da sessão 2 (firewall, docker network/volume, service enable/disable, pm2, cron, remoção segura de arquivo).

---

## Regra Docker

Docker não é destino default.

VPClick é a aplicação atualmente intencionalmente em Docker na VPS.

Novo site deve ser classificado como:
- shared hosting;
- VPS systemd/runtime nativo;
- VPS estático;
- Docker apenas se a arquitetura exigir.

VPRequisições está no shared hosting.

---

## Tools

O servidor homologado em 2026-09-19 expõe **62 tools** (49 da homologação inicial + 13 adicionadas na auditoria de segurança da mesma data), incluindo:

Firewall (novo):
- firewall_status / firewall_allow / firewall_delete_rule

Docker (expandido):
- docker_network_ls / docker_volume_ls / docker_network_rm / docker_volume_rm
- docker_compose_action agora também suporta a ação `down`

systemd (expandido):
- service_enable / service_disable

Observabilidade de host (novo):
- infra_listening_ports (portas em escuta)
- infra_pm2_list (processos PM2, sem variáveis de ambiente)
- infra_cron_list (crontab root + /etc/cron.d)

Arquivos (expandido):
- file_delete (remoção com backup automático)

Catálogo original (49 tools):

Inventário:
- infra_status
- infra_list_projects
- infra_inventory

Hostinger:
- VPS list/status/metrics/start/stop/restart
- Shared Hosting: orders/websites
- files + safe file read
- Git auto-deploy status
- SSL status
- databases + cron jobs
- Node.js settings/builds/build logs/runtime logs
- env key names only
- Node.js vulnerabilities
- controlled Node.js restart
- hostinger_api_call as fallback

Linux:
- systemd status/logs/start/stop/restart
- Docker ps/logs/restart/compose
- Git status/log/fetch/pull
- file read/write
- env list/set/remove
- Nginx test/reload
- APT check/upgrade
- deploy_project
- infra_exec_command

Consulte o código e o RAG para catálogo completo e política de risco.

---

## Segurança

Nunca versionar:
- HOSTINGER_API_TOKEN;
- X-API-Keys;
- chaves SSH privadas;
- PATs GitHub;
- passwords;
- env values;
- service-role keys.

Arquivos reais ignorados:
- .env
- config/projects.yaml
- config/inventory.yaml
- secrets/
- data/

Confirmações:
- CONFIRMO — crítico;
- CONFIRMO_DESTRUTIVO — destrutivo;
- BREAK_GLASS — shell arbitrário com flag habilitada.

Break-glass deve permanecer desligado normalmente. Quando habilitado, roda como usuário `infra-mcp` com `sudo NOPASSWD: ALL` — é root irrestrito, não só Docker.

Firewall (`ufw`) desde 2026-09-19: ativo, `default deny incoming`, liberado apenas 22/80/443. Tor e Cloudflare WARP foram desativados no mesmo dia por falta de uso comprovado (Tor tinha evidência real de abuso como proxy aberto). Ver `00_READ_FIRST_INFRASTRUCTURE_MCP.md` seção 4B para detalhes.

---

## Desenvolvimento

~~~bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
cp .env.example .env
cp config/projects.example.yaml config/projects.yaml
cp config/inventory.example.yaml config/inventory.yaml
verticalparts-infra-mcp
~~~

Servidor remoto:

~~~env
MCP_TRANSPORT=streamable-http
MCP_HOST=127.0.0.1
MCP_PORT=8020
~~~

---

## Claude

Conector Infrastructure:

Nome:
VerticalParts Infrastructure

URL:
https://infra-mcp.vpsistema.com/mcp

Autenticação:
Sem login

Header:
X-API-Key

O valor nunca deve entrar neste repositório. O runbook descreve como recuperá-lo no host autorizado.

---

## Novo site

Não basta fazer deploy.

Definition of Done:
- target escolhido;
- runtime saudável;
- DNS;
- TLS;
- health externo;
- deploy conhecido;
- rollback;
- inventory atualizado;
- projects atualizado quando aplicável;
- sem segredo no Git.

Use 05_RUNBOOK_COPY_PASTE_RECOVERY_AND_ONBOARDING.md.

---

## Referências oficiais

Anthropic:
https://support.claude.com/pt/articles/11175166-comece-com-conectores-personalizados-usando-mcp-remoto

Hostinger API:
https://developers.hostinger.com/

Hostinger MCP:
https://www.hostinger.com/support/11079316-hostinger-api-mcp-server/

Hostinger Remote MCP:
https://mcp.hostinger.com

---

## Reconciliação pós-auditoria

Em 2026-09-19 foram atualizados também os documentos complementares antigos (`CLAUDE.md`, `docs/*`, espelho `rag/*` e exemplos de configuração) para remover conclusões superadas pela auditoria real.

Entre as correções:
- Shared Hosting Hostinger possui API útil para arquivos, Node.js, Git auto-deploy, SSL, bancos e cron;
- o catálogo tinha 49 tools nessa primeira reconciliação (uma segunda auditoria no mesmo dia elevou para 62 — ver seção "Tools" acima e `00_READ_FIRST_INFRASTRUCTURE_MCP.md` seção 4B);
- Docker do VPClick está corrigido/homologado via sudo e erro de socket futuro é regressão;
- o registro Hostinger do VPClick é legado, não produção;
- `website_type=other` não equivale automaticamente a PHP;
- associações de repositório sem evidência foram removidas dos exemplos.

## Princípio final

Este repositório é tanto software quanto manual de continuidade operacional.

Uma LLM autorizada deve conseguir, apenas lendo-o e usando leitura segura:
- reconstruir a topologia;
- detectar drift;
- recuperar conexão MCP;
- recuperar um serviço;
- conectar Claude novamente;
- publicar um novo site;
- migrar ambiente;
- atualizar inventário;
- operar sem expor segredos.
