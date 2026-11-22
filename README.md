# SERVER BUILDER AI

Bot Discord em Python para montar estruturas de servidores por modelos, publicar painéis de venda e abrir tickets privados.

## Recursos
- `/criar_servidor`: modelos Loja, Comunidade, Gamer e RP.
- `/configurar_tickets`: publica um painel com botão para abrir tickets privados.
- `/painel_vendas`: publica um card de produto com preço e descrição.
- Usa a conexão Gateway do Discord por meio de `discord.py`.

## Requisitos
- Python 3.10 ou superior.
- Aplicação e bot criados no Discord Developer Portal.
- Permissões no servidor: Gerenciar Canais, Gerenciar Cargos, Ver Canais e Enviar Mensagens.

## Instalação
1. Instale as dependências: `pip install -r requirements.txt`.
2. Configure a variável de ambiente `DISCORD_TOKEN` com o token do bot.
3. Inicie: `python bot.py`.

Nunca publique o token no GitHub ou envie-o em conversas. Se ele já tiver sido exposto, gere outro no Developer Portal.

## Uso
Convide o bot para um servidor onde você tenha autorização e conceda somente as permissões necessárias. Depois use os comandos slash no servidor.

O bot precisa permanecer em execução para responder aos comandos e aos botões. Este repositório contém o código-fonte; não é um APK nem um serviço hospedado 24 horas.
