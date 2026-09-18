# Deploy do próprio Infrastructure MCP

## Recomendação

Hospedar fora da VPS alvo. Isso é necessário para que `hostinger_vps_start/stop/restart` continue disponível quando o host administrado estiver fora do ar.

## Desenvolvimento local

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
cp .env.example .env
cp config/projects.example.yaml config/projects.yaml
verticalparts-infra-mcp
```

## Produção remota

Configurar:

```env
MCP_TRANSPORT=streamable-http
MCP_HOST=127.0.0.1
MCP_PORT=8020
```

Depois publicar somente via proxy HTTPS autenticado.

## Pré-requisitos do target Linux

- OpenSSH;
- Python não é obrigatório no target;
- Git para projetos Git;
- Docker para tools Docker;
- Nginx para tools Nginx;
- systemd;
- usuário SSH dedicado;
- chave pública autorizada;
- sudoers mínimo necessário.

## Control plane Hostinger

Definir `HOSTINGER_API_TOKEN` e `HOSTINGER_VM_ID`. O ID deve ser descoberto por `hostinger_list_vps`; não confundir com endereço IP.
