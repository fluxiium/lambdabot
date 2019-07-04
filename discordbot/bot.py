import logging
import os
import discord
from discord import Message
from discord.ext import commands
from discord.ext.commands import CommandInvokeError, CommandOnCooldown, DisabledCommand, MissingPermissions, \
    BotMissingPermissions, CheckFailure, CommandError, MissingRequiredArgument
from discordbot.help import HelpCommand
from util import log_exc
from discordbot.models import DiscordServer, DiscordContext, DiscordUser, DiscordChannel, DiscordImage
from discordbot import settings


def get_prefix(_, msg: Message):
    if msg.guild:
        try:
            return DiscordServer.objects.get(server_id=str(msg.guild.id)).prefix
        except DiscordServer.DoesNotExist:
            pass
    return '!'

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
bot = commands.Bot(command_prefix=get_prefix, case_insensitive=True, help_command=HelpCommand())

@bot.event
async def on_guild_join(server: discord.Guild):
    logging.info(f'joining server: {server}')
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
    logging.info(f'Logged in as {bot.user}, {bot.user.id}')
    await bot.change_presence(activity=discord.Game(name=settings.DISCORD_STATUS))

@bot.event
async def on_message(msg: discord.Message):
    ctx = await bot.get_context(msg, cls=DiscordContext)
    ctx.images = await DiscordImage.from_message(msg)
    if ctx.is_blacklisted:
        return
    if len(ctx.images) > 0:
        DiscordChannel.objects.filter(channel_id=ctx.channel.id).update(recent_image=ctx.images[0].url)
    if ctx.valid:
        await bot.invoke(ctx)

@bot.check
async def check_if_command_enabled(ctx: DiscordContext):
    name = ctx.command.name
    return not ctx.server_data or (ctx.channel_data.command_enabled(name) and ctx.server_data.command_enabled(name))

@bot.event
async def on_message_edit(_, msg: discord.Message):
    ctx = await bot.get_context(msg, cls=DiscordContext)
    if ctx.is_blacklisted:
        return
    image = await DiscordImage.from_message(msg, just_one=True)
    if image:
        DiscordChannel.objects.filter(channel_id=msg.channel.id).update(recent_image=image.url)

@bot.event
async def on_command(ctx: DiscordContext):
    logging.info(f'{ctx.guild}, #{ctx.channel}, {ctx.author}: {ctx.message.content}')

async def send_error_msg(ctx: DiscordContext, msg):
    if not ctx.can_respond:
        return
    await ctx.send(f"{ctx.author.mention} :warning: {msg}")

@bot.event
async def on_command_error(ctx: DiscordContext, exc):
    if isinstance(exc, CommandOnCooldown):
        await send_error_msg(ctx, f"You're memeing too fast! Please wait {int(exc.retry_after)} seconds.")
    elif isinstance(exc, DisabledCommand):
        await send_error_msg(ctx, f"`{ctx.command}` is disabled here")
    elif isinstance(exc, MissingPermissions):
        await send_error_msg(ctx, f"You need the following permissions to use this command: `{', '.join(exc.missing_perms)}`")
    elif isinstance(exc, BotMissingPermissions):
        await send_error_msg(ctx, f"The bot needs the following permissions for this command: `{', '.join(exc.missing_perms)}`")
    elif isinstance(exc, CheckFailure):
        return
    elif isinstance(exc, MissingRequiredArgument) and ctx.can_respond:
        await ctx.send_help(ctx.command)
    elif isinstance(exc, CommandInvokeError):
        log_exc(exc, ctx)
        await send_error_msg(ctx, "error :cry:")
    elif isinstance(exc, CommandError):
        if settings.DEBUG:
            log_exc(exc, ctx)
        await send_error_msg(ctx, str(exc) or "error :cry:")

@bot.command(name='invite')
async def cmd_invite(ctx: DiscordContext):
    """
    add the bot to your own server
    """
    await ctx.send(f'{ctx.author.mention} Visit {settings.WEBSITE_URL} to add this bot to your server.')

def run_bot():
    print('loading cogs: ', end='')
    for cog_name in os.listdir(os.path.join(settings.BASE_DIR, 'discordbot', 'cogs')):
        cog_name, _ = os.path.splitext(cog_name)
        if cog_name and not cog_name.startswith('__'):
            print(cog_name, end=' ')
            bot.load_extension('discordbot.cogs.' + cog_name)
    print()
    bot.run(settings.DISCORD_TOKEN)
