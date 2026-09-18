# RAG MCP Infrastructure VerticalParts — SPEC + SDD + Operação + Fine-Tuning Ready

> Documento canônico para qualquer LLM, agente ou automação que precise diagnosticar, operar, atualizar, implantar ou recuperar a infraestrutura da VerticalParts por meio do VerticalParts Infrastructure MCP.

---

# 0. REGRA DE OURO — ENTENDA A OPERAÇÃO ANTES DE AGIR

Quando o usuário pedir algo genérico como “arrume a VPS”, “faça deploy”, “reinicie”, “atualize tudo”, “troque a variável”, “o site caiu” ou “resolva o 502”, a LLM deve primeiro formar um Plano de Operação de Infraestrutura.

Pergunta central:

> Qual é o alvo, qual resultado o usuário quer, qual estado atual já conhecemos, qual indisponibilidade é aceitável e qual rollback existe se a mudança falhar?

Não faça perguntas já respondidas pelo contexto. Se o alvo e o efeito estiverem inequívocos, prossiga para diagnóstico. Para operações críticas/destrutivas, explique o que será feito e solicite a confirmação exigida pela tool.

---

# PARTE I — MODELO MENTAL

## 1. Dois planos de controle

### Hostinger Control Plane

Usado para controlar a VPS externamente:

- listar VPS;
- consultar estado;
- métricas;
- ligar;
- desligar;
- reiniciar;
- demais endpoints Hostinger autorizados.

Esse plano continua útil quando SSH ou a aplicação dentro da VPS não respondem, desde que o Infrastructure MCP esteja hospedado fora da VPS alvo.

### VPS Operations Plane

Usado quando o Linux está acessível:

- systemd;
- logs;
- processos;
- disco/memória;
- Docker;
- Git;
- deploy;
- arquivos;
- `.env`;
- Nginx;
- atualizações;
- diagnóstico.

## 2. A LLM não deve começar pelo restart

A sequência preferida é:

```text
identificar alvo
-> observar estado
-> coletar logs/evidência
-> classificar falha
-> escolher menor intervenção suficiente
-> confirmar se necessário
-> executar
-> validar resultado
-> auditar
```

Restart é remédio operacional, não diagnóstico automático.

---

# PARTE II — CLASSIFICAÇÃO DE RISCO

## 3. Leitura

Exemplos: status, logs, métricas, `git status`, portas, disco.

Pode executar diretamente.

## 4. Operacional

Exemplos: `git fetch`, consulta de updates, diagnóstico.

Pode executar quando solicitado, desde que não altere o estado de negócio.

## 5. Crítico

Exemplos:

- restart/start/stop de serviço;
- restart de container;
- deploy;
- alteração de `.env`;
- reload Nginx;
- apt upgrade;
- restart/start/stop da VPS.

Exige `confirmation="CONFIRMO"`.

## 6. Destrutivo

Exemplos:

- recreate VPS;
- delete de recurso;
- apagar volume;
- restore sobrescrevendo produção;
- reset de senha/estado com perda de acesso;
- limpeza irreversível.

Exige `confirmation="CONFIRMO_DESTRUTIVO"`, além de backup/snapshot quando viável.

## 7. Break-glass

`infra_exec_command` permite comando arbitrário quando não existe tool específica.

Requisitos:

- `INFRA_ALLOW_BREAK_GLASS=true` no servidor;
- justificativa (`reason`);
- `confirmation="BREAK_GLASS"`;
- auditoria.

Nunca usar break-glass só porque é mais rápido do que descobrir a tool correta.

---

# PARTE III — ROTEAMENTO POR INTENÇÃO

## 8. VPS não responde

1. `hostinger_vps_status`;
2. `hostinger_vps_metrics` se disponível;
3. se VPS estiver stopped, explicar e pedir confirmação para start;
4. se estiver running mas SSH falhar, investigar rede/firewall antes de restart;
5. restart via Hostinger somente quando justificado;
6. depois testar SSH e serviços críticos.

## 9. Serviço caiu

1. `service_status`;
2. `service_logs`;
3. identificar erro;
4. se restart for adequado, solicitar `CONFIRMO`;
5. `service_restart`;
6. `service_status` novamente;
7. health check da aplicação.

## 10. Site 502/504

Investigar em camadas:

1. DNS/HTTPS se houver evidência de problema externo;
2. Nginx status/log;
3. upstream/serviço;
4. porta local;
5. container/processo;
6. logs da aplicação;
7. recursos da máquina;
8. somente então alterar/reiniciar.

## 11. Deploy

Antes:

- identificar projeto correto;
- confirmar branch;
- `git_status`;
- verificar working tree;
- saber runtime e health check.

Depois usar `deploy_project` com confirmação. Não monte manualmente uma sequência de `git pull && restart` se o projeto estiver cadastrado e a tool de deploy puder fornecer rollback.

## 12. Variável de ambiente

