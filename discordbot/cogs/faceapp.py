import io
import random
import string
import requests
import discord
import util
from discord.ext import commands
from discord.ext.commands import Bot, CommandError, BadArgument
from discordbot.checks import image_required
from discordbot.models import DiscordContext

_FILTERS = [
    "smile",
    "smile_2",
    "hot",
    "old",
    "young",
    "female",
    "female_2",
    "makeup",
    "impression",
    "bangs",
    "glasses",
    "wave",
    "male",
    "hipster",
    "pan",
    "lion",
    "hitman",
    "heisenberg"
]


class FaceAppCog:

    def __init__(self, bot: Bot):
        self.cog_name = "FaceApp"
        self.bot = bot

    # source: https://github.com/xeyalxx/faceapp_p3/blob/master/faceapp.py
    @classmethod
    def __do_faceapp(cls, url, filter_name):
        device_id = ''.join(random.choice(string.ascii_letters) for _ in range(8))
        headers = {'User-agent': "FaceApp/1.0.229 (Linux; Android 4.4)", 'X-FaceApp-DeviceID': device_id}
        res = requests.post('http://node-01.faceapp.io/api/v2.7/photos', headers=headers,
                            files={'file': requests.get(url, headers=util.headers).content})
        code = res.json().get('code')
        if not code:
            raise BadArgument('no face detected :cry:')
        crop = filter_name in ['smile', 'smile_2', 'old', 'young'] and '0' or '1'
        res2 = requests.get(
            'http://node-01.faceapp.io/api/v2.7/photos/%s/filters/%s?cropped=%s' % (code, filter_name, crop),
            headers=headers)
        if 'x-faceapp-errorcode' in res2.headers:
            raise CommandError()
        return res2.content

    @commands.command(name='faceapp', aliases=['fa'], usage='<%s> <image>' % '|'.join(_FILTERS))
    @image_required()
    async def _cmd_fa(self, ctx: DiscordContext, flt):
        if flt not in _FILTERS:
            raise BadArgument('invalid filter')
        async with ctx.typing():
            result = self.__do_faceapp(ctx.images[0].url, flt)
        await ctx.send(ctx.author.mention, file=discord.File(io.BytesIO(result), 'faceapp.jpg'))


def setup(bot: Bot):
    bot.add_cog(FaceAppCog(bot))
