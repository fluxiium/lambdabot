from discord import Message
from discord.ext import commands
from discord.ext.commands import BadArgument, Command, CheckFailure, NoPrivateMessage, MissingPermissions
from discordbot.models import DiscordContext, DiscordServer
from memeviewer.models import MemeImagePool, MemeTemplate


def get_prefix(_, msg: Message):
    if msg.guild is None:
        return '!'
    else:
        return DiscordServer.objects.get_or_create(server_id=msg.guild.id)[0].prefix


def command_enabled(cmd, ctx: DiscordContext):
    if ctx.channel_data is None:
        return False
    name = isinstance(cmd, Command) and cmd.name or cmd
    return not ctx.server_data or (ctx.channel_data.command_enabled(name) and ctx.server_data.command_enabled(name))


def discord_command(name, parent=None, group=False, management=False, guild_only=False, image_required=False,
                    invoke_without_command=True, enabled=command_enabled, pass_context=True, hidden=None, **attrs):

    def is_manager(ctx: DiscordContext):
        return getattr(ctx.channel.permissions_for(ctx.author), 'manage_guild', None) or ctx.author.id == 257499042039332866

    async def predicate(ctx: DiscordContext):
        if (guild_only or management) and ctx.guild is None:
            raise NoPrivateMessage('This command cannot be used in private messages.')
        if management and not is_manager(ctx):
            raise MissingPermissions(['manage_server'])
        if image_required and len(ctx.images) == 0:
            raise BadArgument('an image is required')
        return True

    if hidden is None:
        if management:
            def hidden(_, ctx):
                return not command_enabled(name, ctx) or ctx.guild is None or not is_manager(ctx)
        elif guild_only:
            def hidden(_, ctx):
                return not command_enabled(name, ctx) or ctx.guild is None
        else:
            def hidden(_, ctx):
                return not command_enabled(name, ctx)

    def decorator(f):
        cmdattrs = attrs
        cmdattrs['name'] = name
        cmdattrs['enabled'] = enabled
        cmdattrs['hidden'] = hidden
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
    def __init__(self, many=False):
        self.__many = many

    async def convert(self, ctx, argument):
        if self.__many:
            pool_names = argument.split()
        else:
            pool_names = [argument]
        pools = MemeImagePool.objects.filter(name__in=pool_names)
        if len(pools) == 0:
            raise BadArgument("no matching pools found!")
        return self.__many and pools or pools[0]


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
            raise BadArgument("no matching commands found!")
        return self.__many and cmds or cmds[0]