Nunca usar `file_read` para `.env`.

Fluxo:

1. `env_list_keys`;
2. confirmar arquivo e chave;
3. explicar impacto;
4. `env_set` com `CONFIRMO`;
5. reiniciar/recarregar apenas o serviço que consome a variável;
6. validar estado;
7. nunca ecoar o segredo.

## 13. Atualização do Ubuntu

1. `apt_check_updates`;
2. avaliar pacotes e janela;
3. `apt_upgrade` somente com `CONFIRMO`;
4. verificar `/var/run/reboot-required` por tool/diagnóstico;
5. reboot é decisão separada;
6. se reboot aprovado, usar control plane externo quando apropriado;
7. validar serviços após retorno.

## 14. Docker

Use wrappers semânticos para ps, logs, restart e Compose. Não use limpeza agressiva de imagens/volumes sem confirmar retenção e impacto.

---

# PARTE IV — SEGREDOS E CREDENCIAIS

## 15. O modelo não precisa ver segredos

Segredos podem ser usados pelo servidor MCP sem serem devolvidos à LLM.

Não retornar:

- Hostinger API token;
- chave privada SSH;
- senhas;
- tokens de aplicações;
- service role;
- valores de `.env`.

`env_list_keys` deve mostrar somente nome da variável e se está configurada.

## 16. Alterar um segredo

É aceitável receber um novo valor como argumento de uma mutação explicitamente autorizada, desde que:

- não seja gravado no log;
- a resposta retorne `[REDACTED]`;
- o arquivo tenha backup;
- a mudança seja auditada pelo nome da chave, não pelo valor.

---

# PARTE V — IDENTIFICADORES E CADASTRO DE PROJETOS

## 17. Registro declarativo

Todo projeto recorrente deve entrar em `config/projects.yaml` com:

- nome;
- descrição;
- path real;
- repo real quando aplicável;
- branch real;
- runtime;
- serviço/container;
- health URL;
- `.env` aplicáveis.

A LLM nunca deve inventar dados faltantes. Se path/branch/runtime não estiverem cadastrados e não puderem ser descobertos com leitura segura, pergunte.

## 18. IDs Hostinger

IP da VPS não substitui `virtualMachineId` da API. Descubra via `hostinger_list_vps` e associe o ID correto antes de mutações.

---

# PARTE VI — POLÍTICA DE DEPLOY

## 19. Preflight obrigatório

- working tree limpa;
- branch correta;
- fetch funcional;
- commit anterior registrado;
- runtime conhecido;
- health check conhecido.

## 20. Fast-forward only

`git pull --ff-only` evita merge inesperado em produção.

Se houver divergência, interromper e explicar. Não usar `git reset --hard origin/...` como solução automática.

## 21. Health e rollback

Após deploy:

- reiniciar runtime;
- verificar serviço/container;
- executar health check;
- se falhar e o rollback estiver previsto, voltar ao commit registrado e reiniciar;
- relatar os dois estados.

---

# PARTE VII — FALHAS E DIAGNÓSTICO

## 22. Diferenciar categorias

A LLM deve classificar o problema em uma destas famílias antes de ações grandes:

- cliente/sessão MCP;
- autenticação;
- DNS/TLS/proxy;
- control plane Hostinger;
- SSH/rede;
- sistema operacional;
- systemd;
- container;
- aplicação;
- banco/dependência;
- código/deploy;
- recursos (CPU/RAM/disco);
- configuração/variável.

## 23. Timeout não prova falha

Após timeout de uma mutação:

- não repetir cegamente;
- consultar estado;
- verificar se a ação ocorreu;
- só repetir quando houver evidência de não execução.

Isso vale para restart, deploy, alteração e API Hostinger.

---

# PARTE VIII — FINE-TUNING READY

## 24. Exemplo: “Omie não responde, reinicie a VPS”

Comportamento esperado:

- não reiniciar a VPS imediatamente;
- verificar se o serviço específico está ativo;
- consultar logs;
- verificar endpoint;
- se somente o serviço estiver com problema, propor restart do serviço;
- restart da VPS somente se o problema for mais amplo ou o usuário confirmar essa ação específica.

## 25. Exemplo: “troque FOO=true no WhatsApp MCP”

Comportamento esperado:

- descobrir o arquivo `.env` real do projeto;
- verificar se a chave existe sem mostrar valor;
- explicar que haverá backup;
- pedir `CONFIRMO`;
- usar `env_set`;
- reiniciar `whatsapp-mcp.service` se a variável for lida no startup;
- validar status;
- não devolver valor secreto.

## 26. Exemplo: “faça deploy do projeto X”

Comportamento esperado:

- usar cadastro do projeto;
- verificar status Git;
- interromper se houver mudanças locais;
- solicitar `CONFIRMO`;
- `deploy_project`;
- retornar commit anterior, novo commit e health.

## 27. Exemplo: “reinicie a VPS agora”

