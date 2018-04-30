import asyncio
import os
import re
import discord
import lamdabotweb.settings as config
from django.core.management import BaseCommand
from discordbot.util import get_prefix
from lamdabotweb.settings import BASE_DIR
from discord.ext import commands
from discord.ext.commands import CommandInvokeError, CommandOnCooldown, MissingPermissions
from discordbot.models import DiscordServer, DiscordContext, DiscordUser, DiscordChannel
from util import log, log_exc


class Command(BaseCommand):
    help = 'Starts the discord bot'
    bot = None

    def handle(self, *args, **options):
        bot = commands.Bot(command_prefix=get_prefix, description='I make memes.')

        @bot.event
        async def on_guild_join(server: discord.Guild):
            log('joining server:', server)
            s = DiscordServer.objects.get_or_create(server_id=server.id)[0]
            s.name = server.name
            s.save()

        @bot.event
        async def on_member_update(_, member: discord.Member):
            DiscordUser.objects.filter(user_id=member.id).update(name=member.name)

        @bot.event
        async def on_guild_update(_, server: discord.Guild):
            DiscordServer.objects.filter(server_id=server.id).update(name=server.name)

        @bot.event
        async def on_guild_channel_update(_, channel):
            DiscordChannel.objects.filter(channel_id=channel.id).update(name=channel.name)

        @bot.event
        async def on_private_channel_update(_, channel):
            DiscordChannel.objects.filter(channel_id=channel.id).update(name='DM-' + str(channel.id))

        @bot.event
        async def on_ready():
            log('Logged in as', bot.user.name, bot.user.id)
            print('\n'.join(map(lambda x: '        {} {}'.format(x.id, x.name), bot.guilds)))
            await bot.change_presence(activity=discord.Game(name=config.DISCORD_STATUS))

        @bot.event
        async def on_message(msg: discord.Message):
            if re.search("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", msg.content) is not None:
                await asyncio.sleep(2)

            ctx = await bot.get_context(msg, cls=DiscordContext)
            if len(ctx.images) > 0:
                DiscordChannel.objects.filter(channel_id=ctx.channel.id).update(recent_image=ctx.images[0].url)
            if ctx.valid:
                await bot.invoke(ctx)

        @bot.event
        async def on_command_error(ctx: DiscordContext, exc):
            if isinstance(exc, CommandOnCooldown):
                await ctx.send("{0} you're memeing too fast! Please wait {1} seconds.".format(ctx.author.mention, int(exc.retry_after)))
            elif isinstance(exc, MissingPermissions) and 'send_messages' in exc.missing_perms:
                pass
            elif isinstance(exc, CommandInvokeError):
                log_exc(exc)
                await ctx.send("{} error :cry:".format(ctx.author.mention))
            elif ctx.channel_data is not None:
                await ctx.send("{} {}".format(ctx.author.mention, str(exc) or "error :cry:"))

        print('loading cogs: ', end='')
        for cog_name in os.listdir(os.path.join(BASE_DIR, 'discordbot', 'cogs')):
            cog_name, _ = os.path.splitext(cog_name)
            if cog_name and not cog_name.startswith('__'):
                print(cog_name, end=' ')
                bot.load_extension('discordbot.cogs.' + cog_name)
        print()

        bot.run(config.DISCORD_TOKEN)
