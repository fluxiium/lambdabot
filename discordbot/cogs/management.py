from discord.ext.commands import Bot, BadArgument, guild_only, Command
from discordbot.models import DiscordContext, DiscordChannel
from discordbot.util import discord_command, management_cmd, CommandParam


class ManagementCog:

    def __init__(self, bot: Bot):
        self.cog_name = "Management"
        self.bot = bot

    async def __toggle_cmd(self, ctx: DiscordContext, cmd: Command, data):
        if not cmd:
            return await ctx.send("{} currently disabled commands{}: ```{} ```".format(
                ctx.author.mention,
                isinstance(data, DiscordChannel) and ' in `#{}`'.format(ctx.channel.name) or '',
                ', '.join(data.disabled_cmds.strip().split('\n'))
            ))
        if cmd.name in ['svcmd', 'cmd']:
            raise BadArgument('nope.avi')
        enabled = data.toggle_command(cmd.name)
        await ctx.send("{} command `{}` is now {}abled{}".format(
            ctx.author.mention,
            cmd.name,
            enabled and 'en' or 'dis',
            isinstance(data, DiscordChannel) and ' in `#{}`'.format(ctx.channel.name) or '',
        ))

    @discord_command(name='svcmd', help='toggle command serverwide')
    @management_cmd()
    async def _cmd_svcmd(self, ctx: DiscordContext, cmd: CommandParam()=None):
        await self.__toggle_cmd(ctx, cmd, ctx.server_data)

    @discord_command(name='cmd', help='toggle command in current channel')
    @management_cmd()
    async def _cmd_cmd(self, ctx: DiscordContext, cmd: CommandParam()=None):
        await self.__toggle_cmd(ctx, cmd, ctx.channel_data)

    @discord_command(name='prefix', help='set command prefix')
    @management_cmd()
    async def _cmd_prefix(self, ctx: DiscordContext, prefix):
        ctx.server_data.prefix = prefix
        ctx.server_data.save()
        await ctx.send('{} command prefix on this server is now set to `{}`'.format(ctx.author.mention, prefix))

def setup(bot: Bot):
    bot.add_cog(ManagementCog(bot))
