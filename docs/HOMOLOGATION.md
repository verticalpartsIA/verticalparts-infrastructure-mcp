# Homologação — VerticalParts Infrastructure MCP

Versão: 2026-09-19
Status: homologação principal concluída; algumas tools novas ainda exigem teste individual quando forem usadas

## Resultado geral

A cadeia local do MCP foi validada após atualização do código:

- `verticalparts-infra-mcp.service` = `active`;
- MCP `initialize` local funciona;
- `tools/list` retornou **49 tools**;
- `hostinger_ssl_status` foi chamada pelo protocolo MCP real e retornou sucesso;
- autenticação pública por `X-API-Key` já havia sido validada;
- Docker foi corrigido para executar por `sudo docker` / `sudo docker compose`;
- `docker_ps` e Compose `ps` foram homologados;
- `vpclick` foi registrado como runtime Docker com deploy externo via GitHub Actions.

## Hostinger Shared Hosting — descoberta validada

A API de Hosting retornou 14 websites em dois planos.

### Conta Cloud — 9 registros Node.js

Auto-deploy Git Hostinger observado como ativo em todos:

| Domínio | Repositório | Branch |
|---|---|---|
| escamaxcompravp.vpsistema.com | verticalpartsIA/011_EscamaxCompraVP | feat/reskin-verticalparts |
| gentegestao.vpsistema.com | verticalpartsIA/17_gente-gestao | main |
| posvenda360.vpsistema.com | verticalpartsIA/004_sac_posvenda360 | main |
| propostas.vpsistema.com | verticalpartsIA/002_proposta_comercial | main |
| vpclick.vpsistema.com | verticalpartsIA/005_vpclick | main |
| vpdashboarddre.vpsistema.com | verticalpartsIA/bd_omie | main |
| vpgestaoimportacao.vpsistema.com | verticalpartsIA/010_GestaoImportacao | main |
| vprequisicoes.vpsistema.com | verticalpartsIA/003_requisicoes | main |
| vpsistema.com | verticalpartsIA/vpsistema | main |

Atenção: o registro Hostinger do VPClick é legado. A produção canônica de `vpclick.vpsistema.com` está na VPS, em Docker, e seu deploy é GitHub Actions.

### Conta Premium — 5 registros `other`

Os cinco expõem PHP 8.3.33 no plano, mas isso não prova que a aplicação seja PHP.

Arquivos observados no document root:

- `assetmanager.vpsistema.com`: `index.html`, JS/assets e `default.php`;
- `catraca.vpsistema.com`: `index.html` + `assets/`;
- `interativo.vpsistema.com`: `index.html` + diretórios/assets;
- `suporte.vpsistema.com`: `index.html`, `assets/`, `uploads/`, `api.php`;
- `visitas.vpsistema.com`: `index.html`, assets e ZIP histórico de deploy.

Nenhum dos cinco apresentou auto-deploy Git Hostinger configurado.

## VPRequisições — evidências

Validado por API:
- Node.js 22;
- app_type `other`;
- output `dist`;
- build script `build`;
- entry file `server.js`;
- deploy Git de `verticalpartsIA/003_requisicoes`, branch `main`;
- build recente concluído;
- runtime logs endpoint responde;
- SSL ativo;
- HTTPS redirect ativo.

A leitura de `.htaccess` mostrou Passenger apontando para o `hbuilds/current/nodejs`, portanto o código Node ativo é gerenciado pela camada de build da Hostinger e não precisa aparecer no document root.

## Bancos e cron

A API da conta Cloud listou quatro bancos MySQL. Nenhuma senha é retornada pela API. Os registros observados não estavam associados a um domínio por campo `domain`, então não inferir qual aplicação usa qual banco sem outra evidência.

Cron jobs da conta Cloud: lista vazia no momento da auditoria.

## Build logs

O build recente de VPRequisições concluiu, mas registrou avisos de dependência e vulnerabilidades npm. Esses números são sinal de auditoria de dependências, não prova automática de exploração em produção.

## O que foi implementado no MCP

Novas tools semânticas:
- `hostinger_list_orders`;
- `hostinger_website_files`;
- `hostinger_website_file_read`;
- `hostinger_git_autodeploy_status`;
- `hostinger_ssl_status`;
- `hostinger_list_databases`;
- `hostinger_list_cron_jobs`;
- `hostinger_nodejs_settings`;
- `hostinger_nodejs_builds`;
- `hostinger_nodejs_build_logs`;
- `hostinger_nodejs_runtime_logs`;
- `hostinger_nodejs_env_keys`;
- `hostinger_nodejs_vulnerabilities`;
- `hostinger_nodejs_restart`.

O catálogo completo observado passou para 49 tools.

## Escopo do que está realmente homologado

Não declarar que toda tool nova foi testada end-to-end apenas porque aparece em `tools/list`.

Evidência por nível:
- endpoints de arquivos, Git, SSL, bancos, cron, settings, builds e logs foram exercitados diretamente durante a descoberta;
- `hostinger_ssl_status` foi adicionalmente exercitada através do protocolo MCP após o deploy;
- `hostinger_nodejs_restart` não foi executada em produção durante esta homologação;
- env keys e vulnerabilities foram implementadas com base na API oficial, mas devem ser verificadas no primeiro uso real.

## Critério de pronto desta fase

Concluído:
- serviço ativo;
- código sincronizado;
- 49 tools carregadas;
- uma nova tool semântica validada via MCP;
- documentação reconciliada;
- segredos não versionados.

Pendências estruturais:
- reduzir sudo amplo para allowlist granular;
- mover control plane para host independente;
- ampliar testes end-to-end das novas tools conforme uso;
- implementar mais wrappers de mutação apenas quando necessários e com guardrails.
