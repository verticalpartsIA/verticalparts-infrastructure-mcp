# 00 — LEIA PRIMEIRO — VerticalParts Infrastructure MCP

Versão documental: 2026-09-19  
Status: canônico  
Escopo: operação, recuperação, evolução, conexão e onboarding de infraestrutura VerticalParts

## 1. Finalidade deste conjunto

Este repositório contém o MCP de infraestrutura da VerticalParts. Ele existe para permitir que uma LLM opere a infraestrutura com contexto, segurança, diagnóstico, auditoria e rollback, sem depender de memória humana sobre comandos, caminhos, domínios ou arquitetura.

Se uma conexão quebrar daqui a meses, se uma VPS mudar, se um novo site entrar no ar, se um domínio migrar de hospedagem compartilhada para VPS ou se outra LLM assumir a operação, este conjunto documental deve permitir reconstruir o raciocínio e recuperar o serviço.

## 2. Ordem obrigatória de leitura para LLMs

1. `00_READ_FIRST_INFRASTRUCTURE_MCP.md` — mapa e precedência.
2. `03_INSTRUCTIONS_LLM_MCP_INFRASTRUCTURE_VERTICALPARTS.md` — regras de comportamento.
3. `01_RAG_MCP_INFRASTRUCTURE_VERTICALPARTS.md` — conhecimento operacional e roteamento.
4. `02_SPEC_MCP_INFRASTRUCTURE_VERTICALPARTS.md` — requisitos e contratos.
5. `04_SDD_MCP_INFRASTRUCTURE_VERTICALPARTS.md` — desenho técnico.
6. `05_RUNBOOK_COPY_PASTE_RECOVERY_AND_ONBOARDING.md` — execução e recuperação com comandos prontos.
7. `README.md`, `docs/*`, `config/*.example.yaml` e código-fonte para detalhes complementares.

## 3. Hierarquia de verdade

Informações de infraestrutura envelhecem. Em caso de divergência, use esta ordem:

1. Estado vivo observado por leitura segura: DNS, Hostinger API, systemd, Docker, Git, Nginx, health checks.
2. `config/inventory.yaml` do ambiente de execução — inventário operacional privado e autoritativo.
3. `config/projects.yaml` do ambiente de execução — cadastro de projetos operáveis.
4. Código em `src/verticalparts_infra_mcp/`.
5. Documentos canônicos numerados na raiz.
6. Documentos históricos em `docs/` e `rag/`.
7. Memória de conversa ou suposição humana.

Nunca use um documento antigo para sobrescrever silenciosamente evidência atual. Se o estado vivo mudou legitimamente, atualize o inventário e, quando for uma mudança arquitetural, atualize estes documentos.

## 4. Estado operacional conhecido em 2026-09-19

Endpoint público do Infrastructure MCP:

`https://infra-mcp.vpsistema.com/mcp`

Transporte:

`Streamable HTTP`

Processo MCP na homologação atual:

- serviço: `verticalparts-infra-mcp.service`
- bind interno: `127.0.0.1:8020`
- instalação: `/opt/verticalparts-infrastructure-mcp`
- usuário do serviço: `infra-mcp`
- ambiente: `/opt/verticalparts-infrastructure-mcp/.env`
- inventário privado: `/opt/verticalparts-infrastructure-mcp/config/inventory.yaml`
- projetos privados: `/opt/verticalparts-infrastructure-mcp/config/projects.yaml`
- auditoria: `/opt/verticalparts-infrastructure-mcp/data/audit.jsonl`

VPS atualmente administrada:

- provider: Hostinger
- VM ID: `1510643`
- hostname: `srv1510643.hstgr.cloud`
- IPv4: `72.61.48.156`
- Ubuntu 24.04 LTS
- Infrastructure MCP está temporariamente na própria VPS administrada.

Limitação arquitetural conhecida: se essa VPS cair totalmente, o MCP hospedado nela também ficará indisponível. A arquitetura resiliente final deve hospedar o control plane em outro host.

### Homologação operacional de 2026-09-19

Após auditoria prática pelo Claude e correção do runtime:

- o endpoint público respondeu `401` sem `X-API-Key`, como esperado;
- o mesmo endpoint respondeu `200` no `initialize` MCP autenticado;
- `serverInfo.name` respondeu `VerticalParts Infrastructure`;
- `serverInfo.version` respondeu `1.30.0`;
- `docker_ps` passou a executar via `sudo docker` e foi homologado com `exit_status: 0`;
- `docker_compose_action(..., action="ps")` foi homologado em `/docker/vpclick`;
- `vpclick-vpclick-1` foi observado em execução na porta `127.0.0.1:8091->80/tcp`;
- `vpclick` foi incluído no registro privado de projetos do runtime;
- seu runtime é `docker_compose`;
- seu deploy é explicitamente externo, via GitHub Actions, workflow `.github/workflows/deploy-vps.yml`.

O antigo erro `permission denied` no socket Docker não deve ser tratado como estado atual. A implementação foi corrigida para usar o caminho privilegiado já previsto no host. Se o erro reaparecer, trate como regressão de permissão/configuração e valide o código e sudoers antes de alterar grupo Docker.

