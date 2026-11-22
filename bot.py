import os
import discord
from discord import app_commands
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)


async def ensure_category(guild: discord.Guild, name: str):
    category = discord.utils.get(guild.categories, name=name)
    if category is None:
        category = await guild.create_category(name, reason="SERVER BUILDER AI setup")
    return category


async def ensure_text_channel(category: discord.CategoryChannel, name: str, topic=None):
    channel = discord.utils.get(category.text_channels, name=name)
    if channel is None:
        channel = await category.create_text_channel(
            name, topic=topic, reason="SERVER BUILDER AI setup"
        )
    return channel


async def ensure_role(guild: discord.Guild, name: str, permissions=None):
    role = discord.utils.get(guild.roles, name=name)
    if role is None:
        role = await guild.create_role(
            name=name,
            permissions=permissions or discord.Permissions.none(),
            reason="SERVER BUILDER AI setup",
        )
    return role


class TicketButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Abrir atendimento",
        style=discord.ButtonStyle.green,
        custom_id="server_builder_ai:open_ticket",
        emoji="🎫",
    )
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        if guild is None:
            return await interaction.response.send_message(
                "Use este botão dentro de um servidor.", ephemeral=True
            )

        existing = discord.utils.get(
            guild.text_channels, name=f"ticket-{interaction.user.id}"
        )
        if existing:
            return await interaction.response.send_message(
                f"Você já tem um ticket aberto: {existing.mention}", ephemeral=True
            )

        category = discord.utils.get(guild.categories, name="ATENDIMENTO")
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(
                view_channel=True, send_messages=True, read_message_history=True
            ),
            guild.me: discord.PermissionOverwrite(
                view_channel=True, send_messages=True, manage_channels=True
            ),
        }
        support_role = discord.utils.get(guild.roles, name="Suporte")
        if support_role:
            overwrites[support_role] = discord.PermissionOverwrite(
                view_channel=True, send_messages=True, read_message_history=True
            )

        channel = await guild.create_text_channel(
            f"ticket-{interaction.user.id}",
            category=category,
            overwrites=overwrites,
            reason="Ticket aberto pelo painel",
        )
        await channel.send(
            f"{interaction.user.mention}, descreva como podemos ajudar. "
            "A equipe de suporte responderá aqui."
        )
        await interaction.response.send_message(
            f"Ticket criado: {channel.mention}", ephemeral=True
        )


@bot.event
async def on_ready():
    bot.add_view(TicketButton())
    try:
        synced = await bot.tree.sync()
        print(f"Conectado como {bot.user}. {len(synced)} comandos sincronizados.")
    except Exception as error:
        print(f"Falha ao sincronizar comandos: {error}")


@bot.tree.command(name="criar_servidor", description="Monta a estrutura de um servidor.")
@app_commands.describe(modelo="Escolha o modelo de servidor")
@app_commands.choices(modelo=[
    app_commands.Choice(name="Loja", value="loja"),
    app_commands.Choice(name="Comunidade", value="comunidade"),
    app_commands.Choice(name="Gamer", value="gamer"),
    app_commands.Choice(name="RP", value="rp"),
])
@app_commands.default_permissions(manage_guild=True)
@app_commands.guild_only()
async def criar_servidor(interaction: discord.Interaction, modelo: app_commands.Choice[str]):
    guild = interaction.guild
    if guild is None:
        return await interaction.response.send_message("Comando apenas em servidores.", ephemeral=True)

    me = guild.me
    if me is None or not me.guild_permissions.manage_channels or not me.guild_permissions.manage_roles:
        return await interaction.response.send_message(
            "Preciso das permissões Gerenciar Canais e Gerenciar Cargos.", ephemeral=True
        )

    await interaction.response.defer(ephemeral=True, thinking=True)

    if modelo.value == "loja":
        await ensure_role(guild, "Cliente")
        await ensure_role(guild, "Suporte")
        sections = {
            "📌 INFORMAÇÕES": ["boas-vindas", "regras", "anuncios"],
            "🛒 LOJA": ["catalogo", "produtos", "como-comprar", "pedidos"],
            "🎫 ATENDIMENTO": ["abrir-ticket"],
        }
    elif modelo.value == "comunidade":
        await ensure_role(guild, "Membro")
        await ensure_role(guild, "Moderador")
        sections = {
            "📌 INFORMAÇÕES": ["boas-vindas", "regras", "anuncios"],
            "💬 COMUNIDADE": ["geral", "midia", "sugestoes"],
            "🔊 VOZ": [],
        }
    elif modelo.value == "gamer":
        await ensure_role(guild, "Player")
        await ensure_role(guild, "Equipe")
        sections = {
            "📌 INFORMAÇÕES": ["regras", "anuncios"],
            "🎮 GAMER": ["geral", "procurar-equipe", "clips", "eventos"],
            "🔊 VOZ": [],
        }
    else:
        await ensure_role(guild, "Cidadão")
        await ensure_role(guild, "Polícia")
        await ensure_role(guild, "Hospital")
        sections = {
            "📌 INFORMAÇÕES": ["regras", "anuncios"],
            "🏙️ CIDADE": ["chat-cidade", "empregos", "comercio"],
            "🚨 SERVIÇOS": ["policia", "hospital", "prefeitura"],
        }

    created = []
    for category_name, channels in sections.items():
        category = await ensure_category(guild, category_name)
        created.append(category.name)
        for channel_name in channels:
            await ensure_text_channel(category, channel_name)
            created.append(f"#{channel_name}")

    await interaction.followup.send(
        "Estrutura configurada! Itens criados ou já existentes:\n"
        + "\n".join(f"• {item}" for item in created),
        ephemeral=True,
    )


@bot.tree.command(name="configurar_tickets", description="Cria o painel de atendimento por tickets.")
@app_commands.default_permissions(manage_guild=True)
@app_commands.guild_only()
async def configurar_tickets(interaction: discord.Interaction):
    guild = interaction.guild
    if guild is None:
        return await interaction.response.send_message("Use em um servidor.", ephemeral=True)
    if not guild.me or not guild.me.guild_permissions.manage_channels:
        return await interaction.response.send_message("Preciso de Gerenciar Canais.", ephemeral=True)

    category = await ensure_category(guild, "ATENDIMENTO")
    panel = await ensure_text_channel(category, "abrir-ticket")
    await panel.send(
        "Precisa de ajuda? Clique no botão abaixo para abrir um canal privado.",
        view=TicketButton(),
    )
    await interaction.response.send_message(
        f"Painel publicado em {panel.mention}.", ephemeral=True
    )


@bot.tree.command(name="painel_vendas", description="Publica um modelo de painel para sua loja.")
@app_commands.describe(produto="Nome do produto", preco="Preço e moeda, por exemplo R$ 10,00", detalhes="Descrição curta")
@app_commands.default_permissions(manage_guild=True)
@app_commands.guild_only()
async def painel_vendas(
    interaction: discord.Interaction, produto: str, preco: str, detalhes: str
):
    embed = discord.Embed(title=produto, description=detalhes, color=discord.Color.blurple())
    embed.add_field(name="Preço", value=preco, inline=False)
    embed.set_footer(text="Para comprar, abra um ticket com a equipe da loja.")
    await interaction.response.send_message(embed=embed)


if not TOKEN:
    raise RuntimeError("Defina a variável DISCORD_TOKEN antes de iniciar o bot.")

bot.run(TOKEN)
