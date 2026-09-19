# 02 — SPEC — VerticalParts Infrastructure MCP

Versão: 2026-09-19
Status: canônico
Escopo: requisitos funcionais, não funcionais, contratos operacionais, onboarding de sites, recuperação e critérios de aceite.

---

## 1. Objetivo

O sistema deve permitir que uma LLM opere infraestrutura VerticalParts por intenção, sem exigir que o operador humano conheça comandos de Linux, APIs Hostinger, Nginx, Docker, Git ou detalhes de conexão MCP.

O sistema deve transformar pedidos como:

- “o site caiu”
- “publique esse projeto”
- “adicione este domínio”
- “reinicie o serviço”
- “Claude perdeu o MCP”
- “migre este site para a VPS”
- “veja o que está consumindo memória”
- “faça deploy”
- “troque uma variável”
- “recupere a VPS”

em planos de ação seguros, auditáveis, reversíveis e validados.

---

## 2. Escopo funcional

O MCP deve cobrir dois planos principais.

### 2.1 Hostinger Control Plane

Responsável por:
- descoberta de VPS;
- status;
- métricas;
- start;
- stop;
- restart;
- inventário de Websites;
- chamada de endpoints oficiais Hostinger ainda não encapsulados;
- evolução futura para DNS, backups, snapshots, firewall e outros recursos suportados pela API.

### 2.2 VPS Operations Plane

Responsável por:
- SSH;
- systemd;
- logs;
- Docker;
- Git;
- arquivos;
- variáveis de ambiente;
- Nginx;
- APT;
- deploy;
- health;
- inventário;
- auditoria.

---

## 3. Fora de escopo por padrão

O sistema não deve assumir autorização implícita para:

- apagar bancos;
- apagar volumes;
- recriar VPS;
- remover projetos;
- destruir snapshots/backups;
- executar shell arbitrário sem break-glass;
- converter arquitetura de projeto;
- mover projeto entre shared hosting e VPS sem decisão explícita;
- containerizar projeto automaticamente;
- expor segredos.

Essas operações exigem design/confirmacão específica.

---

## 4. Requisitos funcionais

### FR-001 — Descoberta do alvo

Antes de qualquer mutação, o MCP/LLM deve identificar:
- ambiente;
- domínio/projeto;
- runtime;
- serviço/container;
- host;
- branch;
- health esperado.

Critério de aceite:
nenhuma mutação deve depender de identificador inventado.

---

### FR-002 — Inventário operacional

Deve existir inventário privado carregável por infra_inventory.

O inventário deve distinguir:
- VPS;
- shared hosting;
- produção;
- redirect;
- legacy;
- migrated;
- aliases;
- runtime;
- service/container;
- observações.

Critério de aceite:
a LLM deve conseguir responder onde um domínio está efetivamente em produção sem depender apenas da API Websites.

---

### FR-003 — Registry de projetos

Projetos operáveis devem poder ser registrados em config/projects.yaml com:
- description;
- path;
- repo;
- branch;
- runtime;
- service/container;
- health;
- env_files.

Critério de aceite:
deploy_project deve recusar projeto inexistente.

---

### FR-004 — Leitura antes de escrita

Quando o efeito depender de estado atual, o sistema deve consultar estado primeiro.

Exemplos:
- service_status antes de restart;
- git_status antes de pull;
- nginx_test antes de reload;
- hostinger_vps_status antes de ciclo de vida.

---

### FR-005 — Tools semânticas

Operações recorrentes devem usar tools específicas.

Shell arbitrário é contingência, não fluxo normal.

Critério:
infra_exec_command deve permanecer indisponível enquanto INFRA_ALLOW_BREAK_GLASS=false.

---

### FR-006 — Hostinger VPS

Deve suportar:
- list;
- status;
- metrics;
- start;
- stop;
- restart.

Mutações exigem CONFIRMO.

---

### FR-007 — Hostinger Websites e Shared Hosting

Deve suportar semanticamente, em leitura:
- listagem de sites e planos;
- arquivos do document root;
- leitura segura de arquivo texto;
- status de auto-deploy Git;
- status SSL;
- bancos sem exposição de senha;
- cron jobs;
- settings Node.js;
- histórico de builds;
- build logs;
- runtime logs;
- nomes de variáveis de ambiente sem valores;
- vulnerabilidades Node.js.

