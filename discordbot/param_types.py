from discord.ext import commands
from discord.ext.commands import BadArgument
from discordbot.models import DiscordContext
from memeviewer.models import MemeImagePool, MemeTemplate
from util import is_url


class ImagePoolParam(commands.Converter):
    def __init__(self, many=False, avail_only=False, moderated_only=False, ignore_urls=False):
        self.many = many
        self.avail_only = avail_only
        self.moderated_only = moderated_only
        self.ignore_urls = ignore_urls

    async def convert(self, ctx: DiscordContext, argument):
        if is_url(argument) and self.ignore_urls:
            return self.many and [] or None
        if self.many:
            pool_names = argument.split()
        else:
            pool_names = [argument]
        if self.avail_only:
            obj = ctx.user_data.available_pools(ctx.channel_data)
        elif self.moderated_only:
            obj = ctx.user_data.moderated_pools
        else:
            obj = MemeImagePool.objects
        pools = obj.filter(name__in=pool_names)
        if len(pools) == 0:
            raise BadArgument("no matching pools found!")
        return self.many and pools or pools[0]


class MemeTemplateParam(commands.Converter):
    async def convert(self, ctx: DiscordContext, argument):
        template = None
        argument = argument.replace('`', '')
        if argument == '^':
            template = ctx.channel_data.recent_template
        elif argument:
            template = MemeTemplate.find(image_pools=ctx.channel_data.image_pools.all(), name=argument)
        if not template:
            raise BadArgument("template `{0}` not found :cry:".format(argument))
        return template


class CommandParam(commands.Converter):
    def __init__(self, many=False):
        self.many = many

    async def convert(self, ctx: DiscordContext, argument):
        if self.many:
            cmd_names = argument.split()
        else:
            cmd_names = [argument]
        cmds = list(map(lambda cmd_name: ctx.bot.get_command(cmd_name), cmd_names))
        if len(cmds) == 0:
            raise BadArgument("no matching commands found!")
        return self.many and cmds or cmds[0]
