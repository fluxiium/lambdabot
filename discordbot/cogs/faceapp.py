import io
import random
import string
import requests
import discord
import util
from discord.ext.commands import Bot, CommandError, BadArgument
from discordbot.util import discord_command
from discordbot.models import DiscordContext


class FaceAppCog:

    def __init__(self, bot: Bot):
        self.cog_name = "FaceApp"
        self.bot = bot

    # source: https://github.com/xeyalxx/faceapp_p3/blob/master/faceapp.py
    @classmethod
    async def __do_faceapp(cls, ctx: DiscordContext, url, filter_name):
        device_id = ''.join(random.choice(string.ascii_letters) for _ in range(8))
        headers = {'User-agent': "FaceApp/1.0.229 (Linux; Android 4.4)", 'X-FaceApp-DeviceID': device_id}
        async with ctx.typing():
            res = requests.post('http://node-01.faceapp.io/api/v2.7/photos', headers=headers,
                                files={'file': requests.get(url, headers=util.headers).content})
        code = res.json().get('code')
        if not code:
            raise BadArgument('no face detected :cry:')
        crop = filter_name in ['smile', 'smile_2', 'old', 'young'] and '0' or '1'
        async with ctx.typing():
            res2 = requests.get(
                'http://node-01.faceapp.io/api/v2.7/photos/%s/filters/%s?cropped=%s' % (code, filter_name, crop),
                headers=headers)
        if 'x-faceapp-errorcode' in res2.headers:
            raise CommandError()
        await ctx.send(ctx.author.mention, file=discord.File(io.BytesIO(res2.content), 'faceapp.jpg'))

    @discord_command(name='smile', image_required=True)
    async def _cmd_smile(self, ctx: DiscordContext):
        await self.__do_faceapp(ctx, ctx.images[0].url, ctx.command.name)

    @discord_command(name='smile2', image_required=True)
    async def _cmd_smile_2(self, ctx: DiscordContext):
        await self.__do_faceapp(ctx, ctx.images[0].url, 'smile_2')

    @discord_command(name='hot', image_required=True)
    async def _cmd_hot(self, ctx: DiscordContext):
        await self.__do_faceapp(ctx, ctx.images[0].url, ctx.command.name)

    @discord_command(name='old', image_required=True)
    async def _cmd_old(self, ctx: DiscordContext):
        await self.__do_faceapp(ctx, ctx.images[0].url, ctx.command.name)

    @discord_command(name='young', image_required=True)
    async def _cmd_young(self, ctx: DiscordContext):
        await self.__do_faceapp(ctx, ctx.images[0].url, ctx.command.name)

    @discord_command(name='female', image_required=True)
    async def _cmd_female(self, ctx: DiscordContext):
        await self.__do_faceapp(ctx, ctx.images[0].url, ctx.command.name)

    @discord_command(name='female2', image_required=True)
    async def _cmd_female_2(self, ctx: DiscordContext):
        await self.__do_faceapp(ctx, ctx.images[0].url, 'female_2')

    @discord_command(name='makeup', image_required=True)
    async def _cmd_makeup(self, ctx: DiscordContext):
        await self.__do_faceapp(ctx, ctx.images[0].url, ctx.command.name)

    @discord_command(name='impression', image_required=True)
    async def _cmd_impression(self, ctx: DiscordContext):
        await self.__do_faceapp(ctx, ctx.images[0].url, ctx.command.name)

    @discord_command(name='bangs', image_required=True)
    async def _cmd_bangs(self, ctx: DiscordContext):
        await self.__do_faceapp(ctx, ctx.images[0].url, ctx.command.name)

    @discord_command(name='glasses', image_required=True)
    async def _cmd_glasses(self, ctx: DiscordContext):
        await self.__do_faceapp(ctx, ctx.images[0].url, ctx.command.name)

    @discord_command(name='wave', image_required=True)
    async def _cmd_wave(self, ctx: DiscordContext):
        await self.__do_faceapp(ctx, ctx.images[0].url, ctx.command.name)

    @discord_command(name='male', image_required=True)
    async def _cmd_male(self, ctx: DiscordContext):
        await self.__do_faceapp(ctx, ctx.images[0].url, ctx.command.name)

    @discord_command(name='hipster', image_required=True)
    async def _cmd_hipster(self, ctx: DiscordContext):
        await self.__do_faceapp(ctx, ctx.images[0].url, ctx.command.name)

    @discord_command(name='pan', image_required=True)
    async def _cmd_pan(self, ctx: DiscordContext):
        await self.__do_faceapp(ctx, ctx.images[0].url, ctx.command.name)

    @discord_command(name='lion', image_required=True)
    async def _cmd_lion(self, ctx: DiscordContext):
        await self.__do_faceapp(ctx, ctx.images[0].url, ctx.command.name)

    @discord_command(name='hitman', image_required=True)
    async def _cmd_hitman(self, ctx: DiscordContext):
        await self.__do_faceapp(ctx, ctx.images[0].url, ctx.command.name)

    @discord_command(name='heisenberg', image_required=True)
    async def _cmd_heisenberg(self, ctx: DiscordContext):
        await self.__do_faceapp(ctx, ctx.images[0].url, ctx.command.name)


def setup(bot: Bot):
    bot.add_cog(FaceAppCog(bot))