Deve suportar restart do processo Node.js como operação CRITICAL, exigindo `CONFIRMO`.

A LLM deve entender que:
- site listado como enabled != prova de que DNS de produção aponta para ele;
- `website_type=other` não prova que a aplicação é PHP;
- integração Git Hostinger ativa não prova que esse ambiente seja a produção canônica;
- VPClick é o caso conhecido em que o registro Shared Hosting é legado e a produção está na VPS/Docker.

Leitura de arquivo deve bloquear caminhos inseguros e arquivos com alta probabilidade de conter segredo.
A listagem de env Node.js deve retornar apenas nomes de chaves; valores mascarados da API não devem ser propagados como valores reais.

---

### FR-008 — Fallback Hostinger

hostinger_api_call deve permitir endpoint oficial ainda não encapsulado.

Requisitos:
- method;
- path;
- body;
- classificação de risco;
- confirmação proporcional;
- auditoria;
- nenhum endpoint inventado.

---

### FR-009 — SSH seguro

O plano Linux deve:
- usar chave;
- usar known_hosts;
- usar usuário dedicado;
- evitar senha root;
- restringir caminhos;
- registrar mutações.

Estado atual conhecido:
usuário infra-mcp.

Meta de segurança:
sudo mínimo necessário.

---

### FR-010 — systemd

Deve suportar:
- status;
- logs;
- start;
- stop;
- restart.

Mutações exigem CONFIRMO.

Critério:
após restart, validar status e health externo quando houver.

---

### FR-011 — Docker

Deve suportar:
- ps;
- logs;
- restart;
- Compose ps/logs/pull/build/up/restart.

Regra arquitetural:
Docker não é destino default.

Estado conhecido:
VPClick é a aplicação intencionalmente em Docker.

---

### FR-012 — Git

Deve suportar:
- status;
- log;
- fetch;
- pull.

Política:
- fast-forward only;
- working tree limpa;
- sem reset destrutivo automático.

---

### FR-013 — Arquivos

Leitura/escrita apenas em raízes permitidas.

Escrita:
- confirmação;
- backup;
- auditoria.

Arquivos de segredo não devem ser expostos por file_read.

---

### FR-014 — Variáveis

Deve existir fluxo específico para env:
- listar apenas nomes/configured;
- set com backup;
- remove com backup;
- nunca retornar valor secreto.

---

### FR-015 — Nginx

nginx_reload deve ser condicionado a nginx_test válido.

Se test falhar:
- reload proibido;
- erro retornado.

---

### FR-016 — APT

Deve suportar:
- check;
- upgrade.

Upgrade:
- CONFIRMO;
- sem reboot automático.

Reboot é ação separada.

---

### FR-017 — Deploy declarativo

deploy_project deve:
1. resolver projeto;
2. validar repo/branch/path;
3. verificar working tree;
4. registrar old SHA;
5. fetch/update;
6. build;
7. restart;
8. health;
9. rollback em health failure quando configurado;
10. auditar.

---

### FR-018 — Health

Health deve ser funcional, não apenas “processo ativo”.

Pode incluir:
- HTTP;
- endpoint MCP;
- service state;
- container;
- porta.

Critério:
deploy não é considerado concluído sem health quando health está configurado.

---

### FR-019 — Auditoria

Toda mutação deve registrar:
- timestamp;
- tool;
- target;
- operação;
- outcome;
- exit/status;
- erro útil.

Nunca registrar:
- token;
- password;
- private key;
- API key;
- secret.

---

### FR-020 — Confirmações

Níveis:

READ:
sem confirmação.

CRITICAL:
CONFIRMO.

DESTRUCTIVE:
CONFIRMO_DESTRUTIVO.

BREAK_GLASS:
BREAK_GLASS + reason + flag habilitada.

---

### FR-021 — Diagnóstico antes de restart

A LLM deve classificar:
- sessão/cliente;
- auth;
- DNS;
- TLS;
- proxy;
- service;
- container;
- app;
- DB;
- dependency;
- resource pressure.

Restart só após evidência ou solicitação explícita devidamente confirmada.

---

### FR-022 — Timeout seguro

Após timeout de mutação:
- verificar estado;
- não repetir cegamente.

---

### FR-023 — Reconexão Claude

