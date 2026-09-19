# 05 — RUNBOOK COPY/PASTE — Recovery, Connection and Site Onboarding

Versão: 2026-09-19
Status: canônico
Objetivo: permitir reconstrução operacional por uma LLM ou humano autorizado sem depender de memória.

IMPORTANTE:
- comandos abaixo não contêm segredos;
- alguns comandos exibem segredos no terminal autorizado;
- nunca cole o resultado secreto em chat, issue ou Git;
- confirme o target antes de executar mutações.

---

# PARTE A — REFERÊNCIA RÁPIDA

Infrastructure MCP:
https://infra-mcp.vpsistema.com/mcp

WhatsApp MCP:
https://whatsapp-mcp.vpsistema.com/mcp

Omie MCP:
https://mcp.vpsistema.com/omie/mcp

VPS atual:
72.61.48.156

VM ID:
1510643

Infrastructure service:
verticalparts-infra-mcp.service

Install path:
/opt/verticalparts-infrastructure-mcp

Internal port:
8020

Infrastructure auth token file:
/root/infra-mcp-auth-token

WhatsApp auth token file:
/root/whatsapp-mcp-auth-token

---

# PARTE B — TESTE RÁPIDO DO INFRASTRUCTURE MCP

## B1. Ver serviço

~~~bash
systemctl is-active verticalparts-infra-mcp.service
~~~

Esperado:

active

## B2. Ver status completo

~~~bash
systemctl --no-pager --full status verticalparts-infra-mcp.service
~~~

## B3. Ver logs

~~~bash
journalctl -u verticalparts-infra-mcp.service -n 200 --no-pager
~~~

## B4. Confirmar porta local

~~~bash
ss -ltnp | grep ':8020'
~~~

## B5. Testar endpoint público sem chave

~~~bash
curl -i https://infra-mcp.vpsistema.com/mcp
~~~

Esperado:
401 ou resposta de autenticação equivalente.

401 aqui significa que o gateway pode estar vivo e protegendo corretamente.

## B6. Obter token sem registrar no Git

~~~bash
cat /root/infra-mcp-auth-token
~~~

Copie apenas para o campo seguro necessário. Não cole em conversa.

## B7. Carregar token em variável temporária no shell

~~~bash
INFRA_TOKEN="$(cat /root/infra-mcp-auth-token)"
~~~

## B8. Initialize local MCP

~~~bash
H=$(mktemp); curl -sS -D "$H" -o /tmp/infra-init.out -X POST http://127.0.0.1:8020/mcp -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' --data '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"runbook-check","version":"1.0"}}}'; cat /tmp/infra-init.out; rm -f "$H" /tmp/infra-init.out
~~~

## B9. Verificar infra_inventory no source carregado

~~~bash
grep -n "infra_inventory" /opt/verticalparts-infrastructure-mcp/src/verticalparts_infra_mcp/server.py
~~~

## B10. Testar tools/list local e procurar infra_inventory

~~~bash
H=$(mktemp); curl -sS -D "$H" -o /tmp/infra-init.out -X POST http://127.0.0.1:8020/mcp -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' --data '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"runbook-check","version":"1.0"}}}'; SID=$(awk 'BEGIN{IGNORECASE=1} /^mcp-session-id:/{gsub("\r","",$2); print $2}' "$H"); curl -sS -X POST http://127.0.0.1:8020/mcp -H "Mcp-Session-Id: $SID" -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' --data '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' | grep -o 'infra_inventory' | head -1; rm -f "$H" /tmp/infra-init.out
~~~

Esperado:

infra_inventory

## B11. Limpar variável de token

~~~bash
unset INFRA_TOKEN
~~~

---

# PARTE C — SE O CLAUDE NÃO CONECTAR

## C1. Confirme a URL

Infrastructure:

https://infra-mcp.vpsistema.com/mcp

Não usar:
- http
- porta 8020 pública
- URL sem /mcp

## C2. Confirme DNS

