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

## 11. Firewall (adicionado 2026-09-19)

Achado real: o `ufw` estava **totalmente inativo** (`iptables -L INPUT` com policy `ACCEPT`, sem nenhuma regra) — toda porta que qualquer processo abrisse em `0.0.0.0` ficava acessível pela internet inteira, sem nenhum filtro. Não era um estado teórico: o proxy Tor SOCKS aberto na porta 9050 (ver seção 12) tinha evidência real de abuso (~15 mil conexões, ~360MB) justamente por causa disso.

Corrigido: `ufw` ativo, `default deny incoming`, liberado apenas `22/tcp`, `80/tcp`, `443/tcp` (+ IPv6). Regra: minimizar exposição direta — serviço interno deve ouvir em `127.0.0.1:PORTA` e passar por Nginx como gateway (TLS + auth), não ser exposto direto em `0.0.0.0`. Antes de liberar uma porta nova no firewall, perguntar se ela realmente precisa ser alcançável da internet.

Tools: `firewall_status` (leitura), `firewall_allow`/`firewall_delete_rule` (crítico, `CONFIRMO`). Cruzar sempre com `infra_listening_ports` para saber o que está de fato escutando, já que firewall e bind de porta são camadas independentes — uma pode estar certa e a outra errada.

## 12. Tor e Cloudflare WARP (adicionado 2026-09-19)

Achado: `tor@default.service` estava com `SocksPort 0.0.0.0:9050` no `/etc/tor/torrc` — o padrão do pacote é `127.0.0.1`, então essa era uma alteração deliberada de alguém, não configuração de fábrica. Combinado com o firewall inativo (seção 11), isso deixou um proxy SOCKS aberto exposto à internet, com evidência real de tráfego de abuso nos logs do próprio Tor. `warp-svc.service` (Cloudflare WARP) estava instalado e ativo, mas nunca chegou a ser configurado (nunca aceitou os termos de serviço) — inerte, mas ocupando espaço de superfície de ataque à toa.

Nenhum script/serviço conhecido do stack VerticalParts dependia de nenhum dos dois (busca por `torsocks`, `:9050`, `socks5`, `warp-cli`, `1.1.1.1` em todos os projetos conhecidos não retornou nada).

Ação: ambos parados e desabilitados (`systemctl disable`), pacotes mantidos no sistema (reversível). Lição: um serviço instalado e habilitado não é evidência de uso — verificar configuração customizada, consumidores reais no código e logs de tráfego antes de decidir manter ou desativar.

## 13. Path traversal em tools de arquivo (achado e corrigido 2026-09-19)

Achado por review automatizado (Codex) no PR que introduziu `file_delete`: `SSHRunner.assert_allowed_path` fazia checagem léxica por prefixo de string. Um caminho como `/opt/../etc/hostname` passava por começar com `/opt/` (uma raiz permitida), mas o shell remoto resolvia esse caminho para fora da raiz antes de executar `sudo rm -rf` — ou seja, um `file_delete` confirmado corretamente pelo operador (`CONFIRMO_DESTRUTIVO` no alvo certo) ainda assim poderia apagar qualquer caminho acessível a root, fora do que o operador pretendia.

Corrigido em duas camadas:
1. `assert_allowed_path` agora rejeita qualquer caminho com segmento `..`, o que corrige o vetor para **todas** as tools que passam por ali (`file_read`, `file_write`, `git_status/log/fetch/pull`, `docker_compose_action`), não só `file_delete`.
2. `file_delete` especificamente também resolve o caminho real no host remoto via `realpath -m` (que segue symlinks) e revalida esse caminho resolvido contra as raízes permitidas antes de montar o comando de remoção — fecha também o vetor de um symlink intermediário apontando pra fora da árvore permitida, que a checagem léxica sozinha não detecta.

## 13A. Credencial exposta em log de container (achado 2026-09-19)

O log de inicialização do container `hermes-agent-god7` (agente de terminal remoto do template Hostinger, ttyd — não confundir com "Hermes AI Agent" da NousResearch) expunha a credencial de acesso ao terminal web em base64 diretamente no log (`docker logs`). Não reproduzimos o valor em nenhum documento. O container foi removido em 2026-09-19 por decisão do operador (sem uso relevante — uma única sessão real registrada em meses, e o Traefik do host não tinha rota externa funcional até ele), o que elimina a exposição residual. Backup completo preservado fora do Git, em `/root/hermes-agent-god7-backup-*.tar.gz` na VPS.

## 13B. Gateway sem autenticação em `mcp.vpsistema.com` (achado e corrigido 2026-09-19)

`mcp.vpsistema.com` tem dois `location` no Nginx: `/omie/` (checado) e `/` — catch-all, que faz proxy para `vpprd-mcp` (porta 3100). O segundo não tinha checagem de `X-API-Key`, diferente do padrão usado em `infra-mcp.vpsistema.com` e `whatsapp-mcp.vpsistema.com`. Corrigido com o mesmo padrão (`if ($http_x_api_key != "...") { return 401; }`), chave nova em `/root/vpprd-mcp-auth-token` (600, root:root). Importante para avaliação de impacto: o app `vpprd-mcp` já tinha autenticação própria via Bearer token internamente (confirmado testando com a chave de gateway correta — a aplicação ainda devolvia 401 próprio), então a exposição real anterior à correção era menor do que a ausência de X-API-Key sozinha sugeria; ainda assim, a defesa em profundidade no gateway é o padrão consistente do resto da infra e foi aplicada.

## 14. Segredos em observabilidade de processo (achado e corrigido 2026-09-19)

Achado por review automatizado: a primeira versão de `infra_pm2_list` retornava a saída crua de `pm2 jlist`, que inclui `pm2_env.env` — todas as variáveis de ambiente do processo, incluindo eventuais tokens/senhas configurados por essa via. Uma tool de observabilidade não pode ser um vetor de vazamento de segredo só porque a fonte de dados devolve tudo junto.

Corrigido: `infra_pm2_list` agora retorna uma projeção fixa de campos operacionais (`pm_id`, `name`, `pid`, `status`, `restart_time`, `uptime_since`, `cwd`, `exec_interpreter`, `monit`) e nunca inclui `pm2_env.env`.
