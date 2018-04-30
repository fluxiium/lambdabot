import discord
import config
from discord.ext import commands
from discord.ext.commands import Bot, BadArgument, BucketType, CommandError, guild_only
from discordbot.util import image_required, MemeTemplateParam, ImagePoolParam, discord_command, management_cmd
from discordbot.models import log, DiscordContext
from lamdabotweb.settings import MAX_SRCIMG_SIZE
from memeviewer.models import NotEnoughImages, MemeImagePool


class MemeGeneratorCog:

    def __init__(self, bot: Bot):
        self.cog_name = "Meme generator"
        self.bot = bot

    @discord_command(
        name='meme',
        help='generate a random meme\n'
             'you can specify a template to use for the meme\n'
             'use `^` to use the template of the last meme generated in this channel',
        aliases=['meem', 'mem', 'meemay', 'memuch', 'miejm'],
        usage='[[template_name] | ^]',
    )
    @commands.cooldown(config.DISCORD_MEME_LIMIT, config.DISCORD_MEME_COOLDOWN, BucketType.user)
    @guild_only()
    async def _cmd_meem(self, ctx: DiscordContext, *, template: MemeTemplateParam()=None):
        try:
            async with ctx.typing():
                meme = ctx.user_data.generate_meme(template=template, channel=ctx.channel_data).meme
                meme.make_img()
                log(ctx.author, ' - meme generated:', meme)

                msgstr = "{2} here's a meme (using template `{0}`)\n<{1}>".format(
                    meme.template_link,
                    meme.info_url,
                    ctx.author.mention
                )
        except NotEnoughImages:
            raise CommandError('no image pools enabled in this channel.')

        await ctx.send(msgstr, file=discord.File(meme.local_path))

    @discord_command(name='submit', help='submit a source image', usage='<image>')
    @commands.cooldown(config.DISCORD_MEME_LIMIT, config.DISCORD_MEME_COOLDOWN, BucketType.user)
    @guild_only()
    @image_required()
    async def _cmd_submit(self, ctx: DiscordContext):
        if ctx.channel_data.submission_pool is None:
            raise CommandError('submission pool is not set for this channel')
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

    @discord_command(name='pool', help='enable/disable image pool in current channel')
    @management_cmd()
    async def _cmd_pool(self, ctx: DiscordContext, *, pool: ImagePoolParam()=None):
        if not pool:
            pools = ctx.channel_data.image_pools.values_list('name', flat=True)
            return await ctx.send("{} currently enabled image pools in `#{}`: ```{} ```\navailable pools: ```{} ```".format(
                ctx.author.mention,
                ctx.channel.name,
                ', '.join(pools),
                ', '.join(MemeImagePool.objects.exclude(name__in=pools).values_list('name', flat=True))
            ))
        assert isinstance(pool, MemeImagePool)
        enabled = ctx.channel_data.image_pools.filter(pk=pool.pk).first() and True or False
        if enabled:
            ctx.channel_data.image_pools.remove(pool)
        else:
            ctx.channel_data.image_pools.add(pool)
        await ctx.send("{} image pool `#{}` is now {}abled in `#{}`".format(
            ctx.author.mention,
            pool,
            enabled and 'dis' or 'en',
            ctx.channel.name
        ))

    @discord_command(name='subpool', help='set the default image pool used for submissions')
    @management_cmd()
    async def _cmd_subpool(self, ctx: DiscordContext, *, pool: ImagePoolParam()=None):
        if not pool:
            avail = MemeImagePool.objects.values_list('name', flat=True)
            if ctx.channel_data.submission_pool:
                avail = avail.exclude(pk=ctx.channel_data.submission_pool.pk)
            return await ctx.send("{} current submission pool for `#{}`: ```{}```\navailable pools: ```{} ```".format(
                ctx.author.mention,
                ctx.channel.name,
                ctx.channel_data.submission_pool or '(none)',
                ', '.join(avail)
            ))
        assert isinstance(pool, MemeImagePool)
        ctx.channel_data.submission_pool = pool
        ctx.channel_data.save()
        await ctx.send("{} submission pool for `#{}` set to `{}`".format(ctx.author.mention, ctx.channel.name, pool))


def setup(bot: Bot):
    bot.add_cog(MemeGeneratorCog(bot))