~~~bash
dig +short infra-mcp.vpsistema.com A
~~~

Esperado no estado atual:

72.61.48.156

## C3. Confirme TLS

~~~bash
curl -Iv https://infra-mcp.vpsistema.com/mcp
~~~

## C4. Confirme Nginx

~~~bash
nginx -t
~~~

## C5. Confirme config ativa

~~~bash
grep -R "infra-mcp.vpsistema.com" /etc/nginx/sites-enabled /etc/nginx/sites-available 2>/dev/null
~~~

## C6. Confirme upstream

~~~bash
curl -i http://127.0.0.1:8020/mcp
~~~

Sem MCP payload pode retornar erro de método/protocolo; o objetivo é verificar que há processo respondendo.

## C7. Se local funciona e público não

Investigar:
- Nginx;
- TLS;
- auth;
- firewall;
- DNS.

Não reiniciar VPS primeiro.

## C8. Se público funciona e Claude não

Revisar no Claude:
- conector habilitado;
- URL;
- Sem login;
- header X-API-Key;
- valor atual;
- permissões de tools.

Se necessário, remover e recriar o custom connector com os dados canônicos.

---

# PARTE D — COMO CONECTAR NO CLAUDE WEB/DESKTOP

## D1. Infrastructure

Nome:

VerticalParts Infrastructure

URL:

https://infra-mcp.vpsistema.com/mcp

Autenticação:

Sem login

Header:

X-API-Key

Para obter valor na VPS:

~~~bash
cat /root/infra-mcp-auth-token
~~~

Teste no Claude:

~~~text
Use o conector VerticalParts Infrastructure.
Consulte infra_inventory e informe os domínios em VPS e shared hosting.
Não faça alterações.
~~~

## D2. WhatsApp

Nome:

VerticalParts WhatsApp

URL:

https://whatsapp-mcp.vpsistema.com/mcp

Autenticação:

Sem login

Header:

X-API-Key

Valor:

~~~bash
cat /root/whatsapp-mcp-auth-token
~~~

Teste:

~~~text
Use o conector VerticalParts WhatsApp e consulte somente o status.
Não envie mensagens.
~~~

## D3. Omie

Nome:

VerticalParts Omie

URL:

https://mcp.vpsistema.com/omie/mcp

Configuração atual:
Sem login e sem header adicional.

Teste:
consulta somente leitura.

---

# PARTE E — CLAUDE CODE REMOTO

Antes:

~~~powershell
claude mcp list
~~~

## E1. Omie remoto

~~~powershell
claude mcp add --transport http --scope user verticalparts-omie https://mcp.vpsistema.com/omie/mcp
~~~

Verificar:

~~~powershell
claude mcp get verticalparts-omie
~~~

## E2. WhatsApp remoto

Obter token via SSH em variável temporária:

~~~powershell
$WHATSAPP_MCP_TOKEN = ssh root@72.61.48.156 "cat /root/whatsapp-mcp-auth-token"
~~~

Adicionar:

~~~powershell
claude mcp add --transport http --scope user verticalparts-whatsapp https://whatsapp-mcp.vpsistema.com/mcp --header "X-API-Key: $WHATSAPP_MCP_TOKEN"
~~~

Limpar variável:

~~~powershell
Remove-Variable WHATSAPP_MCP_TOKEN
~~~

## E3. Infrastructure remoto

~~~powershell
$INFRA_MCP_TOKEN = ssh root@72.61.48.156 "cat /root/infra-mcp-auth-token"
~~~

~~~powershell
claude mcp add --transport http --scope user verticalparts-infrastructure https://infra-mcp.vpsistema.com/mcp --header "X-API-Key: $INFRA_MCP_TOKEN"
~~~

~~~powershell
Remove-Variable INFRA_MCP_TOKEN
~~~

Verificar:

~~~powershell
claude mcp get verticalparts-infrastructure
~~~

OBSERVAÇÃO:
dependendo da versão do Claude Code, configuração de header pode ser persistida no config local. Trate esse config como sensível.