A documentação e o runbook devem permitir recriar conectores:

Infrastructure:
https://infra-mcp.vpsistema.com/mcp
Sem login
X-API-Key

WhatsApp:
https://whatsapp-mcp.vpsistema.com/mcp
Sem login
X-API-Key

Omie:
https://mcp.vpsistema.com/omie/mcp
configuração atual sem header adicional.

---

### FR-024 — Recuperação de chave sem versionamento

A documentação pode informar comandos de recuperação, nunca valores.

Infrastructure:
cat /root/infra-mcp-auth-token

WhatsApp:
cat /root/whatsapp-mcp-auth-token

---

### FR-025 — Claude Code

Deve ser possível usar MCPs remotos em Claude Code.

Deve permanecer separado o Omie local:
C:\Users\gelso\omie-mcp\omie-mcp-global.cmd

Falha do Omie local deve ser diagnosticada no Windows antes da VPS.

---

### FR-026 — Novo site: descoberta

Antes do onboarding, obter:
- nome;
- domínio;
- repo;
- branch;
- stack;
- build;
- start;
- porta;
- env;
- DB;
- storage;
- DNS;
- TLS;
- target;
- health;
- deploy strategy.

---

### FR-027 — Novo site: classificação

A LLM deve escolher explicitamente uma classe:

A. Hostinger shared hosting.
B. VPS com runtime nativo/systemd.
C. VPS estático/Nginx.
D. VPS Docker, somente se arquitetura exigir.

A escolha deve ser registrada.

---

### FR-028 — Novo site: shared hosting

Fluxo deve contemplar:
- criar/identificar website no Hostinger;
- publicar;
- configurar pipeline;
- DNS;
- env;
- health;
- inventário.

Não criar container na VPS apenas porque há Docker disponível.

---

### FR-029 — Novo site: VPS systemd

Fluxo deve contemplar:
- path;
- user;
- runtime;
- build;
- service unit;
- porta loopback;
- Nginx;
- TLS;
- DNS;
- health;
- projects.yaml;
- inventory.yaml.

---

### FR-030 — Novo site: VPS estático

Fluxo:
- build;
- diretório final;
- ownership;
- Nginx root;
- DNS;
- TLS;
- health;
- inventário.

---

### FR-031 — Novo site: Docker

Somente mediante decisão explícita.

Fluxo:
- image/compose;
- volumes;
- env;
- ports;
- health;
- restart policy;
- backup;
- Nginx;
- TLS;
- inventory.

---

### FR-032 — Migração

Migração deve:
1. manter origem ativa;
2. preparar target;
3. validar target;
4. executar cutover;
5. validar externo;
6. preservar rollback;
7. marcar origem como legacy/migrated;
8. atualizar inventory;
9. limpar somente depois.

---

### FR-033 — DNS como evidência

DNS deve ser consultado ao reconciliar produção.

Critério:
a LLM não deve classificar um domínio apenas com base em configuração Nginx ou API Websites.

---

### FR-034 — TLS

Todo endpoint público de produção deve ter:
- HTTPS;
- certificado válido;
- renovação administrável;
- hostname coerente.

---

### FR-035 — Segurança de MCP público

Porta interna não deve ser exposta diretamente.

Fluxo recomendado:
Internet -> HTTPS gateway/Nginx -> auth -> loopback MCP.

---

### FR-036 — 401 esperado

Para MCP com API key:
request sem chave pode responder 401.

Isso deve ser interpretado como:
endpoint possivelmente vivo, auth faltando.

Não classificar automaticamente como serviço indisponível.

---

### FR-037 — Rotação de API key

Rotação deve:
- gerar novo segredo;
- atualizar gateway;
- validar Nginx;
- atualizar clientes;
- testar;
- remover antigo;
- não versionar valor.

---

### FR-038 — Topologia documental

Mudança permanente em:
- domínio;
- runtime;
- ambiente;
- service;
- container;
- endpoint;
- auth;
- deploy;

deve gerar atualização de inventory e documentação.

---

### FR-039 — Fonte externa oficial

Quando API/cliente evoluir, consultar documentação oficial antes de codificar novos wrappers.

Hostinger:
https://developers.hostinger.com/

Anthropic:
https://support.claude.com/pt/articles/11175166-comece-com-conectores-personalizados-usando-mcp-remoto

