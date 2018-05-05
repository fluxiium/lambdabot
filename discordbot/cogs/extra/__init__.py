import random
import re
import requests
import shutil
from googletrans import Translator
import lamdabotweb.settings as config
import discord
from bs4 import BeautifulSoup
from discord.ext import commands
from discord.ext.commands import Bot, CommandError, Context, BucketType
from discordbot.cogs.extra.dance import dance
from discordbot.util import discord_command
from util import headers


class ExtraCmdCog:

    def __init__(self, bot: Bot):
        self.cog_name = "Cool stuff"
        self.bot = bot

    @discord_command(name='led')
    async def _cmd_led(self, ctx: Context, *, text):
        """
        generate an LED sign
        (uses wigflip.com)
        """
        async with ctx.typing():
            response = requests.post('http://wigflip.com/signbot/', data={
                'T': text,
                'S': 'L',
            }, headers=headers)

            soup = BeautifulSoup(response.content.decode('utf-8'), "html5lib")
            img = soup.select_one('#output img')

        if img is not None:
            await ctx.send("{} {}".format(ctx.author.mention, img['src']))
        else:
            raise CommandError()

    @discord_command(name='mario', usage='[name] <first_line> <message>')
    async def _cmd_mario(self, ctx, first_line, message, arg3=''):
        """
        generate a mario GIF
        (uses wigflip.com)
        """
        if arg3:
            name = first_line
            title = message
            msgtext = arg3
        else:
            name = None
            title = first_line
            msgtext = message

        async with ctx.typing():
            response = requests.post('http://wigflip.com/thankyoumario/', data={
                'name': name,
                'title': title,
                'lines': msgtext,
                'double': 'y',
            }, headers=headers)

            soup = BeautifulSoup(response.content.decode('utf-8'), "html5lib")
            img = soup.select_one('#output img')

        if img is not None:
            await ctx.send("{} {}".format(ctx.author.mention, img['src']))
        else:
            raise CommandError()

    @discord_command(name='noviews')
    async def _cmd_noviews(self, ctx):
        """
        show a random youtube video with no views
        (uses petittube.com)
        """
        attempt = 0
        videourl = None

        async with ctx.typing():
            while videourl is None and attempt < 5:
                # noinspection PyBroadException
                try:
                    response = requests.get('http://www.petittube.com', headers=headers)
                    soup = BeautifulSoup(response.content.decode('utf-8'), "html5lib")
                    videourl = re.search('/(\w+)\?', soup.select_one('iframe')['src']).groups()[0]
                except Exception:
                    attempt += 1

        if videourl is not None:
            await ctx.send("{} https://youtu.be/{}".format(ctx.author.mention, videourl))
        else:
            raise CommandError()

    @discord_command(name='dance', guild_only=True)
    @commands.cooldown(config.DANCE_LIMIT, config.DANCE_COOLDOWN, BucketType.user)
    @commands.bot_has_permissions(attach_files=True)
    async def _cmd_dance(self, ctx, *, text):
        """
        generate text using dancing letters
        (uses gifs from artie.com)
        """
        async with ctx.typing():
            tmpdir = dance(text)
        await ctx.send(file=discord.File(tmpdir + '/dance.gif'))
        shutil.rmtree(tmpdir)

    @discord_command(name='googletrans', aliases=['gt'], usage='[num] (text)')
    async def _cmd_googletrans(self, ctx, num, *, text=''):
        """
        google translate text num times into random languages and then back to english
        (num = 4 by default)
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
            howmany = max(1, min(10, int(num)))
        except ValueError:
            howmany = 4
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
        await ctx.send('{} **{}** ```{} ```'.format(ctx.author.mention, ' ➔ '.join([start] + langs), text))


def setup(bot: Bot):
    bot.add_cog(ExtraCmdCog(bot))
