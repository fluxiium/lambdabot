import discord
import json
import random
import requests
import textwrap
from bs4 import BeautifulSoup
from discord import Embed, Message
from discord.ext import commands
from discord.ext.commands import CommandError, Bot, Cog
from django.utils import timezone
from util import headers
from discordbot.models import DiscordImage, DiscordContext
from discordbot import settings

IMG_ARCHIVE_CHANNEL = 441204229902827535
NO_LOG_CHANNELS = [460903023925788673, 381240135905312778, 436225212774613022, 407251146785292318, 406968735329419264,
                   156833429143420928]
if settings.DEBUG:
    SERVER_ID = 395615515101495299
    LOG_CHANNEL = 395616760302141450
    MODERATORS_ROLE = 460730783259426818
    CITIZEN_ROLE = 460730783259426818
    GAY_BABY_ROLE = 493054368313245696
else:
    SERVER_ID = 154305477323390976
    LOG_CHANNEL = 154637540341710848
    MODERATORS_ROLE = 406968787343245312
    CITIZEN_ROLE = 460736996185341962
    GAY_BABY_ROLE = 486241262819737610


def moderators_only():
    async def predicate(ctx):
        return ctx.is_manager or MODERATORS_ROLE in [r.id for r in ctx.author.roles]
    return commands.check(predicate)


def hldiscord_only():
    def predicate(ctx: DiscordContext):
        return ctx.guild and ctx.guild.id == SERVER_ID
    return commands.check(predicate)


class HalfLifeCog(Cog):
    def __init__(self, bot: Bot):
        self.__cog_name__ = "Half-Life"
        self.bot = bot

    @property
    def get_log_channel(self):
        return self.bot.get_channel(LOG_CHANNEL)

    @property
    def get_img_archive_channel(self):
        return self.bot.get_channel(IMG_ARCHIVE_CHANNEL)

    @moderators_only()
    @hldiscord_only()
    @commands.command(name='verify', hidden=True)
    async def cmd_verify(self, ctx: DiscordContext, *, user: discord.Member):
        citizen_role = discord.utils.get(ctx.guild.roles, id=CITIZEN_ROLE)
        if citizen_role not in user.roles:
            await user.add_roles(citizen_role)
            await ctx.send(f'{ctx.author.mention} user verified!')
        else:
            raise CommandError('This user is verified already!')

    @moderators_only()
    @hldiscord_only()
    @commands.command(name='jail', hidden=True)
    async def cmd_jail(self, ctx: DiscordContext, *, user: discord.Member):
        await user.add_roles(discord.utils.get(ctx.guild.roles, id=GAY_BABY_ROLE))

    @moderators_only()
    @hldiscord_only()
    @commands.command(name='unjail', hidden=True)
    async def cmd_unjail(self, ctx: DiscordContext, *, user: discord.Member):
        await user.remove_roles(discord.utils.get(ctx.guild.roles, id=GAY_BABY_ROLE))

    @commands.command(name='overwiki')
    async def cmd_wiki(self, ctx: DiscordContext, *, query=None):
        """
        search the half-life overwiki
        if no argument is given shows a random article
        """
        wiki_url = 'http://combineoverwiki.net'
        article = None
        was_random = False

        async with ctx.typing():
            if not query:
                was_random = True
                response = requests.get(
                    '{0}/api.php?action=query&generator=random&grnnamespace=0&grnlimit=1&prop=info&inprop=url&format=json'.format(wiki_url),
                    headers=headers,
                )
                article_data = json.loads(response.text)
                article = next(iter(article_data['query']['pages'].values()))

            else:
                response = requests.get(
                    '{0}/api.php?action=query&generator=search&gsrsearch={1}&gsrlimit=1&prop=info&inprop=url&format=json'.format(wiki_url, query),
                    headers=headers,
                )
                article_data = json.loads(response.text)
                if article_data.get('query') is not None:
                    article = next(iter(article_data['query']['pages'].values()))

        proceed = False
        soup = None

        async with ctx.typing():
            while not proceed:
                if article is None:
                    raise CommandError("article not found :cry:")

                response = requests.get(article['fullurl'], headers=headers)
                soup = BeautifulSoup(response.text, "html5lib")

                heading = soup.select_one('#firstHeading')
                if not was_random or heading is None or not heading.getText().lower().endswith('(disambiguation)'):
                    proceed = True
                else:
                    page_links = soup.select('#mw-content-text > ul:nth-of-type(1) > li')
                    random_page = random.choice([li.select_one('a:nth-of-type(1)').getText() for li in page_links])
                    if random_page is None:
                        article = None
                    else:
                        response = requests.get(
                            '{0}/api.php?action=query&generator=search&gsrsearch={1}&gsrlimit=1&prop=info&inprop=url&format=json'.format(
                                wiki_url, random_page),
                            headers=headers,
                        )
                        article_data = json.loads(response.text)
                        if article_data.get('query') is not None:
                            article = next(iter(article_data['query']['pages'].values()))

        pic_tag = soup.select_one('td.infoboximage > a > img')
        if pic_tag is None:
            pic_tag = soup.select_one('img.thumbimage')

        desc_tag = soup.select_one('div#mw-content-text > p:nth-of-type(2)')
        desc = textwrap.shorten(desc_tag.getText(), width=250) if desc_tag is not None else None

        embed = Embed(
            title=article['title'],
            url=article['fullurl'],
            color=0xF7923A,
            description=desc,
        )
        embed.set_footer(
            text="Combine Overwiki",
            icon_url="http://combineoverwiki.net/images/1/12/HLPverse.png".format(wiki_url)
        )

        if pic_tag is not None:
            embed.set_thumbnail(url="{0}{1}".format(wiki_url, pic_tag['src']))

        await ctx.send("{} {}".format(ctx.author.mention, article['fullurl']), embed=embed)

    async def on_message_delete(self, message: Message):
        if not message.guild or message.guild.id != SERVER_ID or message.channel.id in NO_LOG_CHANNELS:
            return

        images = DiscordImage.from_message(message, attachments_only=True)

        if len(images) == 0:
            return

        for att in images:
            att_path = att.save()
            msg_archived = await self.get_img_archive_channel.send(file=discord.File(att_path))
            att.cleanup()
            att = msg_archived.attachments[0]

            embed = Embed(
                description="**Attachment sent by {0} deleted in <#{1}>**\n{2}".format(
                    message.author.mention, message.channel.id, att.proxy_url
                ),
                color=0xFF470F,
                timestamp=timezone.now()
            )
            embed.set_author(
                name=str(message.author),
                icon_url=message.author.avatar_url
            )
            embed.set_footer(
                text="ID: {0}".format(message.author.id),
            )

            await self.get_log_channel.send(embed=embed)


def setup(bot: Bot):
    bot.add_cog(HalfLifeCog(bot))
