# CLAUDE.md — VerticalParts Infrastructure MCP

Versão operacional: 2026-09-19
Status: revisado após auditoria e homologação real

## Leitura obrigatória

Antes de operar este repositório, leia nesta ordem:

1. `00_READ_FIRST_INFRASTRUCTURE_MCP.md`
2. `03_INSTRUCTIONS_LLM_MCP_INFRASTRUCTURE_VERTICALPARTS.md`
3. `01_RAG_MCP_INFRASTRUCTURE_VERTICALPARTS.md`
4. `02_SPEC_MCP_INFRASTRUCTURE_VERTICALPARTS.md`
5. `04_SDD_MCP_INFRASTRUCTURE_VERTICALPARTS.md`
6. `05_RUNBOOK_COPY_PASTE_RECOVERY_AND_ONBOARDING.md`

Depois consulte:
- `README.md`;
- `docs/*`;
- `config/*.example.yaml`;
- `src/verticalparts_infra_mcp/*`.

Os arquivos numerados da raiz são canônicos. Arquivos em `docs/` são complementares. O RAG canônico é o arquivo `01_RAG...` da raiz.

## Missão

Administrar e recuperar infraestrutura VerticalParts por tools semânticas, com diagnóstico antes de intervenção, confirmação proporcional ao risco, proteção de segredos, inventário, auditoria, health e rollback.

## Hierarquia de verdade

1. estado vivo observado;
2. `config/inventory.yaml` do runtime;
3. `config/projects.yaml` do runtime;
4. código em execução;
5. documentos canônicos numerados;
6. documentação complementar;
7. memória de conversa.

## Estado homologado em 2026-09-19

- serviço: `verticalparts-infra-mcp.service`;
- endpoint: `https://infra-mcp.vpsistema.com/mcp`;
- transporte: Streamable HTTP;
- bind interno: `127.0.0.1:8020`;
- autenticação pública: `X-API-Key` no gateway;
- catálogo MCP observado: **49 tools**;
- `hostinger_ssl_status` homologada end-to-end pelo protocolo MCP;
- Docker usa `sudo docker` / `sudo docker compose` no plano SSH;
- o antigo erro de socket Docker foi corrigido; se reaparecer, tratar como regressão;
- break-glass permanece desabilitado por padrão.

## Shared Hosting Hostinger

O MCP possui tools semânticas para:
- orders/websites;
- arquivos e leitura segura de texto;
- Git auto-deploy;
- SSL;
- bancos;
- cron jobs;
- Node.js settings;
- builds;
- build logs;
- runtime logs;
- nomes de env sem valores;
- vulnerabilidades Node.js;
- restart controlado de Node.js.

Regra: prefira essas tools a `hostinger_api_call`.

Estado observado:
- 9 registros Node.js na conta Cloud, todos com auto-deploy Git ativo;
- 5 registros `other` na conta Premium, sem auto-deploy Git Hostinger;
- `website_type=other` não significa automaticamente PHP;
- PHP 8.3.33 está disponível nesses cinco ambientes, mas a aplicação real deve ser classificada pelos arquivos/runtime;
- `vpclick.vpsistema.com` ainda existe no Shared Hosting com Git ativo, porém é legado; produção canônica é Docker na VPS.

## Regras obrigatórias

- Não invente target, path, VM ID, website, serviço, container, branch, porta, health ou credencial.
- Consulte `infra_inventory` antes de decisões de topologia.
- DNS + runtime + health definem produção; cadastro Hostinger isolado não define.
- Não mostre segredos.
- Valores de env retornados pela Hostinger são mascarados e nunca devem ser reutilizados como valores reais.
- Não tente ler `.env`, private keys ou certificados privados pela tool de arquivos.
- Prefira tool específica a `hostinger_api_call`; prefira `hostinger_api_call` a break-glass quando o endpoint oficial ainda não tem wrapper.
- Repositório Git sujo bloqueia deploy por padrão.
- Projeto com `deploy.mode=external` não deve ser publicado por `deploy_project`.
- Teste Nginx antes de reload.
- Timeout de mutação exige verificação de estado antes de retry.
- Operação crítica: `CONFIRMO`.
- Operação destrutiva: `CONFIRMO_DESTRUTIVO`.
- Break-glass: `BREAK_GLASS` e flag habilitada.
- Depois de mutação, valide o estado final.
- Docker não é default; VPClick é a aplicação atualmente intencionalmente containerizada na VPS.
- VPRequisições está no Shared Hosting e não deve ser iniciado em Docker na VPS.
- Não desligue o cadastro legado do VPClick na Hostinger apenas por ele ser legado; investigar impacto antes.
- Omie local do Claude Code não é Omie remoto.
- Mudança estrutural exige atualização de inventory e documentação.

## Continuidade operacional

Se conexão quebrar ou novo site precisar entrar no ar, siga `05_RUNBOOK_COPY_PASTE_RECOVERY_AND_ONBOARDING.md`.

Nunca deixe uma mudança arquitetural registrada somente em conversa.
