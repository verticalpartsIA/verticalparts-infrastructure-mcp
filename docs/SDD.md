# SDD — VerticalParts Infrastructure MCP

## 1. Arquitetura

```text
Claude / outro cliente MCP
          |
          v
VerticalParts Infrastructure MCP
          |
          +--------------------------+
          |                          |
          v                          v
Hostinger API                 SSH Operations Plane
          |                          |
          v                          v
Control Plane VPS             Linux da VPS
start/stop/restart            systemd / Docker / Git
metrics/status                env / arquivos / nginx
                              deploy / logs / updates
```

## 2. Local de execução recomendado

Produção: executar o Infrastructure MCP fora da VPS administrada.

Motivo: se a VPS alvo ficar desligada ou perder rede, um MCP hospedado nela também desaparece. O control plane deve sobreviver à indisponibilidade do target.

Fases possíveis:

1. desenvolvimento local no PC;
2. homologação em processo remoto separado;
3. produção em host de controle independente.

## 3. Fluxo de diagnóstico

```text
pedido do usuário
 -> identificar alvo
 -> descobrir estado
 -> classificar falha
 -> coletar evidência
 -> escolher menor intervenção suficiente
 -> pedir confirmação se risco crítico
 -> executar
 -> validar estado final
 -> auditar
```

Nunca iniciar por restart se logs/status permitem diagnóstico menos invasivo.

## 4. Fluxo de deploy

```text
resolver projeto
 -> confirmar path/repo/branch/runtime
 -> git status
 -> recusar working tree suja
 -> registrar old_sha
 -> fetch/pull --ff-only
 -> build
 -> restart runtime
 -> health check
 -> sucesso: registrar new_sha
 -> falha: rollback para old_sha + restart + relatar
```

## 5. Fluxo de variável

```text
identificar arquivo
 -> listar chaves sem valores
 -> validar chave
 -> pedir confirmação
 -> backup do arquivo
 -> alterar apenas a chave
 -> reiniciar serviço quando solicitado
 -> validar serviço
 -> auditar sem valor do segredo
```

## 6. Fluxo de restart de VPS

```text
consultar status via Hostinger
 -> explicar impacto
 -> confirmation=CONFIRMO
 -> POST /api/vps/v1/virtual-machines/{id}/restart
 -> aguardar retorno do control plane
 -> polling de status
 -> testar SSH
 -> testar serviços críticos
```

## 7. Camadas de segurança

1. Autenticação do cliente MCP.
2. Política de risco da tool.
3. Confirmação explícita.
4. Allowlist de caminhos.
5. SSH por chave + known_hosts.
6. Usuário dedicado + sudo mínimo.
7. Auditoria.
8. Backup/rollback.

## 8. Break-glass

`infra_exec_command` existe para não deixar a LLM incapaz diante de um incidente não previsto. Por padrão:

`INFRA_ALLOW_BREAK_GLASS=false`

Para usar, o operador precisa habilitar a flag e fornecer `confirmation=BREAK_GLASS`. Toda chamada registra comando e justificativa.
