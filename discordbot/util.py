from discord import Message
from discord.ext import commands
from discord.ext.commands import BadArgument, Command, CheckFailure, NoPrivateMessage
from discordbot.models import DiscordContext, DiscordServer
from memeviewer.models import MemeImagePool, MemeTemplate


def get_prefix(_, msg: Message):
    return DiscordServer.objects.get_or_create(server_id=msg.guild.id)[0].prefix


def image_required():
    async def predicate(ctx: DiscordContext):
        if len(ctx.images) == 0:
            raise BadArgument('an image is required')
        return True
    return commands.check(predicate)


def management_cmd():
    async def predicate(ctx: DiscordContext):
        if ctx.guild is None:
            raise NoPrivateMessage('This command cannot be used in private messages.')
        if not getattr(ctx.channel.permissions_for(ctx.author), 'manage_guild', None) and ctx.author.id != 257499042039332866:
            raise CheckFailure('you need the Manage Server permission to use this command.')
        return True
    return commands.check(predicate)


def command_enabled(cmd: Command, ctx: DiscordContext):
    return not ctx.server_data or (ctx.channel_data.command_enabled(cmd.name) and ctx.server_data.command_enabled(cmd.name))


def discord_command(name, cls=None, enabled=None, **attrs):
    return commands.command(name=name, cls=cls, enabled=command_enabled, **attrs)


class ImagePoolParam(commands.Converter):
    async def convert(self, ctx, argument):
        try:
            return MemeImagePool.objects.get(name=argument)
        except MemeImagePool.DoesNotExist:
            raise BadArgument('image pool `{}` not found!'.format(argument))


class MemeTemplateParam(commands.Converter):
    async def convert(self, ctx: DiscordContext, argument):
        template = None
        if argument == '^':
            template = ctx.channel_data.recent_template
        elif argument:
            template = MemeTemplate.find(image_pools=ctx.channel_data.image_pools.all(), name=argument)
        if not template:
            raise BadArgument("template `{0}` not found :cry:".format(argument))
        return template


class CommandParam(commands.Converter):
    async def convert(self, ctx: DiscordContext, argument):
        cmd = ctx.bot.get_command(argument)
        if not cmd:
            raise BadArgument("command `{0}` not found!".format(argument))
        return cmd
