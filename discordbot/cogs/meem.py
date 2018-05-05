from django.core.files import File
import discord
import lamdabotweb.settings as config
from typing import List
from discord.ext import commands
from discord.ext.commands import Bot, BadArgument, BucketType, CommandError
from discordbot.util import MemeTemplateParam, ImagePoolParam, discord_command
from discordbot.models import log, DiscordContext, DiscordSourceImgSubmission
from memeviewer.models import NotEnoughImages, MemeImagePool, MemeSourceImage, POOL_TYPE_SRCIMGS, POOL_TYPE_ALL


class MemeGeneratorCog:

    def __init__(self, bot: Bot):
        self.cog_name = "Meme generator"
        self.bot = bot

    @discord_command(name='meme', aliases=['meem', 'mem', 'meemay', 'memuch', 'miejm'], guild_only=True)
    @commands.cooldown(config.DISCORD_MEME_LIMIT, config.DISCORD_MEME_COOLDOWN, BucketType.user)
    @commands.bot_has_permissions(attach_files=True)
    async def _cmd_meem(self, ctx: DiscordContext, *, template: MemeTemplateParam()=None):
        """
        generate a random meme
        you can specify a template to use for the meme
        use `^` to use the template of the last meme generated in this channel
        """
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
            raise CommandError('not enough source images or templates available (please enable more image pools)')

        await ctx.send(msgstr, file=discord.File(meme.local_path))

    @discord_command(name='submit', usage='[image pool] <images...>', guild_only=True, image_required=True)
    @commands.cooldown(config.DISCORD_MEME_LIMIT, config.DISCORD_MEME_COOLDOWN, BucketType.user)
    async def _cmd_submit(self, ctx: DiscordContext, pool: ImagePoolParam(avail_only=True, ignore_urls=True) = None):
        """
        submit a source image
        you can specify an image pool to submit to (use !pool to see a list)
        otherwise, the channel's default pool will be used
        """
        if pool is None:
            pool = ctx.channel_data.submission_pool
            if pool is None:
                raise CommandError('no default submission pool is set for this channel, please specify')
        if pool.pool_type not in [POOL_TYPE_SRCIMGS, POOL_TYPE_ALL]:
            raise CommandError('source images cannot be added to this image pool')
        added = 0
        imgcount = len(ctx.images)
        async with ctx.typing():
            for img in ctx.images:
                submitted_file = img.save()
                srcimg = MemeSourceImage(image_pool=pool, friendly_name=img.filename)
                srcimg.image_file.save(srcimg.name + '.jpg', File(open(submitted_file, "rb")))
                srcimg.save()
                submission = DiscordSourceImgSubmission.objects.create(sourceimg=srcimg, discord_user=ctx.user_data, discord_channel=ctx.channel_data)
                img.cleanup()
                if submission is not None:
                    added += 1
                    log(ctx.author, 'sourceimg submitted:', submission.sourceimg)

        if added == imgcount:
            if imgcount == 1:
                await ctx.send("{} thanks! The source image will be added to the pool `{}` once it's approved.".format(ctx.author.mention, pool))
            else:
                await ctx.send("{} thanks! The source images will be added to the pool `{}` once they're approved.".format(ctx.author.mention, pool))
        else:
            if imgcount == 1:
                raise BadArgument("the image is too big or invalid format! (supported jpeg/png < {} KB)".format(config.MAX_SRCIMG_SIZE / 1000))
            else:
                raise BadArgument("{}/{} images submitted. The rest is too big or invalid format! (supported jpeg/png < {} KB)".format(added, imgcount, config.MAX_SRCIMG_SIZE / 1000))

    @discord_command(name='pool', usage='[add <pools...> | remove <pools...>]', guild_only=True, group=True)
    async def _cmd_pool(self, ctx: DiscordContext):
        """
        select which image pools are used to make memes in this channel
        if no argument is given, shows a list of currently enabled image pools
        """
        pools = ctx.channel_data.image_pools.values_list('name', flat=True)
        avail = ctx.user_data.available_pools().exclude(name__in=pools).values_list('name', flat=True)
        return await ctx.send("{} currently enabled image pools in `#{}`: ```{} ```{}".format(
            ctx.author.mention,
            ctx.channel.name,
            ' '.join(pools),
            ctx.is_manager and '\navailable pools: ```{} ```'.format(' '.join(avail)) or '',
        ))

    @staticmethod
    async def __toggle_pools(ctx: DiscordContext, pools: List[MemeImagePool], enable):
        pool_names = []
        for pool in pools:
            assert isinstance(pool, MemeImagePool)
            pool_names.append(pool.name)
            if enable:
                ctx.channel_data.image_pools.add(pool)
            else:
                ctx.channel_data.image_pools.remove(pool)
        await ctx.send("{} the following image pools are now {}abled in `#{}`: ```{} ```".format(
            ctx.author.mention,
            enable and 'en' or 'dis',
            ctx.channel.name,
            ' '.join(pool_names),
        ))

    @discord_command(parent=_cmd_pool, name='add', management=True)
    async def _cmd_pool_add(self, ctx: DiscordContext, *, pools: ImagePoolParam(many=True, avail_only=True)):
        await self.__toggle_pools(ctx, pools, True)

    @discord_command(parent=_cmd_pool, name='remove', management=True)
    async def _cmd_pool_remove(self, ctx: DiscordContext, *, pools: ImagePoolParam(many=True, avail_only=True)):
        await self.__toggle_pools(ctx, pools, False)

    @discord_command(name='subpool', management=True)
    async def _cmd_subpool(self, ctx: DiscordContext, *, pool: ImagePoolParam()=None):
        """ set the default image pool used for submissions in this channel """
        if not pool:
            avail = ctx.user_data.available_pools().values_list('name', flat=True)
            if ctx.channel_data.submission_pool:
                avail = avail.exclude(pk=ctx.channel_data.submission_pool.pk)
            return await ctx.send("{} current submission pool for `#{}`: ```{} ```\navailable pools: ```{} ```".format(
                ctx.author.mention,
                ctx.channel.name,
                ctx.channel_data.submission_pool or '',
                ' '.join(avail)
            ))
        assert isinstance(pool, MemeImagePool)
        ctx.channel_data.submission_pool = pool
        ctx.channel_data.save()
        await ctx.send("{} submission pool for `#{}` set to `{}`".format(ctx.author.mention, ctx.channel.name, pool))


def setup(bot: Bot):
    bot.add_cog(MemeGeneratorCog(bot))
