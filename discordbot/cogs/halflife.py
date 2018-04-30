import discord
import json
import random
import requests
import textwrap
import config

from bs4 import BeautifulSoup
from discord import Embed, Message
from discord.ext.commands import Context, CommandError, Bot
from django.utils import timezone
from discordbot.util import discord_command
from util import headers
from discordbot.models import DiscordImage

_IMG_ARCHIVE_CHANNEL = 395615705048809492
if config.DEBUG:
    _SERVER_ID = 395615515101495299
    _LOG_CHANNEL = 395616760302141450
else:
    _SERVER_ID = 154305477323390976
    _LOG_CHANNEL = 154637540341710848


class HalfLifeCog:
    def __init__(self, bot: Bot):
        self.cog_name = "Half-Life"
        self.bot = bot

    @property
    def __log_channel(self):
        return self.bot.get_channel(_LOG_CHANNEL)

    @property
    def __img_archive_channel(self):
        return self.bot.get_channel(_IMG_ARCHIVE_CHANNEL)

    @discord_command(name='overwiki', help='search the half-life overwiki')
    async def _cmd_wiki(self, ctx: Context, *, query=None):
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
                article_data = json.loads(response.content.decode('utf-8'))
                article = next(iter(article_data['query']['pages'].values()))

            else:
                response = requests.get(
                    '{0}/api.php?action=query&generator=search&gsrsearch={1}&gsrlimit=1&prop=info&inprop=url&format=json'.format(wiki_url, query),
                    headers=headers,
                )
                article_data = json.loads(response.content.decode('utf-8'))
                if article_data.get('query') is not None:
                    article = next(iter(article_data['query']['pages'].values()))

        proceed = False
        soup = None

        async with ctx.typing():
            while not proceed:
                if article is None:
                    raise CommandError("article not found :cry:")

                response = requests.get(article['fullurl'], headers=headers)
                soup = BeautifulSoup(response.content.decode('utf-8'), "html5lib")

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
                        article_data = json.loads(response.content.decode('utf-8'))
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
        if not message.guild or message.guild.id != _SERVER_ID:
            return

        images = DiscordImage.from_message(message, attachments_only=True)

        if len(images) == 0:
            return

        for att in images:
            att_path = att.save()
            msg_archived = await self.__img_archive_channel.send(file=discord.File(att_path))
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

            await self.__log_channel.send(embed=embed)


def setup(bot: Bot):
    bot.add_cog(HalfLifeCog(bot))
