# Deploy do próprio Infrastructure MCP

Versão: 2026-09-19
Status: revisado após homologação

## Estado atual

O Infrastructure MCP está homologado temporariamente na própria VPS administrada:

- instalação: `/opt/verticalparts-infrastructure-mcp`;
- serviço: `verticalparts-infra-mcp.service`;
- bind: `127.0.0.1:8020`;
- proxy público: `https://infra-mcp.vpsistema.com/mcp`;
- serviço executa como usuário `infra-mcp`;
- catálogo observado: 49 tools.

Essa co-localização funciona, mas cria um ponto único de falha: se a VPS ficar totalmente indisponível, o próprio control plane também fica indisponível.

## Arquitetura recomendada futura

Hospedar o MCP administrador fora da VPS alvo. Assim `hostinger_vps_start/stop/restart` continua disponível durante falha total do target.

## Atualização segura do próprio MCP

1. confirmar working tree limpa;
2. `git fetch`;
3. revisar commits entrantes;
4. `git pull --ff-only origin main`;
5. se dependências mudaram, atualizar venv;
6. validar sintaxe/import;
7. reiniciar somente `verticalparts-infra-mcp.service`;
8. confirmar `active`;
9. executar MCP `initialize`;
10. executar `tools/list`;
11. executar uma tool de leitura real.

Atualizações apenas de Markdown/documentação não exigem restart do serviço.

## Desenvolvimento local

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
cp .env.example .env
cp config/projects.example.yaml config/projects.yaml
cp config/inventory.example.yaml config/inventory.yaml
verticalparts-infra-mcp
```

## Produção remota

```env
MCP_TRANSPORT=streamable-http
MCP_HOST=127.0.0.1
MCP_PORT=8020
```

Publicar somente via HTTPS autenticado. Não expor 8020 diretamente à Internet.

## Pré-requisitos do plano Linux

- OpenSSH;
- Git para projetos Git;
- Docker apenas para targets Docker;
- Nginx quando aplicável;
- systemd;
- usuário SSH dedicado;
- chave pública autorizada;
- known_hosts validado;
- sudo controlado.

Na homologação atual o sudo do usuário `infra-mcp` ainda é amplo. Isso é dívida de segurança; a meta é sudo granular depois de testar todas as tools.

## Control plane Hostinger

Configurar `HOSTINGER_API_TOKEN` e `HOSTINGER_VM_ID` sem versionar valores.

A API Hostinger é usada tanto para VPS quanto para Shared Hosting. O Shared Hosting não depende de SSH para as operações já cobertas semanticamente por API: websites, orders, arquivos, SSL, bancos, cron e Node.js.

Nunca assumir que um website listado pela API é produção. Produção é reconciliada por DNS + inventory + runtime + health.
