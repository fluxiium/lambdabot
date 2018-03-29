import discord
import config
from discord.ext import commands
from discord.ext.commands import Bot, BadArgument, BucketType, CommandOnCooldown, MissingRequiredArgument, CommandError
from discordbot.util import log, DiscordContext, DiscordImage
from lamdabotweb.settings import MAX_SRCIMG_SIZE, DISCORD_SEND_ATTACHMENTS
from memeviewer.models import MemeTemplate
from memeviewer.preview import preview_meme


class MemeGeneratorCog:
    def __init__(self, bot: Bot):
        self.cog_name = "Meme generator"
        self.bot = bot

    @commands.command(
        name='meme',
        help='generate a random meme\n'
             'you can specify a template to use for the meme\n'
             'use `^` to use the template of the last meme generated',
        aliases=['meem', 'mem', 'meemay', 'memuch', 'miejm']
    )
    @commands.cooldown(config.DISCORD_MEME_LIMIT, config.DISCORD_MEME_COOLDOWN, BucketType.user)
    async def _cmd_meem(self, ctx: DiscordContext, *, template_name=None):
        template = None

        if template_name == '^':
            template = MemeTemplate.find(ctx.server_data.context)
        elif template_name:
            template = MemeTemplate.find(template_name)

        if template_name and not template:
            raise BadArgument("template `{0}` not found :cry:".format(template_name))

        meme = ctx.member_data.generate_meme(template=template, channel=ctx.message.channel).meme
        preview_meme(meme)
        log(ctx.author, 'meme generated:', meme)

        msgstr = "{2} here's a meme (using template `{0}`){1}".format(
            meme.template_link,
            DISCORD_SEND_ATTACHMENTS and '' or ('\n' + meme.get_info_url()),
            ctx.author.mention
        )

        await ctx.send(msgstr, file=DISCORD_SEND_ATTACHMENTS and discord.File(meme.get_local_path()) or None)

    @commands.command(
        name='submit',
        help='submit a source image',
        usage='(attachment | embed)'
    )
    @commands.cooldown(config.DISCORD_MEME_LIMIT, config.DISCORD_MEME_COOLDOWN, BucketType.user)
    async def _cmd_submit(self, ctx: DiscordContext):
        images = DiscordImage.get_from_message(ctx.message)
        imgcount = len(images)

        if imgcount < 1:
            raise CommandError("please add an attachment or embed")

        added = 0

        for attachment in images:
            submitted_file = attachment.save()
            submission = ctx.member_data.submit_sourceimg(submitted_file, attachment.filename)
            if submission is not None:
                added += 1
                log('sourceimg submitted by {}: {}'.format(ctx.author, submission.sourceimg))

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

    @_cmd_meem.error
    @_cmd_submit.error
    async def _meem_error(self, ctx: DiscordContext, error):
        if isinstance(error, CommandOnCooldown):
            await ctx.send("{0} you're memeing too fast! Please wait {1} seconds.".format(ctx.author.mention, int(error.retry_after)))
        elif isinstance(error, CommandError):
            await ctx.send("{} {}".format(ctx.author.mention, str(error)))


def setup(bot: Bot):
    bot.add_cog(MemeGeneratorCog(bot))
