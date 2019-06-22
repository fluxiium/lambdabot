import aiohttp
import json
from discord.ext import commands
from discord.ext.commands import Bot, Context, CommandError, Cog
from util import headers


class GarfieldCog(Cog):
    def __init__(self, bot: Bot):
        self.__cog_name__ = "Garfield"
        self.bot = bot

    @commands.command(name='gfwiki')
    async def cmd_wiki(self, ctx: Context, *, query=None):
        """
        search the garfield wiki
        if no argument is given shows a random article
        """
        wiki_url = 'http://garfield.wikia.com'
        article_url = None

        async with ctx.typing(), aiohttp.ClientSession() as http_ses:
            if not query:
                async with http_ses.get(
                    f'{wiki_url}/api.php?action=query&list=random&rnnamespace=0&rnlimit=1&format=json',
                    headers=headers,
                ) as r:
                    article_data = json.loads(await r.text())
                    article_id = article_data['query']['random'][0]['id']

                async with http_ses.get(
                    f'{wiki_url}/api/v1/Articles/Details?ids={article_id}',
                    headers=headers,
                ) as r:
                    article_data = json.loads(await r.text())
                    article_url = f"{wiki_url}{article_data['items'][str(article_id)]['url']}"

            else:
                async with http_ses.get(
                    f'{wiki_url}/api/v1/Search/List?query={query}&limit=1',
                    headers=headers,
                ) as r:
                    article_data = json.loads(await r.text())
                    if article_data.get('exception') is None:
                        article_url = article_data['items'][0]['url']

        if article_url is None:
            raise CommandError("article not found :cry:")
        else:
            await ctx.send(f"{ctx.author.mention} {article_url}")


def setup(bot: Bot):
    bot.add_cog(GarfieldCog(bot))
