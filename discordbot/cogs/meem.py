import discord
import config
from discord.ext import commands
from discord.ext.commands import Bot, BadArgument, BucketType
from discordbot.checks import image_required
from discordbot.models import log, DiscordContext
from lamdabotweb.settings import MAX_SRCIMG_SIZE, DISCORD_SEND_ATTACHMENTS
from memeviewer.models import MemeTemplate


class MemeGeneratorCog:

    def __init__(self, bot: Bot):
        self.cog_name = "Meme generator"
        self.bot = bot

    @commands.command(
        name='meme',
        help='generate a random meme\n'
             'you can specify a template to use for the meme\n'
             'use `^` to use the template of the last meme generated',
        aliases=['meem', 'mem', 'meemay', 'memuch', 'miejm'],
    )
    @commands.cooldown(config.DISCORD_MEME_LIMIT, config.DISCORD_MEME_COOLDOWN, BucketType.user)
    async def _cmd_meem(self, ctx: DiscordContext, *, template_name=None):
        template = None

        async with ctx.typing():
            if template_name == '^':
                template = ctx.channel_data.recent_template
            elif template_name:
                template = MemeTemplate.find(template_name)

        if template_name and not template:
            raise BadArgument("template `{0}` not found :cry:".format(template_name))

        async with ctx.typing():
            meme = ctx.user_data.generate_meme(template=template, channel=ctx.channel_data).meme
            meme.make_img()
            log(ctx.author, ' - meme generated:', meme)

            msgstr = "{2} here's a meme (using template `{0}`){1}".format(
                meme.template_link,
                DISCORD_SEND_ATTACHMENTS and ' ' or ('\n' + meme.get_info_url()),
                ctx.author.mention
            )

        await ctx.send(msgstr, file=DISCORD_SEND_ATTACHMENTS and discord.File(meme.local_path) or None)

    @commands.command(name='submit', help='submit a source image', usage='<image>')
    @commands.cooldown(config.DISCORD_MEME_LIMIT, config.DISCORD_MEME_COOLDOWN, BucketType.user)
    @image_required()
    async def _cmd_submit(self, ctx: DiscordContext):
        added = 0
        imgcount = len(ctx.images)
        async with ctx.typing():
            for img in ctx.images:
                submitted_file = img.save()
                submission = ctx.user_data.submit_sourceimg(channel=ctx.channel_data, path=submitted_file, filename=img.filename)
                img.cleanup()
                if submission is not None:
                    added += 1
                    log(ctx.author, 'sourceimg submitted:', submission.sourceimg)

        if added == imgcount:
            if imgcount == 1:
                await ctx.send("{} thanks! The source image will be added once it's approved.".format(ctx.author.mention))
            else:
                await ctx.send("{} thanks! The source images will be added once they're approved.".format(ctx.author.mention))
        else:
            if imgcount == 1:
                raise BadArgument("the image is too big or invalid format! (supported jpeg/png < {} KB)".format(MAX_SRCIMG_SIZE / 1000))
            else:
                raise BadArgument("{}/{} images submitted. The rest is too big or invalid format! (supported jpeg/png < {} KB)".format(added, imgcount, MAX_SRCIMG_SIZE / 1000))


def setup(bot: Bot):
    bot.add_cog(MemeGeneratorCog(bot))