---

# PARTE F — OMIE LOCAL NO CLAUDE CODE

Launcher:

C:\Users\gelso\omie-mcp\omie-mcp-global.cmd

Adicionar:

~~~powershell
claude mcp add omie-verticalparts --scope user -- cmd /c "C:\Users\gelso\omie-mcp\omie-mcp-global.cmd"
~~~

Verificar:

~~~powershell
claude mcp list
~~~

Se CONNECT_TIMEOUT:
1. reiniciar sessão Claude Code;
2. claude mcp list;
3. verificar processo local;
4. investigar launcher;
5. não reiniciar VPS automaticamente.

---

# PARTE G — ATUALIZAR O PRÓPRIO INFRASTRUCTURE MCP

## G1. Ver branch/status

~~~bash
git -C /opt/verticalparts-infrastructure-mcp status --short --branch
~~~

## G2. Fetch

~~~bash
git -C /opt/verticalparts-infrastructure-mcp fetch --all --prune
~~~

## G3. Pull seguro

~~~bash
git -C /opt/verticalparts-infrastructure-mcp pull --ff-only origin main
~~~

Se houver working tree suja:
PARE. Não faça reset hard automaticamente.

## G4. Se pyproject mudou, atualizar dependências

~~~bash
cd /opt/verticalparts-infrastructure-mcp && .venv/bin/pip install -e .
~~~

## G5. Reiniciar

~~~bash
systemctl restart verticalparts-infra-mcp.service
~~~

## G6. Verificar

~~~bash
systemctl is-active verticalparts-infra-mcp.service
~~~

## G7. Validar tools/list

Use B10.

## G8. Validar inventory YAML

~~~bash
cd /opt/verticalparts-infrastructure-mcp && .venv/bin/python -c "import yaml; p='config/inventory.yaml'; d=yaml.safe_load(open(p)); print('INVENTARIO_OK', len(d.get('domains', {})), 'dominios')"
~~~

---

# PARTE H — INVENTÁRIO

Arquivo real:

/opt/verticalparts-infrastructure-mcp/config/inventory.yaml

Não versionado.

## H1. Ler inventário

~~~bash
cat /opt/verticalparts-infrastructure-mcp/config/inventory.yaml
~~~

Não deve conter segredos.

## H2. Validar sintaxe

~~~bash
cd /opt/verticalparts-infrastructure-mcp && .venv/bin/python -c "import yaml; yaml.safe_load(open('config/inventory.yaml')); print('YAML_OK')"
~~~

## H3. Antes de editar

~~~bash
cp /opt/verticalparts-infrastructure-mcp/config/inventory.yaml /opt/verticalparts-infrastructure-mcp/config/inventory.yaml.bak
~~~

## H4. Regra de atualização

Adicionar domínio com:
- environment;
- status;
- runtime/service/container quando aplicável;
- alias/migration notes;
- sem credenciais.

---

# PARTE I — PROJECT REGISTRY

Arquivo real:

/opt/verticalparts-infrastructure-mcp/config/projects.yaml

## I1. Ver

~~~bash
cat /opt/verticalparts-infrastructure-mcp/config/projects.yaml
~~~

## I2. Backup

~~~bash
cp /opt/verticalparts-infrastructure-mcp/config/projects.yaml /opt/verticalparts-infrastructure-mcp/config/projects.yaml.bak
~~~

## I3. Validar YAML

~~~bash
cd /opt/verticalparts-infrastructure-mcp && .venv/bin/python -c "import yaml; yaml.safe_load(open('config/projects.yaml')); print('PROJECTS_YAML_OK')"
~~~

---

# PARTE J — DIAGNÓSTICO DE SERVIÇO SYSTEMD

Substitua SERVICO.

## J1. Status

~~~bash
systemctl --no-pager --full status SERVICO
~~~

## J2. Logs

~~~bash
journalctl -u SERVICO -n 200 --no-pager
~~~

