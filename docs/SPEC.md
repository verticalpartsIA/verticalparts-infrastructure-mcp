# SPEC — VerticalParts Infrastructure MCP

## 1. Objetivo

Permitir que uma LLM administre infraestrutura da VerticalParts por intenção de negócio, com ferramentas semânticas, confirmação proporcional ao risco, auditoria e capacidade de recuperação.

O escopo cobre dois planos:

- Hostinger Control Plane: ciclo de vida da VPS e recursos expostos pela API Hostinger.
- VPS Operations Plane: sistema operacional, serviços, containers, Git, deploy, variáveis, arquivos, proxy e diagnóstico.

## 2. Requisitos funcionais

### FR-INFRA-001 — Descoberta de alvo
Antes de alterar qualquer recurso, identificar host, projeto, serviço/container e ambiente corretos. Nome textual ambíguo não autoriza mutação.

### FR-INFRA-002 — Leitura antes de escrita
Quando uma mutação depender do estado atual, consultar o estado antes. Ex.: status do serviço antes de restart, working tree antes de pull, `nginx -t` antes de reload.

### FR-INFRA-003 — Ferramentas semânticas
Preferir tools específicas. Shell genérico é break-glass e não caminho normal.

### FR-INFRA-004 — Control plane externo
Start/stop/restart da VPS deve ser possível pela API Hostinger. Isso permite recuperação mesmo quando SSH não responde, desde que o MCP esteja hospedado fora da VPS alvo.

### FR-INFRA-005 — SSH seguro
Usar chave SSH, verificação de host key e usuário dedicado em produção. Não guardar senha root no MCP.

### FR-INFRA-006 — Serviços
Permitir status, logs, start, stop e restart de systemd. Mutações exigem confirmação.

### FR-INFRA-007 — Docker
Permitir listar, logs, restart de container e ações Compose. Remoções/`down` destrutivo devem exigir confirmação destrutiva em versões futuras.

### FR-INFRA-008 — Git
Permitir status, log, fetch e pull. Pull deve usar `--ff-only` e recusar working tree suja por padrão.

### FR-INFRA-009 — Variáveis
Listar nomes/chaves sem revelar valores. Alterações criam backup e não devolvem o segredo ao modelo.

### FR-INFRA-010 — Arquivos
Leitura/escrita limitadas a raízes permitidas. Escrita cria backup. `.env` deve usar ferramentas próprias.

### FR-INFRA-011 — Nginx
Testar configuração antes de reload. Nunca recarregar se `nginx -t` falhar.

### FR-INFRA-012 — Deploy
Deploy deve executar preflight, registrar commit anterior, atualizar código, buildar, reiniciar runtime, fazer health check e fazer rollback se configurado e necessário.

### FR-INFRA-013 — Atualizações do SO
Permitir consulta de updates. Instalação exige confirmação. Reboot é operação separada.

### FR-INFRA-014 — Auditoria
Toda mutação deve registrar timestamp, tool, alvo, ação, resultado e erro, sem segredos.

### FR-INFRA-015 — Confirmação por risco
Leitura: sem confirmação.
Operacional reversível: pode executar sem confirmação quando explicitamente solicitado.
Crítico: `CONFIRMO`.
Destrutivo: `CONFIRMO_DESTRUTIVO`.
Break-glass: `BREAK_GLASS` e flag de servidor habilitada.

### FR-INFRA-016 — Fallback Hostinger
A API Hostinger evolui. Deve existir fallback genérico para endpoint ainda não encapsulado, com classificação automática de risco e confirmação.

### FR-INFRA-017 — Fallback Linux
Deve existir execução arbitrária controlada para incidentes excepcionais. Ela deve estar desabilitada por padrão.

### FR-INFRA-018 — Diagnóstico antes de reiniciar
A LLM deve distinguir sessão do cliente, processo local, serviço remoto, proxy, rede, autenticação e aplicação antes de reiniciar infraestrutura.

### FR-INFRA-019 — Rollback
Mudanças com rollback viável devem preservar referência anterior: backup de arquivo, commit anterior, versão anterior ou snapshot.

### FR-INFRA-020 — Não inventar
Nunca inventar ID da VPS, caminho, serviço, container, branch, variável, porta, health URL, credencial ou resultado.

## 3. Requisitos não funcionais

- Segurança: mínimo privilégio, segredos fora do Git, autenticação externa.
- Auditabilidade: toda escrita rastreável.
- Resiliência: control plane independente da VPS alvo.
- Reversibilidade: backup/rollback sempre que viável.
- Observabilidade: logs e health checks antes/depois.
- Determinismo: mesmas condições devem levar à mesma política de risco.