---

### FR-040 — Degradação segura

Se inventário estiver ausente/corrompido:
- não inventar;
- operar apenas leitura segura;
- reconstruir a partir do estado vivo;
- validar antes de salvar.

---

### FR-041 — Firewall (adicionado 2026-09-19)

Deve suportar:
- status (leitura);
- allow;
- delete rule.

Mutações exigem CONFIRMO.

Critério de aceite: uma porta nova exposta por qualquer serviço deve poder ser auditada (`firewall_status`) e restringida sem depender de break-glass.

---

### FR-042 — Docker network/volume (adicionado 2026-09-19)

Deve suportar:
- listagem de redes e volumes (leitura);
- remoção de rede/volume.

Remoção exige CONFIRMO_DESTRUTIVO e deve recusar automaticamente quando ainda houver container anexado (rede) ou referenciando (volume) — a tool não deve depender só da confirmação humana para essa checagem de segurança.

`docker_compose_action` deve suportar a ação `down`, classificada como DESTRUCTIVE (diferente de pull/build/up/restart, que são CRITICAL).

---

### FR-043 — Observabilidade de host (adicionado 2026-09-19)

Deve suportar, em leitura:
- portas TCP em escuta e processo responsável;
- processos PM2 sob root (categoria de runtime separada de systemd/Docker);
- crontab do root e jobs de `/etc/cron.d` (schedule + comando, não só nome de arquivo).

`infra_pm2_list` nunca deve retornar `pm2_env.env` (variáveis de ambiente do processo) — segredos de app não podem vazar por uma tool de observabilidade.

---

### FR-044 — Remoção segura de arquivo/diretório (adicionado 2026-09-19)

`file_delete` deve:
1. recusar `.env`;
2. normalizar barra final;
3. resolver o caminho real no host remoto (`realpath -m`) e revalidar contra as raízes permitidas — não confiar só na checagem léxica local, que não enxerga symlinks;
4. fazer backup `.tar.gz` do alvo, como irmão fora da árvore sendo removida, antes de apagar;
5. exigir CONFIRMO_DESTRUTIVO.

---

## 5. Requisitos não funcionais

### NFR-001 — Segurança

Segredos fora do Git.
Least privilege como meta.
Break-glass off por padrão.

### NFR-002 — Auditabilidade

Toda mutação rastreável.

### NFR-003 — Reversibilidade

Toda mudança relevante deve ter rollback quando tecnicamente viável.

### NFR-004 — Resiliência

Control plane idealmente externo à VPS alvo.

### NFR-005 — Disponibilidade

Mutações devem minimizar downtime.

### NFR-006 — Determinismo

Mesma operação + mesmo estado -> mesma política de risco.

### NFR-007 — Observabilidade

Logs, health, status e inventário acessíveis.

### NFR-008 — Idempotência operacional

Retry de mutação só após verificar estado.

### NFR-009 — Portabilidade de LLM

Documentação deve ser suficiente para Claude, Claude Code ou outra LLM autorizada entender a arquitetura.

### NFR-010 — Atualização documental

Mudanças estruturais não podem ficar apenas “na memória do chat”.

### NFR-011 — Compatibilidade

MCP remoto deve manter transporte compatível com clientes autorizados.

### NFR-012 — Privacidade

O modelo deve receber somente o mínimo necessário de dados operacionais.

---

## 6. Contrato de inventário

Estrutura mínima recomendada:

~~~yaml
version: 1

environments:
  vps:
    provider: hostinger
    role: production
    vm_id: "..."
    hostname: "..."
    ipv4: "..."

  shared_hosting:
    provider: hostinger
    role: production

domains:
  app.exemplo.com:
    environment: vps
    status: production
    runtime: systemd
    service: app.service

aliases:
  antigo.exemplo.com: app.exemplo.com
~~~

Campos adicionais podem incluir:
- repo;
- branch;
- container;
- website_type;
- source_of_truth;
- notes;
- migrated_from;
- health;
- deploy_mode.

---

## 7. Contrato de projetos

Exemplo:

~~~yaml
projects:
  app:
    description: "Aplicação X"
    path: "/opt/app"
    repo: "git@github.com:org/repo.git"
    branch: "main"
    runtime:
      type: systemd
      service: "app.service"
    health:
      url: "https://app.exemplo.com/health"
      mode: "http"
    env_files:
      - ".env"
