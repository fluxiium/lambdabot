from discord.ext import commands
from discord.ext.commands import BadArgument
from discordbot.models import DiscordContext


def image_required():
    async def predicate(ctx: DiscordContext):
        if len(ctx.images) == 0:
            raise BadArgument('an image is required')
        return True
    return commands.check(predicate)
