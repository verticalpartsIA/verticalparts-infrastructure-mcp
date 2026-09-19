# Instalação — VerticalParts Infrastructure MCP

Versão: 2026-09-19
Status: revisado após auditoria

## Estratégia

A instalação pode ocorrer em duas fases:

1. homologação co-localizada na VPS alvo;
2. produção resiliente em host de controle independente.

O ambiente atual está na fase 1 e foi homologado funcionalmente. A fase 2 continua recomendada para recuperação durante falha total da VPS.

## Pré-requisitos

- Python 3.11+;
- Git;
- acesso autorizado à API Hostinger;
- token Hostinger armazenado fora do Git;
- chave SSH dedicada;
- usuário Linux dedicado `infra-mcp`;
- known_hosts;
- Nginx/HTTPS ou gateway compatível com Streamable HTTP;
- segredo de autenticação externa do MCP;
- DNS do endpoint remoto.

## Arquivos que nunca entram no Git

- `.env`;
- `config/projects.yaml`;
- `config/inventory.yaml`;
- `secrets/`;
- `data/`;
- private keys;
- tokens;
- passwords;
- dumps;
- backups com dados.

## Instalação do pacote

```bash
git clone https://github.com/verticalpartsIA/verticalparts-infrastructure-mcp.git /opt/verticalparts-infrastructure-mcp
cd /opt/verticalparts-infrastructure-mcp
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -e .
cp .env.example .env
cp config/projects.example.yaml config/projects.yaml
cp config/inventory.example.yaml config/inventory.yaml
```

Não inicie o serviço antes de preencher e validar `.env`, SSH, inventory e projects.

## Configuração mínima

```env
MCP_TRANSPORT=streamable-http
MCP_HOST=127.0.0.1
MCP_PORT=8020
HOSTINGER_API_TOKEN=
HOSTINGER_VM_ID=
INFRA_SSH_HOST=
INFRA_SSH_PORT=22
INFRA_SSH_USER=infra-mcp
INFRA_SSH_KEY=/opt/verticalparts-infrastructure-mcp/secrets/id_ed25519
INFRA_SSH_KNOWN_HOSTS=/opt/verticalparts-infrastructure-mcp/secrets/known_hosts
INFRA_PROJECTS_FILE=/opt/verticalparts-infrastructure-mcp/config/projects.yaml
INFRA_INVENTORY_FILE=/opt/verticalparts-infrastructure-mcp/config/inventory.yaml
INFRA_POLICIES_FILE=/opt/verticalparts-infrastructure-mcp/config/policies.yaml
INFRA_AUDIT_LOG=/opt/verticalparts-infrastructure-mcp/data/audit.jsonl
INFRA_ALLOW_BREAK_GLASS=false
```

O token Hostinger deve permanecer somente no ambiente seguro do host.

## Ordem de homologação

1. validar SSH dedicado;
2. iniciar MCP em loopback;
3. executar tools de leitura;
4. validar Hostinger API;
5. validar `infra_inventory`;
6. validar `infra_list_projects`;
7. validar Docker somente se houver target Docker;
8. instalar systemd;
9. **validar firewall do host** (`ufw status verbose` ou `firewall_status`) — não presumir que está ativo/correto só porque o host é novo; achado real de 2026-09-19 mostrou um host em produção há meses com firewall totalmente inativo. Estado esperado: `default deny incoming`, liberado só o estritamente necessário (tipicamente `22/80/443`);
10. publicar HTTPS autenticado;
11. executar `initialize` e `tools/list`;
12. chamar uma tool real de leitura;
13. testar mutação controlada somente com confirmação.

## Shared Hosting

A API Hostinger atual já cobre uma parte grande da operação sem SSH:
- websites/orders;
- arquivos;
- SSL;
- bancos;
- cron;
- Node.js builds/logs/settings/env/vulnerabilities/restart.

Portanto, não tente descobrir SSH de Shared Hosting como primeira solução. Use API semântica primeiro. SSH só deve ser investigado se surgir uma necessidade concreta que a API não cobre.

## Systemd

Copiar e revisar `systemd/verticalparts-infra-mcp.service.example`.

O serviço atual executa como `infra-mcp`. Mudanças de hardening devem ser testadas contra SSH key/known_hosts e todas as tools.

## Sudo

Durante a homologação o usuário `infra-mcp` possui sudo amplo. Isso é temporário.

Meta:
- allowlist de systemctl/journalctl;
- Nginx;
- Docker;
- APT;
- outros comandos estritamente necessários.

Não adicionar o usuário ao grupo Docker como correção automática; o desenho atual usa `sudo docker`.

## Segurança

Não habilite `INFRA_ALLOW_BREAK_GLASS=true` por conveniência. O shell arbitrário é contingência.
