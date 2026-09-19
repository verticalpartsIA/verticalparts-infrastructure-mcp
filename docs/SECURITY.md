# Segurança

Versão: 2026-09-19

## 1. Princípio

Fornecer capacidade administrativa sem entregar segredos desnecessários ao modelo e sem transformar uma LLM em shell irrestrito.

## 2. Credenciais

- Hostinger API token: somente secret store/`.env` do host;
- Infrastructure `X-API-Key`: gateway e arquivo root-only autorizado;
- WhatsApp `X-API-Key`: gateway e arquivo root-only autorizado;
- SSH: private key fora do Git;
- `known_hosts` obrigatório;
- GitHub: chave dedicada quando aplicável;
- nunca documentar valores de tokens, passwords ou private keys.

## 3. Sudo — estado real e meta

Estado atual de homologação:
- `infra-mcp` possui sudo amplo `NOPASSWD: ALL`.

Isso foi usado para homologar o plano operacional e não é o alvo ideal de produção.

Meta:
- reduzir para allowlist de `systemctl`, `journalctl`, Nginx, Docker, APT e comandos estritamente necessários.

Não adicionar `infra-mcp` ao grupo Docker como “correção padrão”. O desenho atual usa `sudo docker`, mantendo a elevação explícita.

## 4. Segredos em env

No plano VPS:
- `env_list_keys` lista nomes/configured sem valores;
- `env_set` recebe valor novo, grava e retorna redigido.

No plano Hostinger:
- API de env Node.js retorna valores mascarados;
- `hostinger_nodejs_env_keys` deve devolver somente nomes;
- nunca copiar `********` para uma operação de escrita;
- replacing env na Hostinger substitui o conjunto inteiro, então essa mutação exige tratamento especial se for implementada semanticamente.

## 5. Leitura de arquivos Shared Hosting

`hostinger_website_file_read`:
- exige path relativo;
- bloqueia traversal;
- bloqueia nomes/sufixos de segredo conhecidos;
- deve ser usada para configuração/texto operacional, não para extração de credenciais.

A própria API Hostinger também pode recusar arquivos grandes, binários, symlinks e conteúdo sensível.

## 6. Autenticação externa do MCP

Endpoint público:
- HTTPS;
- Nginx/gateway;
- header `X-API-Key`;
- upstream em loopback.

Porta 8020 não deve ser publicada diretamente.

Um 401 sem chave é comportamento esperado do gateway protegido e não significa serviço morto.

## 7. Auditoria

Toda mutação deve ser auditada sem:
- tokens;
- senhas;
- private keys;
- valores env;
- conteúdo secreto.

## 8. Shared Hosting e produção

Cadastro Hostinger não define produção.

Exemplo crítico:
- VPClick ainda existe na Hostinger com Git ativo;
- produção real está em Docker na VPS.

Nunca deletar recurso legado sem confirmar DNS, runtime, dependências e rollback.

## 9. Shell arbitrário

`infra_exec_command`:
- desabilitado por padrão;
- exige `INFRA_ALLOW_BREAK_GLASS=true`;
- exige `BREAK_GLASS`;
- exige razão;
- só usar quando nenhuma tool semântica adequada atender.

## 10. Arquitetura resiliente

O Infrastructure MCP ainda está na VPS que administra. Isso aumenta blast radius. O desenho futuro deve mover o control plane para outro host.
