# Segurança

## 1. Princípio

O objetivo é capacidade administrativa ampla sem entregar segredos desnecessários ao modelo.

## 2. Credenciais

- Hostinger: token em secret store/variável de ambiente ou OAuth quando a arquitetura permitir.
- SSH: chave privada fora do repositório.
- Produção: usuário `infra-mcp`, não senha root.
- `known_hosts` obrigatório; não usar `StrictHostKeyChecking=no`.

## 3. Sudo recomendado

Dar ao usuário `infra-mcp` somente comandos necessários por sudoers. Exemplo de categorias:

- `systemctl` para serviços cadastrados;
- `journalctl`;
- `nginx -t` / reload;
- apt update/upgrade quando aprovado;
- Docker, se necessário.

Não liberar `NOPASSWD: ALL` em produção sem decisão explícita de risco.

## 4. Segredos em .env

A LLM pode saber que `DATABASE_URL` existe, mas não precisa receber o valor. `env_set` aceita o novo valor como argumento da chamada, grava e devolve `[REDACTED]`.

## 5. Autenticação externa do MCP

Streamable HTTP deve ficar atrás de HTTPS e autenticação. Opções preferidas:

- OAuth/proxy de identidade;
- access gateway;
- header secreto validado no gateway.

Não publique a porta interna diretamente.

## 6. Auditoria

Auditar toda mutação. Evitar registrar valores de tokens, senhas e chaves.

## 7. Shell arbitrário

Desabilitado por padrão. A presença dessa tool não deve virar atalho para ignorar wrappers semânticos.
