import io
import textwrap
import traceback
from contextlib import redirect_stdout
from typing import Union, List
from discord.ext.commands import Bot, Command
from discordbot.models import DiscordContext, DiscordChannel, DiscordServer
from discordbot.util import discord_command, CommandParam


class ManagementCog:

    def __init__(self, bot: Bot):
        self.cog_name = "Management"
        self.bot = bot
        self._last_result = None

    @staticmethod
    async def __list_cmds(ctx: DiscordContext, data):
        return await ctx.send("{} currently disabled commands{}: ```{} ```".format(
            ctx.author.mention,
            isinstance(data, DiscordChannel) and ' in `#{}`'.format(ctx.channel.name) or '',
            ' '.join(data.disabled_cmds.strip().split('\n'))
        ))

    @staticmethod
    async def __toggle_cmds(ctx: DiscordContext, cmds: List[Command], data: Union[DiscordChannel, DiscordServer], enable):
        cmd_names = []
        for cmd in cmds:
            if cmd.name not in ['svcmd', 'cmd']:
                cmd_names.append(cmd.name)
                data.toggle_command(cmd.name, enable)
        await ctx.send("{} the following commands have been {}abled{}: ```{} ```".format(
            ctx.author.mention,
            enable and 'en' or 'dis',
            isinstance(data, DiscordChannel) and ' in `#{}`'.format(ctx.channel.name) or '',
            ' '.join(cmd_names),
        ))

    @discord_command(name='svcmd', usage='[on <commands...> | off <commands...>]', group=True, management=True, enabled=True)
    async def _cmd_svcmd(self, ctx: DiscordContext):
        """
        enable/disable commands in this server
        if no argument is given, shows a list of currently disabled commands
        """
        await self.__list_cmds(ctx, ctx.server_data)

    @discord_command(parent=_cmd_svcmd, name='on', management=True, enabled=True)
    async def _cmd_svcmd_on(self, ctx: DiscordContext, *, cmds: CommandParam(many=True)):
        await self.__toggle_cmds(ctx, cmds, ctx.server_data, True)

    @discord_command(parent=_cmd_svcmd, name='off', management=True, enabled=True)
    async def _cmd_svcmd_off(self, ctx: DiscordContext, *, cmds: CommandParam(many=True)):
        await self.__toggle_cmds(ctx, cmds, ctx.server_data, False)

    @discord_command(name='cmd', usage='[on <commands...> | off <commands...>]', group=True, management=True, enabled=True)
    async def _cmd_cmd(self, ctx: DiscordContext):
        """
        enable/disable commands in this channel
        if no argument is given, shows a list of currently disabled commands
        """
        await self.__list_cmds(ctx, ctx.channel_data)

    @discord_command(parent=_cmd_cmd, name='on', management=True, enabled=True)
    async def _cmd_cmd_on(self, ctx: DiscordContext, *, cmds: CommandParam(many=True)):
        await self.__toggle_cmds(ctx, cmds, ctx.channel_data, True)

    @discord_command(parent=_cmd_cmd, name='off', management=True, enabled=True)
    async def _cmd_cmd_off(self, ctx: DiscordContext, *, cmds: CommandParam(many=True)):
        await self.__toggle_cmds(ctx, cmds, ctx.channel_data, False)

    @discord_command(name='prefix', management=True)
    async def _cmd_prefix(self, ctx: DiscordContext, prefix):
        ctx.server_data.prefix = prefix
        ctx.server_data.save()
        await ctx.send('{} command prefix on this server is now set to `{}`'.format(ctx.author.mention, prefix))

    # noinspection PyBroadException
    @discord_command(name='epic', yack_only=True)
    async def _eval(self, ctx, *, body: str):
        """Evaluates a code"""

        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result
        }

        env.update(globals())

        if body.startswith('```') and body.endswith('```'):
            return '\n'.join(body.split('\n')[1:-1])

        body = body.strip('` \n')
        stdout = io.StringIO()

        to_compile = 'async def func():\n{}'.format(textwrap.indent(body, "  "))

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send('```py\n{}: {}\n```'.format(e.__class__.__name__, e))

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception:
            value = stdout.getvalue()
            await ctx.send('```py\n{}{}\n```'.format(value, traceback.format_exc()))
        else:
            value = stdout.getvalue()

            if ret is None:
                if value:
                    await ctx.send('```py\n{}\n```'.format(value))
            else:
                self._last_result = ret
                await ctx.send('```py\n{}{}\n```'.format(value, ret))


def setup(bot: Bot):
    bot.add_cog(ManagementCog(bot))
