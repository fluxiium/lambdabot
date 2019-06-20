import discord
from discord.ext import commands
from discord.ext.commands import Bot, Cog
from discordbot.models import DiscordContext
import logging
from discordbot.cogs.clevermurphybot import cleverbot as cleverboi


class CleverMurphyBot(Cog):
    def __init__(self, bot: Bot):
        self.__cog__name__ = 'Cleverbot / Murphybot'
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        ctx = await self.bot.get_context(msg, cls=DiscordContext)
        if ctx.is_blacklisted:
            return

        msg_text = msg.content.strip()
        dm = msg.guild is None

        if (not self.bot.user.mentioned_in(msg) and not dm) or (msg.author == self.bot.user) or msg_text.startswith(await self.bot.get_prefix(msg)):
            return

        mention = dm and self.bot.user.mention or msg.guild.me.mention

        if msg_text.startswith(mention):
            msg_text = msg_text.replace(mention, "", 1).strip()
        elif msg_text.endswith(mention):
            msg_text = msg_text.rsplit(mention, 1)[0].strip()
        elif not dm:
            return

        logging.info(f"{msg.guild or 'DM'}, {msg.author} talking: {msg_text}")

        await cleverboi.talk(msg, msg_text)


def setup(bot):
    bot.add_cog(CleverMurphyBot(bot))
