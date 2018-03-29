import os
import django
import discord
import lamdabotweb.settings as config
from discord.ext import commands
from django.core.exceptions import ObjectDoesNotExist

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lamdabotweb.settings")
django.setup()

from discordbot.models import DiscordServer
from discordbot.util import log

log("")
log("#####################")
log("#  LambdaBot 3883   #")
log("#####################")
log("")

_bot = commands.Bot(command_prefix=config.DISCORD_CMD_PREFIX, description='I make memes.')

for file in os.listdir(os.path.join(config.BASE_DIR, 'discordbot', 'cogs')):
    if file.startswith('__') or not file.endswith('.py'):
        continue
    _bot.load_extension('discordbot.cogs.' + os.path.splitext(file)[0])


@_bot.event
async def on_member_update(_, member: discord.Member):
    try:
        server_data = DiscordServer.get(member.guild)
        member_data = server_data.get_member(member)
        member_data.update(member)
    except ObjectDoesNotExist:
        pass


@_bot.event
async def on_guild_update(_, server: discord.Guild):
    try:
        server_data = DiscordServer.get(server)
        server_data.update(server.name)
    except ObjectDoesNotExist:
        pass


@_bot.event
async def on_ready():
    log('Logged in as', _bot.user.name, _bot.user.id)
    await _bot.change_presence(activity=discord.Game(name=config.DISCORD_STATUS))


@_bot.check
def check_server_whitelisted(ctx):
    try:
        DiscordServer.get(ctx.message.guild)
        return True
    except ObjectDoesNotExist:
        return False


@_bot.check
def check_mans_not_bot(ctx):
    return not ctx.author.bot


_bot.run(config.DISCORD_TOKEN)
