# VerticalParts Infrastructure MCP

MCP corporativo para administração de infraestrutura da VerticalParts por LLMs, com duas camadas de controle:

1. Control Plane Hostinger — operações externas sobre VPS por API Hostinger.
2. VPS Operations — administração interna do Linux por SSH seguro.

O objetivo é permitir que um agente execute diagnóstico, deploy, atualização, gestão de serviços, Docker, Git, variáveis, arquivos, Nginx, backups, atualizações do sistema e recuperação da VPS sem obrigar o usuário a conhecer comandos de infraestrutura.

## Princípio central

A LLM recebe ferramentas semânticas para as operações comuns e dois mecanismos de escape controlados:

- `hostinger_api_call`: fallback para endpoints Hostinger ainda não encapsulados.
- `infra_exec_command`: break-glass para comandos Linux que ainda não possuem tool específica.

Esses fallbacks exigem confirmação para mutações e são auditados.

## Por que duas camadas

O processo que administra Linux não pode ser o único mecanismo de recuperação da própria máquina. Se a VPS ficar indisponível, comandos SSH deixam de funcionar. Por isso o MCP também chama a API Hostinger externamente para status, start, stop, restart e outras operações de control plane.

Em produção, hospede este MCP fora da VPS que ele administra sempre que quiser capacidade real de recuperação após indisponibilidade total.

## Estrutura

```text
verticalparts-infrastructure-mcp/
├── src/verticalparts_infra_mcp/
│   ├── server.py
│   ├── config.py
│   ├── hostinger.py
│   ├── ssh.py
│   ├── audit.py
│   ├── safety.py
│   ├── registry.py
│   └── deploy.py
├── config/
│   ├── projects.example.yaml
│   └── policies.yaml
├── docs/
│   ├── SPEC.md
│   ├── SDD.md
│   ├── TOOL_CATALOG.md
│   ├── RISK_MATRIX.md
│   ├── SECURITY.md
│   ├── DEPLOY.md
│   └── HOMOLOGATION.md
├── rag/
│   └── RAG_MCP_INFRASTRUCTURE_VERTICALPARTS.md
├── systemd/
│   └── verticalparts-infra-mcp.service.example
├── nginx/
│   └── README.md
├── .env.example
└── pyproject.toml
```

## Capacidades implementadas na v0.1

### Hostinger / control plane

- listar VPS;
- consultar VPS;
- métricas;
- start;
- stop;
- restart;
- chamada genérica à API Hostinger com política de confirmação.

### Linux / SSH

- health geral;
- uso de disco e memória;
- processos;
- portas em escuta;
- status/start/stop/restart de systemd;
- journal de serviços;
- Docker ps/logs/restart;
- Docker Compose pull/build/up/restart;
- Git status/fetch/pull/log/checkout;
- leitura e escrita controlada de arquivos;
- listar chaves de `.env` sem revelar valores;
- definir/remover variável de `.env` com backup;
- testar e recarregar Nginx;
- consultar atualizações APT;
- executar upgrade APT com confirmação;
- comando break-glass auditado.

### Deploy

- registro declarativo de projetos;
- preflight de Git;
- bloqueio de deploy com working tree suja por padrão;
- registro do commit anterior;
- atualização do código;
- build configurável;
- restart systemd ou Docker Compose;
- health check;
- rollback automático de código se o health check falhar.

## Instalação local para desenvolvimento

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
cp .env.example .env
cp config/projects.example.yaml config/projects.yaml
verticalparts-infra-mcp
```

Por padrão o transporte é `stdio`. Para servidor remoto:

```env
MCP_TRANSPORT=streamable-http
MCP_HOST=127.0.0.1
MCP_PORT=8020
```

## Segredos

Nunca versione:

- `HOSTINGER_API_TOKEN`;
- chave SSH privada;
- senha root;
- chave de autenticação do MCP;
- valores de `.env` dos projetos.

O MCP trabalha com nomes/chaves de variáveis, mas não deve devolver segredos ao modelo.

## Confirmações

- `CONFIRMO` — operação crítica.
- `CONFIRMO_DESTRUTIVO` — operação destrutiva.
- `BREAK_GLASS` — shell arbitrário.

A LLM deve explicar o alvo e o efeito antes de pedir qualquer uma dessas confirmações.

## Referências oficiais usadas no desenho

- Hostinger Remote MCP: https://mcp.hostinger.com
- Hostinger MCP/API: https://www.hostinger.com/support/11079316-hostinger-api-mcp-server/
- Hostinger API docs: https://developers.hostinger.com/
- Hostinger API MCP source: https://github.com/hostinger/api-mcp-server
- Hostinger Python SDK: https://github.com/hostinger/api-python-sdk

## Estado

v0.1 = scaffold funcional para homologação. Antes de produção devem ser concluídos os testes descritos em `docs/HOMOLOGATION.md`, implantação de autenticação externa e criação de usuário SSH dedicado com privilégios mínimos suficientes.
