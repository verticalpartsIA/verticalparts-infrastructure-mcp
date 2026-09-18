# CLAUDE.md — VerticalParts Infrastructure MCP

Leia primeiro:

1. `rag/RAG_MCP_INFRASTRUCTURE_VERTICALPARTS.md`
2. `docs/SPEC.md`
3. `docs/SDD.md`
4. `docs/RISK_MATRIX.md`
5. `docs/SECURITY.md`
6. `docs/TOOL_CATALOG.md`

## Missão

Administrar infraestrutura por tools semânticas, com diagnóstico antes de intervenção, confirmação proporcional ao risco, segredos protegidos, auditoria e rollback.

## Regras obrigatórias

- Não invente target, path, VM ID, serviço, container, branch ou credencial.
- Não mostre segredos.
- Prefira tool específica a `infra_exec_command`.
- Repositório Git sujo bloqueia deploy por padrão.
- Teste Nginx antes de reload.
- Timeout de mutação exige verificação de estado antes de retry.
- Operação crítica: `CONFIRMO`.
- Operação destrutiva: `CONFIRMO_DESTRUTIVO`.
- Break-glass: `BREAK_GLASS` e flag do servidor habilitada.
- Depois de mutação, valide o estado final.
