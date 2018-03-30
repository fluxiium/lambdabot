from discord import Message
from discord.ext.commands import Bot
from django.core.exceptions import ObjectDoesNotExist
from discordbot.models import DiscordServer


class CustomCmds:
    def __init__(self, bot: Bot):
        self.bot = bot

    # noinspection PyMethodMayBeStatic
    async def on_message(self, msg: Message):
        try:
            server_data = DiscordServer.get(msg.guild)
        except ObjectDoesNotExist:
            return

        msg_text = msg.content.strip()

        if not msg_text.startswith(self.bot.command_prefix) or msg.author.bot:
            return

        cmd = server_data.get_cmd(msg_text[len(self.bot.command_prefix):])
        if cmd is None:
            return
        await msg.channel.send(cmd.message)


def setup(bot: Bot):
    bot.add_cog(CustomCmds(bot))
