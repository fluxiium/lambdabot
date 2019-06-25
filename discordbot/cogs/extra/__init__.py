import aiohttp
import random
import re
import shutil
import discord
from googletrans import Translator
from bs4 import BeautifulSoup
from discord.ext import commands
from discord.ext.commands import Bot, CommandError, Context, BucketType, Cog
from discordbot.cogs.extra.dance import dance
from util import headers
from discordbot import settings


class ExtraCmdCog(Cog):

    def __init__(self, bot: Bot):
        self.__cog_name__ = "Miscellaneous"
        self.bot = bot

    @commands.command('led')
    async def cmd_led(self, ctx: Context, *, text):
        """
        generate an LED sign
        (uses wigflip.com)
        """
        async with ctx.typing(), aiohttp.ClientSession() as http_ses:
            async with http_ses.post('http://wigflip.com/signbot/', data={'T': text, 'S': 'L'}, headers=headers) as r:
                soup = BeautifulSoup(await r.text(), "html5lib")
            img = soup.select_one('#output img')

        if img is not None:
            await ctx.send(f"{ctx.author.mention} {img['src']}")
        else:
            raise CommandError()

    @commands.command(name='mario')
    async def cmd_mario(self, ctx, title, message, name=''):
        """
        generate a mario GIF
        (uses wigflip.com)
        """
        async with ctx.typing(), aiohttp.ClientSession() as http_ses:
            async with http_ses.post('http://wigflip.com/thankyoumario/', data={'name': name, 'title': title, 'lines': message, 'double': 'y'}, headers=headers) as r:
                soup = BeautifulSoup(await r.text(), "html5lib")
            img = soup.select_one('#output img')

        if img is not None:
            await ctx.send(f"{ctx.author.mention} {img['src']}")
        else:
            raise CommandError()

    @commands.command(name='noviews')
    async def cmd_noviews(self, ctx):
        """
        show a random youtube video with no views
        (uses petittube.com)
        """
        attempt = 0
        videourl = None

        async with ctx.typing(), aiohttp.ClientSession() as http_ses:
            while videourl is None and attempt < 5:
                # noinspection PyBroadException
                try:
                    async with http_ses.get('http://www.petittube.com', headers=headers) as r:
                        soup = BeautifulSoup(await r.text(), "html5lib")
                    videourl = re.search('/(\w+)\?', soup.select_one('iframe')['src']).groups()[0]
                except Exception:
                    attempt += 1

        if videourl is not None:
            await ctx.send(f"{ctx.author.mention} https://youtu.be/{videourl}")
        else:
            raise CommandError()

    @commands.command(name='dance', guild_only=True)
    @commands.cooldown(settings.DANCE_LIMIT, settings.DANCE_COOLDOWN, BucketType.user)
    @commands.bot_has_permissions(attach_files=True)
    async def cmd_dance(self, ctx, *, text):
        """
        generate text using dancing letters
        (uses gifs from artie.com)
        """
        async with ctx.typing():
            tmpdir = await dance(text)
        await ctx.send(file=discord.File(tmpdir + '/dance.gif'))
        shutil.rmtree(tmpdir)

    @commands.command(name='googletrans', aliases=['gt'])
    async def cmd_googletrans(self, ctx, num, *, text=''):
        """
        run google translate on some text multiple times
        (4 times by default)
        """
        langs = ["af", "sq", "ar", "be", "bg", "ca", "zh-CN", "zh-TW", "hr",
                 "cs", "da", "nl", "et", "tl", "fi", "fr", "gl", "de", "en",
                 "el", "iw", "hi", "hu", "is", "id", "ga", "it", "ja", "ko",
                 "lv", "lt", "mk", "ms", "mt", "no", "fa", "pl", "pt", "ro",
                 "ru", "sr", "sk", "sl", "es", "sw", "sv", "th", "tr", "uk",
                 "vi", "cy", "yi"]
        translator = Translator()
        if not text:
            text = num
            num = ''
        try:
            howmany = max(1, min(len(langs), int(num)))
        except ValueError:
            howmany = 4
            text = f'{num} {text}'
        text = text.replace('`', '')
        try:
            start = translator.detect(text).lang
        except ValueError:
            start = 'en'
        try:
            langs.remove(start)
        except ValueError:
            pass
        langs = random.sample(langs, howmany - 1) + ['en']
        async with ctx.typing():
            for lang in langs:
                text = translator.translate(text, dest=lang).text
        await ctx.send(f'{ctx.author.mention} **{" ➔ ".join([start] + langs)}** ```{text} ```')


def setup(bot: Bot):
    bot.add_cog(ExtraCmdCog(bot))
