import os
import django
import discord

import re

import asyncio

import lamdabotweb.settings as config
from discord.ext import commands
from django.core.exceptions import ObjectDoesNotExist

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lamdabotweb.settings")
django.setup()

from discordbot.models import DiscordServer
from discordbot.util import log, DiscordContext

log("")
log("####################")
log("#  LambdaBot 3883  #")
log("####################")
log("")

_bot = commands.Bot(command_prefix=config.DISCORD_CMD_PREFIX, description='I make memes.')

for cog_name in config.DISCORD_COGS:
    _bot.load_extension('discordbot.cogs.' + cog_name)


@_bot.event
async def on_guild_join(server: discord.Guild):
    DiscordServer.get(server, create=True)


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


@_bot.event
async def on_message(msg: discord.Message):
    if re.search("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", msg.content) is not None:
        await asyncio.sleep(2)

    ctx = await _bot.get_context(msg, cls=DiscordContext)
    if ctx.valid:
        await _bot.invoke(ctx)


@_bot.check
def check_mans_not_bot(ctx):
    return not ctx.author.bot


_bot.run(config.DISCORD_TOKEN)