## J3. Restart

Operação crítica. Só após confirmação.

~~~bash
systemctl restart SERVICO
~~~

## J4. Confirmar

~~~bash
systemctl is-active SERVICO
~~~

Depois testar health público.

---

# PARTE K — DIAGNÓSTICO NGINX

## K1. Test

~~~bash
nginx -t
~~~

## K2. Listar sites

~~~bash
ls -la /etc/nginx/sites-enabled /etc/nginx/sites-available
~~~

## K3. Localizar domínio

~~~bash
grep -R "server_name" /etc/nginx/sites-available 2>/dev/null
~~~

## K4. Reload

Somente se nginx -t passou.

~~~bash
systemctl reload nginx
~~~

---

# PARTE L — DNS

## L1. Resolver A

~~~bash
dig +short DOMINIO A
~~~

## L2. Resolver CNAME

~~~bash
dig +short DOMINIO CNAME
~~~

## L3. Ver resolução completa

~~~bash
dig DOMINIO
~~~

Não classificar ambiente por configuração local sem consultar DNS.

---

# PARTE M — TLS

## M1. Ver certificado

~~~bash
openssl s_client -connect DOMINIO:443 -servername DOMINIO </dev/null 2>/dev/null | openssl x509 -noout -subject -issuer -dates
~~~

## M2. Testar HTTPS

~~~bash
curl -I https://DOMINIO/
~~~

Para VPS com Certbot, antes de emitir certificado confirme DNS.

---

# PARTE N — DOCKER

Regra:
Docker não é default.

## N1. Containers

~~~bash
docker ps -a
~~~

## N2. Logs

~~~bash
docker logs --tail 200 CONTAINER
~~~

## N3. Restart

Crítico.

~~~bash
docker restart CONTAINER
~~~

Não usar docker system prune, volume prune ou remoção agressiva sem inventário e autorização destrutiva.

---

# PARTE O — GIT

## O1. Status

~~~bash
git -C CAMINHO status --short --branch
~~~

## O2. SHA

~~~bash
git -C CAMINHO rev-parse HEAD
~~~

## O3. Remote

~~~bash
git -C CAMINHO remote -v
~~~

## O4. Fetch

~~~bash
git -C CAMINHO fetch --all --prune
~~~

## O5. Pull

~~~bash
git -C CAMINHO pull --ff-only
~~~

Não usar reset --hard automaticamente.

---

# PARTE P — HOSTINGER

Preferir tools MCP:
- hostinger_list_vps
- hostinger_list_websites
- hostinger_vps_status
- hostinger_vps_metrics

Para endpoint novo:
- verificar https://developers.hostinger.com/
- usar hostinger_api_call apenas com path oficial.

Não expor HOSTINGER_API_TOKEN.

---

# PARTE Q — NOVO SITE: CHECKLIST DE DESCOBERTA

Antes de qualquer comando, preencher:

Nome:
DOMÍNIO:
REPO:
BRANCH:
STACK:
BUILD:
START:
PORTA:
ENV:
BANCO:
STORAGE:
HEALTH:
DESTINO DESEJADO:
DEPLOY MODE:
DOWNTIME ACEITÁVEL:
ROLLBACK:

Se destino não foi definido, classificar.

---

# PARTE R — NOVO SITE NO SHARED HOSTING

Use esta rota se stack for compatível e houver decisão por shared hosting.

## R1. Descobrir websites atuais

Via MCP:
hostinger_list_websites

Ou via código/Hostinger API se necessário.

## R2. Verificar se domínio já existe

Não criar duplicado sem entender estado atual.

## R3. Configurar deploy

Pode ser:
- GitHub Actions;
- integração Hostinger;
- upload/build;
- pipeline existente.

Preservar mecanismo já usado pelo projeto.

## R4. Configurar env no ambiente de hosting

Nunca versionar valores.

## R5. DNS

Apontar conforme instrução oficial do hosting.

