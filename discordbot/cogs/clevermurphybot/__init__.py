import discord
from discord.ext.commands import Bot
from discordbot.models import DiscordImage, DiscordContext
import logging
from discordbot.cogs.clevermurphybot import murphybot as murphy
from discordbot.cogs.clevermurphybot import cleverbot as cleverboi


class CleverMurphyBot:
    def __init__(self, bot: Bot):
        self.bot = bot

    async def on_message(self, msg: discord.Message):
        ctx = await self.bot.get_context(msg, cls=DiscordContext)
        if ctx.is_blacklisted:
            return

        msg_text = msg.content.strip()
        dm = False

        if msg.guild is None:
            dm = True

        if (not self.bot.user.mentioned_in(msg) and not dm) or (msg.author == self.bot.user) or msg_text.startswith(await self.bot.get_prefix(msg)):
            return

        images = DiscordImage.from_message(msg)
        mention = dm and self.bot.user.mention or msg.guild.me.mention

        if msg_text.startswith(mention):
            msg_text = msg_text.replace(mention, "", 1).strip()
        elif msg_text.endswith(mention):
            msg_text = msg_text.rsplit(mention, 1)[0].strip()
        elif not dm:
            return

        logging.info(f"{msg.guild or 'DM'}, {msg.author} talking: {msg_text}")

        answered = False

        for img in images:
            msg_text = msg_text.replace(img.url, "", 1).strip()

        if murphy.is_active() and not msg.author.bot:
            answered = True
            img = images[0] if len(images) > 0 else None
            if msg_text.lower().startswith("what if i ") or (msg_text == "" and img is not None):
                face_pic = img.save() if img is not None else ''
                if msg_text == "" and img is not None:
                    murphy.ask(msg, face_pic=face_pic)
                elif msg_text != "":
                    murphy.ask(msg, question=msg_text, face_pic=face_pic)

            elif msg_text.lower().startswith("what if "):
                murphy.ask(msg, question=msg_text)

            else:
                answered = False

        if msg_text and (not answered or not murphy.is_active()):
            await cleverboi.talk(msg, msg_text)


def setup(bot):
    murphy.start(bot)
    bot.add_cog(CleverMurphyBot(bot))
