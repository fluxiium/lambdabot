from discord.ext import commands
from discord.ext.commands import MissingPermissions, NoPrivateMessage, BadArgument
from discordbot.models import DiscordContext

def yackson_only():
    def predicate(ctx: DiscordContext):
        return ctx.author.id == 257499042039332866
    return commands.check(predicate)


def management_only():
    def predicate(ctx: DiscordContext):
        if ctx.guild is None or not ctx.is_manager:
            raise MissingPermissions(['manage_server'])
        return True
    return commands.check(predicate)


def guild_only():
    def predicate(ctx: DiscordContext):
        if ctx.guild is None:
            raise NoPrivateMessage('This command cannot be used in private messages.')
        return True
    return commands.check(predicate)


def requires_image():
    def predicate(ctx: DiscordContext):
        if len(ctx.images) == 0:
            raise BadArgument('an image is required')
        return True
    return commands.check(predicate)