## R6. TLS

Validar HTTPS.

## R7. Health

~~~bash
curl -I https://NOVODOMINIO/
~~~

## R8. Inventory

Registrar:
environment: shared_hosting
status: production
website_type: ...
notes quando necessário.

## R9. Projects

Se o Infrastructure MCP não opera diretamente o filesystem do shared hosting, projects.yaml pode registrar apenas o que o deploy engine realmente suporta. Não inventar controle inexistente.

---

# PARTE S — NOVO SITE NA VPS COM SYSTEMD

Exemplo genérico. Ajustar stack.

## S1. Criar diretório

~~~bash
mkdir -p /opt/NOME
~~~

Antes de usar /opt, confirmar política e ownership desejado.

## S2. Clonar repo

~~~bash
git clone REPO /opt/NOME
~~~

## S3. Checkout branch

~~~bash
git -C /opt/NOME checkout BRANCH
~~~

## S4. Instalar dependências/build

Stack-specific. Não inventar.

Node exemplo:
~~~bash
cd /opt/NOME && npm ci
~~~

~~~bash
cd /opt/NOME && npm run build
~~~

Python exemplo:
~~~bash
cd /opt/NOME && python3 -m venv .venv
~~~

~~~bash
cd /opt/NOME && .venv/bin/pip install -r requirements.txt
~~~

## S5. Criar env seguro

Não incluir valores no Git.

Permissão recomendada:
~~~bash
chmod 600 /opt/NOME/.env
~~~

## S6. Criar service unit

Modelo:

~~~ini
[Unit]
Description=NOME
After=network.target

[Service]
Type=simple
User=USUARIO
WorkingDirectory=/opt/NOME
EnvironmentFile=/opt/NOME/.env
ExecStart=COMANDO_START
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
~~~

## S7. Validar systemd

~~~bash
systemctl daemon-reload
~~~

~~~bash
systemctl enable --now NOME.service
~~~

~~~bash
systemctl status NOME.service
~~~

## S8. Bind

Preferir app ouvindo em:
127.0.0.1:PORTA

## S9. Nginx

Modelo:

