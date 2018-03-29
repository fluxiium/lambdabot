from discord.ext.commands import Bot, Context, HelpFormatter, CommandNotFound
from django.core.exceptions import ObjectDoesNotExist
from discordbot.models import DiscordServer
from discordbot.util import log_exc


class CustomCmds:
    def __init__(self, bot: Bot):
        self.bot = bot

    # noinspection PyMethodMayBeStatic
    async def on_command_error(self, ctx: Context, exc):
        if not isinstance(exc, CommandNotFound):
            log_exc(exc)

        try:
            server_data = DiscordServer.get(ctx.guild)
        except ObjectDoesNotExist:
            return

        msg_text = ctx.message.content.strip()

        if not msg_text.startswith(ctx.prefix) or ctx.message.author.bot:
            return

        cmd = server_data.get_cmd(ctx.invoked_with)
        if cmd is None:
            return
        await ctx.send(cmd.message)


def setup(bot: Bot):
    bot.add_cog(CustomCmds(bot))