Uma desconexão momentânea do cliente MCP logo após `systemctl restart verticalparts-infra-mcp.service` é esperada porque sessões Streamable HTTP existentes são encerradas. Se houver reconexão automática e chamadas subsequentes retornarem `200`, isso não caracteriza incidente persistente.

## 5. MCPs canônicos relacionados

Omie remoto:

`https://mcp.vpsistema.com/omie/mcp`

WhatsApp remoto:

`https://whatsapp-mcp.vpsistema.com/mcp`

Infrastructure remoto:

`https://infra-mcp.vpsistema.com/mcp`

Omie local de desenvolvimento no Windows:

`C:\Users\gelso\omie-mcp\omie-mcp-global.cmd`

O Omie local não é o Omie remoto. Problema no `omie-verticalparts` do Claude Code deve ser tratado primeiro como problema local/sessão Windows, não como falha da VPS.

## 6. Regra arquitetural de Docker

Estado atual e regra operacional:

- VPClick é o projeto de aplicação intencionalmente executado em Docker na VPS.
- Não assumir Docker para VPRequisições ou para novos projetos.
- Um novo site só deve ser containerizado se sua arquitetura explicitamente exigir Docker.
- Hospedagem compartilhada Hostinger, systemd/Node/Python e site estático são destinos válidos e devem ser avaliados antes de escolher Docker.

A LLM não deve converter um projeto para Docker apenas por conveniência operacional.

## 7. Domínios e ambientes — princípio

O fato de um site aparecer na API de Websites da Hostinger não prova que ele recebe tráfego de produção. A fonte de verdade para localização pública é a combinação:

`DNS atual + inventário operacional + runtime real + health`

Exemplo conhecido: `vpclick.vpsistema.com` ainda pode aparecer cadastrado no shared hosting, mas a produção foi migrada para a VPS e o DNS aponta para `72.61.48.156`.

Também podem existir configurações Nginx antigas na VPS para domínios cuja produção já está no shared hosting. Configuração existente não significa produção ativa.

## 8. Segredos

Nunca versionar nem reproduzir valores de:

- `HOSTINGER_API_TOKEN`;
- `X-API-Key` do Infrastructure MCP;
- `X-API-Key` do WhatsApp MCP;
- chaves privadas SSH;
- PATs do GitHub;
- senhas;
- service-role keys;
- valores de `.env`.

É permitido documentar o local seguro de recuperação do segredo e o comando para lê-lo no host autorizado.

Infrastructure MCP auth token:

`/root/infra-mcp-auth-token`

WhatsApp MCP auth token:

`/root/whatsapp-mcp-auth-token`

A documentação nunca deve conter o valor.

## 9. Confirmações de risco

- leitura: sem confirmação;
- crítico/reversível: `CONFIRMO`;
- destrutivo: `CONFIRMO_DESTRUTIVO`;
- shell arbitrário: `BREAK_GLASS` e `INFRA_ALLOW_BREAK_GLASS=true`.

O break-glass deve permanecer desligado normalmente.

## 10. Protocolo de boot mental da LLM

Ao assumir um incidente ou mudança:

1. identificar qual ambiente está em questão;
2. consultar `infra_inventory`;
3. consultar estado vivo do alvo;
4. reconciliar estado vivo versus inventário;
5. classificar falha;
6. escolher a menor intervenção suficiente;
7. obter confirmação quando exigida;
8. executar;
9. validar;
10. atualizar inventário/documentação se a topologia mudou.

## 11. Quando um novo site entrar no ar

Nunca apenas “subir o site”. A LLM deve completar a cadeia:

`classificar ambiente -> registrar projeto -> deploy -> runtime -> DNS -> proxy/TLS quando aplicável -> health -> inventário -> observabilidade -> teste externo -> documentação`

O runbook completo está em `05_RUNBOOK_COPY_PASTE_RECOVERY_AND_ONBOARDING.md`.

## 12. Fontes externas de referência

Anthropic — conectores MCP remotos:
https://support.claude.com/pt/articles/11175166-comece-com-conectores-personalizados-usando-mcp-remoto

Anthropic — conectores:
https://support.claude.com/pt/articles/11176164-use-conectores-para-estender-os-recursos-do-claude

Hostinger API:
https://developers.hostinger.com/

Hostinger MCP/API:
https://www.hostinger.com/support/11079316-hostinger-api-mcp-server/

Hostinger remote MCP:
https://mcp.hostinger.com

## 13. Regra final

Este repositório não é apenas código de um MCP. Ele é o manual de continuidade operacional da infraestrutura VerticalParts.

Uma LLM que leia os arquivos canônicos deve conseguir:
- entender a topologia;
- descobrir o estado real;
- recuperar o conector;
- recuperar um serviço;
- conectar Claude novamente;
- adicionar um novo site;
- migrar um site entre ambientes;
- atualizar o inventário;
- operar sem revelar segredos;
- saber quando parar e pedir confirmação.