~~~

A LLM não deve preencher placeholders sem descoberta.

---

## 8. Contrato de conexão Claude

### Infrastructure

Name:
VerticalParts Infrastructure

URL:
https://infra-mcp.vpsistema.com/mcp

Auth:
Sem login

Header:
X-API-Key

### WhatsApp

Name:
VerticalParts WhatsApp

URL:
https://whatsapp-mcp.vpsistema.com/mcp

Auth:
Sem login

Header:
X-API-Key

### Omie

Name:
VerticalParts Omie

URL:
https://mcp.vpsistema.com/omie/mcp

Auth atual:
sem header adicional.

---

## 9. Critérios de aceite do MCP

O sistema é considerado operacional quando:

1. service ativo;
2. loopback responde MCP initialize;
3. tools/list retorna catálogo esperado;
4. infra_inventory responde;
5. endpoint público sem chave retorna auth failure esperado;
6. endpoint público com chave válida aceita MCP;
7. Claude enxerga tools;
8. Hostinger API funciona;
9. SSH funciona;
10. auditoria grava mutações;
11. break-glass continua off;
12. segredos não aparecem em output.

---

## 10. Critérios de aceite de novo site

Um site só está “no ar” quando:

1. deploy concluído;
2. runtime saudável;
3. DNS correto;
4. HTTPS válido;
5. URL externa responde;
6. health funcional;
7. env/dependências validadas;
8. inventory atualizado;
9. projects atualizado quando aplicável;
10. rollback conhecido;
11. nenhuma credencial foi versionada.

---

## 11. Critérios de aceite de migração

1. target novo validado;
2. origem preservada até cutover;
3. DNS alterado conscientemente;
4. TLS funcional;
5. health externo OK;
6. rollback disponível durante janela;
7. inventory atualizado;
8. origem marcada legacy/migrated;
9. artefato antigo não removido prematuramente.

---

## 12. Critérios de aceite de recuperação MCP

1. DNS resolve corretamente;
2. TLS válido;
3. Nginx config válida;
4. upstream local ativo;
5. initialize MCP funciona;
6. tools/list funciona;
7. auth pública funciona;
8. Claude reconecta;
9. tool de leitura executa;
10. segredo não foi exposto.

---

## 13. Casos de teste obrigatórios

TC-001:
Claude consulta infra_inventory.

TC-002:
request público sem API key retorna 401 para Infrastructure.

TC-003:
request público autenticado inicializa MCP.

TC-004:
tools/list contém infra_inventory.

TC-005:
service_status funciona.

TC-006:
restart exige confirmação.

TC-007:
env_list_keys não mostra valores.

TC-008:
file_read bloqueia env.

TC-009:
nginx_reload não ocorre se nginx_test falhar.

TC-010:
deploy recusa working tree suja.

TC-011:
deploy com health failure realiza rollback quando configurado.

TC-012:
break-glass recusa enquanto flag false.

TC-013:
hostinger_list_websites retorna sites.

TC-014:
VPClick é classificado como VPS apesar do cadastro legado no shared hosting.

TC-015:
VPRequisições é classificado como shared hosting.

TC-016:
Omie local não causa restart da VPS em CONNECT_TIMEOUT.

TC-017:
novo site exige classificação de ambiente.

TC-018:
Docker não é escolhido automaticamente.

---

## 14. Evolução prioritária

P1:
- tool semântica de DNS;
- health orchestration;
- diagnóstico 502/504;
- rotação controlada de API key;
- export de inventory validado;
- detecção de drift DNS vs inventory.

P2:
- backups/snapshots;
- ~~firewall~~ (implementado em 2026-09-19: `firewall_status/allow/delete_rule`);
- certificados;
- disk maintenance;
- log rotation;
- DB health.

P3:
- mover control plane para host independente;
- autenticação OAuth/identity gateway;
- secrets manager;
- sudo granular.

---

## 15. Definition of Done

Qualquer feature do Infrastructure MCP só está concluída quando:

- implementada;
- classificada por risco;
- auditada;
- testada;
- documentada;
- sem segredo no Git;
- com rollback quando necessário;
- incorporada ao RAG/Instruction se alterar comportamento;
- incorporada ao inventory se alterar topologia.
