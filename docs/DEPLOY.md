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
- catálogo observado: 49 tools (sessão 1); **62 tools** após a auditoria de segurança de 2026-09-19 (sessão 2 — ver `docs/HOMOLOGATION.md`).

Essa co-localização funciona, mas cria um ponto único de falha: se a VPS ficar totalmente indisponível, o próprio control plane também fica indisponível.

## Arquitetura recomendada futura

Hospedar o MCP administrador fora da VPS alvo. Assim `hostinger_vps_start/stop/restart` continua disponível durante falha total do target.

## Atualização segura do próprio MCP

IMPORTANTE (achado real de 2026-09-19): `/opt/verticalparts-infrastructure-mcp` é `root:root`. As tools MCP estruturadas `git_pull`/`git_status`/`file_write` rodam via SSH como usuário `infra-mcp` **sem sudo** e falham nesse diretório especificamente (`dubious ownership` do Git, depois `Permission denied` em `.git/FETCH_HEAD`). Isso não é bug — é a proteção que impede o MCP de se auto-modificar silenciosamente fora do caminho auditado do break-glass. Use os comandos com `sudo` (via break-glass/`infra_exec_command`, ou terminal root direto):

0. uma única vez por ambiente: `sudo git config --global --add safe.directory /opt/verticalparts-infrastructure-mcp`;
1. confirmar working tree limpa (`sudo git status --short` — atenção a arquivos `.bak`/backup deixados dentro do próprio diretório do repo por operações anteriores; mova-os para fora, ex. `/root/mcp-config-backups/`, antes de continuar);
2. `sudo git fetch --all --prune`;
3. revisar commits entrantes;
4. `sudo git pull --ff-only` (ou `checkout BRANCH && pull --ff-only origin BRANCH` para aplicar uma branch específica);
5. se dependências mudaram, atualizar venv: `sudo .venv/bin/pip install -e .`;
6. validar sintaxe/import: `sudo .venv/bin/python3 -m py_compile src/verticalparts_infra_mcp/server.py`;
7. reiniciar somente `verticalparts-infra-mcp.service`;
8. confirmar `active`;
9. executar MCP `initialize`;
10. executar `tools/list` — se uma tool nova não aparecer de imediato, chame qualquer tool de leitura primeiro para forçar a reconexão da sessão do cliente MCP (o catálogo pode ficar em cache por alguns segundos);
11. executar uma tool de leitura real.

Atualizações apenas de Markdown/documentação não exigem restart do serviço, mas ainda passam pelos passos 0–4 (o `git pull` sofre a mesma restrição de ownership independentemente do tipo de arquivo alterado).

Procedimento completo com comandos copy-paste: `05_RUNBOOK_COPY_PASTE_RECOVERY_AND_ONBOARDING.md` PARTE G.

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
