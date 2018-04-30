from discord import Message
from discord.ext import commands
from discord.ext.commands import BadArgument, Command, CheckFailure, NoPrivateMessage
from discordbot.models import DiscordContext, DiscordServer
from memeviewer.models import MemeImagePool, MemeTemplate


def get_prefix(_, msg: Message):
    return DiscordServer.objects.get_or_create(server_id=msg.guild.id)[0].prefix


def command_enabled(cmd: Command, ctx: DiscordContext):
    return not ctx.server_data or (ctx.channel_data.command_enabled(cmd.name) and ctx.server_data.command_enabled(cmd.name))


def discord_command(parent=None, group=False, management=False, guild_only=False, image_required=False,
                    invoke_without_command=True, enabled=command_enabled, pass_context=True, **attrs):

    async def predicate(ctx: DiscordContext):
        if (guild_only or management) and ctx.guild is None:
            raise NoPrivateMessage('This command cannot be used in private messages.')
        if management and not getattr(ctx.channel.permissions_for(ctx.author), 'manage_guild', None) and ctx.author.id != 257499042039332866:
            raise CheckFailure('you need the Manage Server permission to use this command.')
        if image_required and len(ctx.images) == 0:
            raise BadArgument('an image is required')
        return True

    def decorator(f):
        cmdattrs = attrs
        cmdattrs['enabled'] = enabled
        if group:
            cmdattrs['pass_context'] = pass_context
            cmdattrs['invoke_without_command'] = invoke_without_command
        cmddecorator = group and commands.group or commands.command
        cmd = commands.check(predicate)(cmddecorator(**cmdattrs)(f))
        if parent:
            parent.add_command(cmd)
        return cmd

    return decorator


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
    def __init__(self, many=False):
        self.__many = many

    async def convert(self, ctx: DiscordContext, argument):
        if self.__many:
            cmd_names = argument.split()
        else:
            cmd_names = [argument]
        cmds = list(map(lambda cmd_name: ctx.bot.get_command(cmd_name), cmd_names))
        if len(cmds) == 0:
            raise BadArgument("no commands found!")
        return self.__many and cmds or cmds[0]
