import os
import discord
import lamdabotweb.settings as config
from django.core.management import BaseCommand
from discordbot.util import get_prefix
from lamdabotweb.settings import BASE_DIR
from discord.ext import commands
from discord.ext.commands import CommandInvokeError, CommandOnCooldown, DisabledCommand, MissingPermissions, \
    BotMissingPermissions, CheckFailure
from discordbot.models import DiscordServer, DiscordContext, DiscordUser, DiscordChannel, DiscordImage
from util import log, log_exc


class Command(BaseCommand):
    help = 'Starts the discord bot'
    bot = None

    def handle(self, *args, **options):
        bot = commands.Bot(command_prefix=get_prefix, description='I make memes.', case_insensitive=True)

        @bot.event
        async def on_guild_join(server: discord.Guild):
            log('joining server:', server)
            DiscordServer.objects.update_or_create(server_id=str(server.id), defaults={'name': server.name})

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
            await bot.change_presence(activity=discord.Game(name=config.DISCORD_STATUS))

        @bot.event
        async def on_message(msg: discord.Message):
            ctx = await bot.get_context(msg, cls=DiscordContext)
            if ctx.is_blacklisted:
                return
            if len(ctx.images) > 0:
                DiscordChannel.objects.filter(channel_id=ctx.channel.id).update(recent_image=ctx.images[0].url)
            if ctx.valid:
                await bot.invoke(ctx)

        @bot.event
        async def on_message_edit(_, msg: discord.Message):
            ctx = await bot.get_context(msg, cls=DiscordContext)
            if ctx.is_blacklisted:
                return
            image = DiscordImage.from_message(msg, just_one=True)
            if image:
                DiscordChannel.objects.filter(channel_id=msg.channel.id).update(recent_image=image.url)

        @bot.event
        async def on_command_error(ctx: DiscordContext, exc):
            if isinstance(exc, CommandOnCooldown):
                msg = "You're memeing too fast! Please wait {} seconds.".format(int(exc.retry_after))
            elif isinstance(exc, DisabledCommand):
                msg = "`{}` is disabled here".format(ctx.command)
            elif isinstance(exc, MissingPermissions):
                msg = "You need the following permissions to use this command: `{}`".format(', '.join(exc.missing_perms))
            elif isinstance(exc, BotMissingPermissions):
                msg = "The bot needs the following permissions for this command: `{}`".format(', '.join(exc.missing_perms))
            elif isinstance(exc, CheckFailure):
                msg = ""
            elif isinstance(exc, CommandInvokeError):
                log_exc(exc, ctx)
                msg = "error :cry:"
            else:
                if config.DEBUG:
                    log_exc(exc, ctx)
                msg = str(exc) or "error :cry:"
            if msg and ctx.channel_data is not None:  # null ctx.channel_data means no permission to send messages
                await ctx.send("{} :warning: {}".format(ctx.author.mention, msg))

        print('loading cogs: ', end='')
        for cog_name in os.listdir(os.path.join(BASE_DIR, 'discordbot', 'cogs')):
            cog_name, _ = os.path.splitext(cog_name)
            if cog_name and not cog_name.startswith('__'):
                print(cog_name, end=' ')
                bot.load_extension('discordbot.cogs.' + cog_name)
        print()

        bot.run(config.DISCORD_TOKEN)