~~~nginx
server {
    listen 80;
    server_name NOVODOMINIO;

    location / {
        proxy_pass http://127.0.0.1:PORTA;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
~~~

## S10. Testar

~~~bash
nginx -t
~~~

## S11. Reload

~~~bash
systemctl reload nginx
~~~

## S12. DNS

Criar A para o target atual da VPS.

No estado atual:
72.61.48.156

Mas antes de usar esse IP em futuro onboarding, confirmar Hostinger/inventory.

## S13. TLS

Após DNS resolver, usar mecanismo TLS aprovado. Se Certbot estiver instalado:

~~~bash
certbot --nginx -d NOVODOMINIO
~~~

Antes de executar:
- confirmar domínio;
- confirmar Nginx;
- confirmar DNS;
- confirmar impacto.

## S14. Health

~~~bash
curl -I https://NOVODOMINIO/
~~~

## S15. Atualizar inventory.yaml e projects.yaml

Obrigatório para continuidade.

---

# PARTE T — NOVO SITE ESTÁTICO NA VPS

## T1. Build

Executar build conforme projeto.

## T2. Publicar artefato

Exemplo:
 /var/www/NOVODOMINIO/public_html

## T3. Nginx

~~~nginx
server {
    listen 80;
    server_name NOVODOMINIO;

    root /var/www/NOVODOMINIO/public_html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}
~~~

Ajustar fallback SPA apenas se a aplicação for SPA.

## T4. nginx -t, reload, DNS, TLS, health, inventory.

---

# PARTE U — NOVO SITE DOCKER

Só usar com decisão explícita.

## U1. Confirmar arquitetura

Responder:
por que Docker é necessário?

## U2. Compose

Definir:
- image/build;
- env;
- volume;
- network;
- healthcheck;
- restart;
- porta loopback.

Exemplo de porta:

127.0.0.1:PORTA_HOST:PORTA_CONTAINER

Evitar 0.0.0.0 quando Nginx é o gateway.

## U3. Subir

~~~bash
docker compose up -d
~~~

Crítico.

## U4. Health

~~~bash
docker compose ps
~~~

~~~bash
docker compose logs --tail 200
~~~

## U5. Nginx/TLS/DNS/inventory.

---

# PARTE V — MIGRAÇÃO SHARED HOSTING -> VPS

1. Não remover origem.
2. Preparar runtime VPS.
3. Testar local.
4. Testar por host override quando apropriado.
5. Preparar TLS.
6. Confirmar rollback.
7. Alterar DNS.
8. Validar propagação.
9. Testar externo.
10. Marcar migrated_from_shared_hosting.
11. Manter registro antigo por janela segura.
12. Limpar somente depois.

VPClick segue esse modelo histórico.

---

# PARTE W — MIGRAÇÃO VPS -> SHARED HOSTING

1. preparar shared;
2. deploy;
3. env;
4. health;
5. DNS;
6. TLS;
7. validar;
8. marcar Nginx VPS stale/legacy;
9. manter rollback;
10. remover depois.

---

# PARTE X — REDIRECT DE DOMÍNIO LEGADO

Exemplo de padrão:

~~~nginx
server {
    listen 80;
    server_name antigo.exemplo.com;
    return 301 https://novo.exemplo.com$request_uri;
}
~~~

HTTPS legado exige certificado válido para o host antigo antes de o browser aceitar o redirect.

Não remover o certificado antigo enquanto o redirect HTTPS for necessário.

---

# PARTE Y — ROTACIONAR X-API-KEY

Não coloque a chave no Git.

## Y1. Gerar novo segredo

Exemplo:

~~~bash
openssl rand -hex 32
~~~

Não cole o resultado em chat.

## Y2. Salvar em arquivo root-only

Use editor/comando seguro sem registrar em histórico quando possível.

## Y3. chmod

~~~bash
chmod 600 /root/infra-mcp-auth-token
~~~

## Y4. Atualizar Nginx/gateway

Fazer backup da config antes.

## Y5. Testar

~~~bash
nginx -t
~~~

## Y6. Reload

~~~bash
systemctl reload nginx
~~~

## Y7. Atualizar Claude

Atualizar X-API-Key em cada conta/cliente.

## Y8. Validar

tools/list + infra_inventory.

## Y9. Remover chave antiga.

---

# PARTE Z — RECUPERAÇÃO APÓS REBOOT

## Z1. Hostinger state

Use hostinger_vps_status.

## Z2. SSH

~~~bash
ssh root@72.61.48.156
~~~

## Z3. Serviços críticos

~~~bash
systemctl is-active nginx omie-mcp whatsapp-mcp verticalparts-infra-mcp docker
~~~

## Z4. Portas

~~~bash
ss -ltnp
~~~

## Z5. Endpoints

~~~bash
curl -I https://mcp.vpsistema.com/omie/mcp
~~~

~~~bash
curl -I https://whatsapp-mcp.vpsistema.com/mcp
~~~

~~~bash
curl -I https://infra-mcp.vpsistema.com/mcp
~~~

401 em endpoints protegidos pode ser esperado.

---

# PARTE AA — BACKUP ANTES DE MUDANÇA

Config Nginx:

~~~bash
cp ARQUIVO ARQUIVO.bak-$(date +%Y%m%d-%H%M%S)
~~~

Inventory:

~~~bash
cp /opt/verticalparts-infrastructure-mcp/config/inventory.yaml /opt/verticalparts-infrastructure-mcp/config/inventory.yaml.bak-$(date +%Y%m%d-%H%M%S)
~~~

Projects:

~~~bash
cp /opt/verticalparts-infrastructure-mcp/config/projects.yaml /opt/verticalparts-infrastructure-mcp/config/projects.yaml.bak-$(date +%Y%m%d-%H%M%S)
~~~

Git:
registrar SHA antes.

~~~bash
git -C CAMINHO rev-parse HEAD
~~~

---

# PARTE AB — INCIDENTE: DISCO CHEIO

## AB1. Uso

~~~bash
df -hT /
~~~

## AB2. Top diretórios

~~~bash
du -xhd1 / 2>/dev/null | sort -h
~~~

Não apague nada ainda.

## AB3. Docker

~~~bash
docker system df
~~~

Não prune sem análise.

## AB4. Logs

~~~bash
journalctl --disk-usage
~~~

Escolher limpeza segura baseada em evidência.

---

# PARTE AC — INCIDENTE: MEMÓRIA ALTA

~~~bash
free -h
~~~

~~~bash
ps aux --sort=-%mem | head -20
~~~

~~~bash
docker stats --no-stream
~~~

Não reiniciar processos apenas porque consomem memória; avaliar leak, cache e workload.

---

# PARTE AD — INCIDENTE: CPU ALTA

~~~bash
uptime
~~~

~~~bash
ps aux --sort=-%cpu | head -20
~~~

Correlacionar com logs.

---

# PARTE AE — INCIDENTE: CERTIFICADO

~~~bash
openssl s_client -connect DOMINIO:443 -servername DOMINIO </dev/null 2>/dev/null | openssl x509 -noout -subject -issuer -dates
~~~

Se Certbot:

~~~bash
certbot certificates
~~~

Não emitir certificado novo sem validar DNS.

---

# PARTE AF — RECONSTRUIR INVENTÁRIO SE PERDIDO

Somente leitura primeiro.

## AF1. VPS Hostinger
hostinger_list_vps

## AF2. Websites
hostinger_list_websites

## AF3. Nginx domains

~~~bash
grep -RhoP 'server_name\s+\K[^;]+' /etc/nginx/sites-available 2>/dev/null | tr ' ' '\n' | sort -u
~~~

## AF4. DNS

Para cada domínio:

~~~bash
dig +short DOMINIO A
~~~

## AF5. systemd

~~~bash
systemctl list-units --type=service --all --no-pager
~~~

## AF6. Docker

~~~bash
docker ps -a
~~~

## AF7. Portas

~~~bash
ss -ltnp
~~~

## AF8. Git repos

Descobrir cuidadosamente paths conhecidos.

## AF9. Reconciliar

Classifique:
- production;
- redirect;
- legacy;
- migrated;
- stale.

## AF10. Salvar inventory.yaml e validar.

---

# PARTE AG — CRITÉRIO DE SUCESSO

Nunca encerre porque “o comando rodou”.

Para MCP:
- initialize;
- tools/list;
- tools/call;
- public auth;
- Claude test.

Para site:
- runtime;
- DNS;
- TLS;
- HTTP;
- funcionalidade;
- inventory.

Para deploy:
- new SHA;
- runtime;
- health;
- rollback state.

---

# PARTE AH — COMANDO DE TESTE FINAL NO CLAUDE

~~~text
Use o conector VerticalParts Infrastructure.

1. Consulte infra_inventory.
2. Informe os domínios em produção na VPS.
3. Informe os domínios em produção no shared hosting.
4. Informe qual domínio foi migrado do shared hosting para VPS.
5. Informe o redirect legado do VPRequisições.
6. Não faça nenhuma alteração.
~~~

Se a resposta estiver correta, a cadeia Claude -> Nginx/Auth -> MCP -> inventory está funcional.

---

# PARTE AI — REGRA FINAL PARA NOVOS SITES

Depois de colocar um site no ar, a LLM deve deixar o futuro operador sabendo:

- onde roda;
- como inicia;
- como faz deploy;
- qual repo/branch;
- qual domínio;
- qual health;
- como diagnosticar;
- como recuperar;
- como fazer rollback;
- onde está no inventory;
- quais segredos existem sem revelar valores.

Se isso não estiver registrado, o onboarding não terminou.
