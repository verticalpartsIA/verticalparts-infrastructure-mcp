# Instalação — VerticalParts Infrastructure MCP

## Estratégia

A instalação é feita em duas fases:

1. **Homologação**: pode rodar temporariamente na VPS que será administrada, para validar tools, autenticação, SSH e políticas.
2. **Produção resiliente**: mover o MCP administrador para outro host/serviço. Assim o control plane continua disponível mesmo quando a VPS alvo estiver indisponível.

## Pré-requisitos

- Python 3.11+;
- Git;
- acesso à conta Hostinger para gerar um token de API;
- uma chave SSH dedicada para o MCP;
- usuário Linux dedicado `infra-mcp`;
- Nginx/HTTPS ou outro proxy compatível com Streamable HTTP;
- segredo de autenticação externa do endpoint MCP;
- DNS desejado para o MCP remoto.

## Arquivos que nunca entram no Git

- `.env`;
- `config/projects.yaml`;
- chaves SSH privadas;
- token Hostinger;
- segredo usado pelo proxy/MCP;
- dumps e backups.

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
```

Não inicie o serviço antes de preencher e validar `.env`, SSH e `config/projects.yaml`.

## Configuração mínima para homologação

No `.env`:

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
INFRA_POLICIES_FILE=/opt/verticalparts-infrastructure-mcp/config/policies.yaml
INFRA_AUDIT_LOG=/opt/verticalparts-infrastructure-mcp/data/audit.jsonl
INFRA_ALLOW_BREAK_GLASS=false
```

O token Hostinger deve ser criado no hPanel e gravado somente no `.env` do host. Nunca cole o token em issue, chat público, documentação ou commit.

## Ordem de homologação

1. validar SSH dedicado;
2. iniciar MCP manualmente em loopback;
3. executar somente tools de leitura;
4. validar API Hostinger e descobrir `vm_id`;
5. cadastrar projetos reais em `config/projects.yaml`;
6. testar uma mutação operacional controlada;
7. instalar `systemd`;
8. publicar HTTPS autenticado;
9. conectar os clientes MCP;
10. testar deploy/rollback;
11. só então testar restart da VPS via control plane.

## Systemd

Copiar e revisar `systemd/verticalparts-infra-mcp.service.example`. O exemplo usa usuário dedicado e restrições do systemd. Os caminhos precisam existir antes de habilitar o serviço.

## Segurança

Não habilite `INFRA_ALLOW_BREAK_GLASS=true` durante a homologação inicial. O shell arbitrário é mecanismo de contingência e deve permanecer desabilitado por padrão.
