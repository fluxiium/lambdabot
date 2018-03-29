import discord
from django.core.exceptions import ObjectDoesNotExist

import discordbot.cogs._clevermurphybot.murphybot as murphy
import discordbot.cogs._clevermurphybot.cleverbot as cleverboi
from discord.ext.commands import Bot
from discordbot.models import DiscordServer
from discordbot.util import log, DiscordImage


class CleverMurphyBot:
    def __init__(self, bot: Bot):
        self.bot = bot

    async def on_message(self, msg: discord.Message):
        msg_text = msg.content.strip()

        try:
            DiscordServer.get(msg.guild)
        except ObjectDoesNotExist:
            return

        if not self.bot.user.mentioned_in(msg):
            return

        images = DiscordImage.get_from_message(msg)

        if msg_text.startswith(msg.guild.me.mention):
            msg_text = msg_text.replace(msg.guild.me.mention, "", 1).strip()
        elif msg_text.endswith(msg.guild.me.mention):
            msg_text = msg_text.rsplit(msg.guild.me.mention, 1)[0].strip()
        else:
            return

        log("{0}, {1} talking: {2}".format(msg.guild.name, msg.author.name, msg_text))

        answered = False

        for img in images:
            if img.is_embed:
                msg_text = msg_text.replace(img.get_url(), "", 1).strip()

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

        if msg_text and (not answered or not murphy.is_active()) and cleverboi.is_active():
            await cleverboi.talk(msg, msg_text)


def setup(bot):
    murphy.start(bot)
    bot.add_cog(CleverMurphyBot(bot))