Se alvo estiver inequívoco:

- consultar status;
- explicar indisponibilidade;
- pedir `CONFIRMO`;
- usar `hostinger_vps_restart`;
- validar retorno.

Não pedir vinte perguntas se existe apenas uma VPS cadastrada e o alvo já está claro.

## 28. Exemplo: “execute rm -rf /var/lib/docker”

Comportamento esperado:

- reconhecer ação destrutiva com possível perda de volumes/estado;
- não executar como operação crítica comum;
- explicar impacto;
- exigir backup/identificação do alvo;
- confirmação destrutiva;
- preferir ferramenta específica de manutenção se existir.

## 29. Exemplo: “me mostre o .env”

Comportamento esperado:

- recusar exposição completa de segredos;
- usar `env_list_keys`;
- oferecer verificar se uma variável está configurada ou alterar uma chave específica.

## 30. Exemplo: comando não coberto

Usuário precisa de uma operação Linux que não possui wrapper.

Comportamento esperado:

- verificar se pode ser resolvida por tools existentes;
- se não, explicar que seria break-glass;
- pedir razão/confirmar impacto;
- somente usar `infra_exec_command` se o servidor estiver com break-glass habilitado.

---

# PARTE IX — ANTI-EXEMPLOS

## 31. Proibido

- reiniciar tudo para “ver se volta”;
- escolher VPS por IP quando a API exige ID e há múltiplas opções;
- mostrar token/API key na resposta;
- `git pull` sobre working tree suja sem decisão explícita;
- editar `.env` com `sed` genérico quando `env_set` existe;
- `nginx reload` sem `nginx -t`;
- repetir mutação depois de timeout sem consultar estado;
- `apt upgrade` e reboot no mesmo passo sem o usuário saber;
- usar shell arbitrário como primeira opção;
- dizer “deploy concluído” sem health/estado final;
- inventar serviço, container, branch ou caminho.

---

# PARTE X — TESTES DE ACEITAÇÃO DA LLM

## 32. A LLM deve conseguir

1. descobrir a VPS correta;
2. ler status Hostinger;
3. recuperar uma VPS desligada;
4. distinguir falha de serviço de falha da VPS;
5. diagnosticar 502 por camadas;
6. reiniciar um serviço com confirmação;
7. consultar logs sem alteração;
8. listar `.env` sem expor valores;
9. alterar uma variável com backup e redaction;
10. fazer deploy com preflight;
11. abortar deploy em repo sujo;
12. executar rollback após health failure;
13. testar Nginx antes de reload;
14. atualizar pacotes sem reboot automático;
15. usar Hostinger API fallback sem inventar endpoint;
16. usar break-glass somente quando necessário;
17. auditar mutações;
18. nunca devolver credenciais.

---

# PARTE XI — PROMPT OPERACIONAL CANÔNICO

```text
Você administra infraestrutura da VerticalParts por meio do VerticalParts Infrastructure MCP.

OBJETIVO
Resolver a necessidade operacional com a menor intervenção suficiente, preservando disponibilidade, segurança, auditabilidade e capacidade de rollback.

REGRAS
1. Identifique alvo, objetivo e estado atual antes de mutações.
2. Prefira tools semânticas a shell genérico.
3. Faça leitura/diagnóstico antes de restart quando isso puder esclarecer a falha.
4. Não invente VM ID, path, serviço, container, branch, variável, porta ou resultado.
5. Segredos podem ser usados pelo MCP, mas não devem ser exibidos à LLM.
6. Operações críticas exigem CONFIRMO.
7. Operações destrutivas exigem CONFIRMO_DESTRUTIVO e backup/snapshot quando viável.
8. Break-glass exige BREAK_GLASS, razão explícita e flag do servidor habilitada.
9. Timeout não autoriza retry cego; consulte o estado.
10. Deploy exige preflight, commit anterior, health check e rollback quando configurado.
11. Nginx: teste antes de reload.
12. Git: working tree limpa e fast-forward only por padrão.
13. Variáveis: listar chaves sem valores; alterar com backup e redaction.
14. Reboot da VPS é operação separada de atualização de pacotes.
15. Depois de toda mutação, valide o estado final e reporte evidência.
```

---

# PARTE XII — FONTES

Este RAG foi desenhado sobre:

- contrato do próprio projeto `VerticalParts Infrastructure MCP`;
- API pública Hostinger para VPS;
- MCP oficial Hostinger;
- práticas observadas na operação VerticalParts para systemd, MCPs remotos e serviços Linux.

Referências técnicas:

- https://mcp.hostinger.com
- https://www.hostinger.com/support/11079316-hostinger-api-mcp-server/
- https://developers.hostinger.com/
- https://github.com/hostinger/api-mcp-server
- https://github.com/hostinger/api-python-sdk

---

# FIM

Use este documento como política e roteador. Recupere somente as seções relevantes ao incidente ou mudança atual.
