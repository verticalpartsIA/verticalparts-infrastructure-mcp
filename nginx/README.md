# Proxy HTTPS

O MCP remoto deve ouvir somente em loopback, por exemplo `127.0.0.1:8020`, e ser publicado por um proxy HTTPS autenticado.

Não incluímos segredo hardcoded em configuração Nginx.

Requisitos:

- TLS válido;
- encaminhamento compatível com Streamable HTTP;
- autenticação antes do upstream;
- timeouts adequados para sessões MCP;
- porta 8020 não exposta à Internet.

Para Claude.ai, prefira autenticação suportada pelo conector remoto escolhido. Se usar header secreto, ele deve ser armazenado no mecanismo seguro do cliente/gateway e nunca no Git.
