# CLAUDE.md — VerticalParts Infrastructure MCP

## Leitura obrigatória

Antes de operar este repositório, leia nesta ordem:

1. 00_READ_FIRST_INFRASTRUCTURE_MCP.md
2. 03_INSTRUCTIONS_LLM_MCP_INFRASTRUCTURE_VERTICALPARTS.md
3. 01_RAG_MCP_INFRASTRUCTURE_VERTICALPARTS.md
4. 02_SPEC_MCP_INFRASTRUCTURE_VERTICALPARTS.md
5. 04_SDD_MCP_INFRASTRUCTURE_VERTICALPARTS.md
6. 05_RUNBOOK_COPY_PASTE_RECOVERY_AND_ONBOARDING.md

Depois consulte:
- README.md
- docs/*
- config/*.example.yaml
- src/verticalparts_infra_mcp/*

## Missão

Administrar e recuperar infraestrutura VerticalParts por tools semânticas, com diagnóstico antes de intervenção, confirmação proporcional ao risco, proteção de segredos, inventário, auditoria, health e rollback.

## Hierarquia de verdade

1. estado vivo;
2. config/inventory.yaml do runtime;
3. config/projects.yaml do runtime;
4. código;
5. documentos canônicos numerados da raiz;
6. documentos históricos;
7. memória.

## Regras obrigatórias

- Não invente target, path, VM ID, website, serviço, container, branch, porta, health ou credencial.
- Consulte infra_inventory antes de decisões de topologia.
- DNS + runtime + health definem produção; cadastro Hostinger isolado não define.
- Não mostre segredos.
- Prefira tool específica a infra_exec_command.
- Repositório Git sujo bloqueia deploy por padrão.
- Teste Nginx antes de reload.
- Timeout de mutação exige verificação de estado antes de retry.
- Operação crítica: CONFIRMO.
- Operação destrutiva: CONFIRMO_DESTRUTIVO.
- Break-glass: BREAK_GLASS e flag habilitada.
- Depois de mutação, valide o estado final.
- Docker não é default; VPClick é a aplicação atualmente intencionalmente containerizada na VPS.
- VPRequisições está no shared hosting e não deve ser iniciado em Docker na VPS.
- Omie local do Claude Code não é Omie remoto.
- Mudança estrutural exige atualização de inventory e documentação.

## Endpoint canônico

Infrastructure MCP:
https://infra-mcp.vpsistema.com/mcp

## Continuidade operacional

Se conexão quebrar ou novo site precisar entrar no ar, siga:
05_RUNBOOK_COPY_PASTE_RECOVERY_AND_ONBOARDING.md

Nunca deixe uma mudança arquitetural registrada somente em conversa.
