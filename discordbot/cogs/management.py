import asyncio
import inspect
import io
import textwrap
import traceback
from contextlib import redirect_stdout
from typing import Union, List
import discord
from discord.ext import commands
from discord.ext.commands import Bot, Command, Cog
from discordbot import checks
from discordbot.models import DiscordContext, DiscordChannel, DiscordServer
from discordbot.param_types import CommandParam


class ManagementCog(Cog):

    def __init__(self, bot: Bot):
        self.__cog_name__ = "Management"
        self.bot = bot
        self._last_result = None
        self._sessions = set()

    @staticmethod
    async def list_cmds(ctx: DiscordContext, data):
        return await ctx.send("{} currently disabled commands{}: ```{} ```".format(
            ctx.author.mention,
            isinstance(data, DiscordChannel) and f' in `#{ctx.channel.name}`' or '',
            ' '.join(data.disabled_cmds.strip().split('\n'))
        ))

    @staticmethod
    async def toggle_cmds(ctx: DiscordContext, cmds: List[Command], data: Union[DiscordChannel, DiscordServer], enable):
        cmd_names = []
        for cmd in cmds:
            if cmd.name not in ['svcmd', 'cmd']:
                cmd_names.append(cmd.name)
                data.toggle_command(cmd.name, enable)
        await ctx.send("{} the following commands have been {}abled{}: ```{} ```".format(
            ctx.author.mention,
            enable and 'en' or 'dis',
            isinstance(data, DiscordChannel) and f' in `#{ctx.channel.name}`' or '',
            ' '.join(cmd_names),
        ))

    @checks.guild_only()
    @commands.group(name='svcmd', hidden=True, invoke_without_command=True)
    async def cmd_svcmd(self, ctx: DiscordContext):
        """
        enable/disable commands in this server
        if no argument is given, shows a list of currently disabled commands
        """
        await self.list_cmds(ctx, ctx.server_data)

    @checks.management_only()
    @cmd_svcmd.command(name='on')
    async def cmd_svcmd_on(self, ctx: DiscordContext, *, cmds: CommandParam(many = True)):
        await self.toggle_cmds(ctx, cmds, ctx.server_data, True)

    @checks.management_only()
    @cmd_svcmd.command(name='off')
    async def cmd_svcmd_off(self, ctx: DiscordContext, *, cmds: CommandParam(many = True)):
        await self.toggle_cmds(ctx, cmds, ctx.server_data, False)

    @checks.guild_only()
    @commands.group(name='cmd', hidden=True, invoke_without_command=True)
    async def cmd_cmd(self, ctx: DiscordContext):
        """
        enable/disable commands in this channel
        if no argument is given, shows a list of currently disabled commands
        """
        await self.list_cmds(ctx, ctx.channel_data)

    @checks.management_only()
    @cmd_cmd.command(name='on')
    async def cmd_cmd_on(self, ctx: DiscordContext, *, cmds: CommandParam(many = True)):
        await self.toggle_cmds(ctx, cmds, ctx.channel_data, True)

    @checks.management_only()
    @cmd_cmd.command(name='off')
    async def cmd_cmd_off(self, ctx: DiscordContext, *, cmds: CommandParam(many = True)):
        await self.toggle_cmds(ctx, cmds, ctx.channel_data, False)

    @checks.management_only()
    @commands.command(name='prefix', hidden=True)
    async def cmd_prefix(self, ctx: DiscordContext, prefix):
        ctx.server_data.prefix = prefix
        ctx.server_data.save()
        await ctx.send(f'{ctx.author.mention} command prefix on this server is now set to `{prefix}`')

    # noinspection PyBroadException
    @checks.yackson_only()
    @commands.command(name='eval', hidden=True)
    async def cmd_eval(self, ctx: DiscordContext, *, body: str):
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

        body = body.strip('` \n')
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception:
            value = stdout.getvalue()
            await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()

            if ret is None:
                if value:
                    await ctx.send(f'```py\n{value}\n```')
            else:
                self._last_result = ret
                await ctx.send(f'```py\n{value}{ret}\n```')

    # noinspection PyBroadException
    @checks.yackson_only()
    @commands.command(name='py', hidden=True)
    async def cmd_py(self, ctx: DiscordContext):
        """Launches an interactive REPL session."""
        variables = {
            'ctx': ctx,
            'bot': self.bot,
            'message': ctx.message,
            'guild': ctx.guild,
            'channel': ctx.channel,
            'author': ctx.author,
            '_': None,
        }

        if ctx.channel.id in self._sessions:
            await ctx.send('Already running a REPL session in this channel. Exit it with `quit`.')
            return

        self._sessions.add(ctx.channel.id)
        await ctx.send('Enter code to execute or evaluate. `exit()` or `quit` to exit.')

        def check(m):
            return m.author.id == ctx.author.id and \
                   m.channel.id == ctx.channel.id and \
                   m.content.startswith('`')

        while True:
            try:
                response = await self.bot.wait_for('message', check=check, timeout=10.0 * 60.0)
            except asyncio.TimeoutError:
                await ctx.send('Exiting REPL session.')
                self._sessions.remove(ctx.channel.id)
                break

            cleaned = response.content.strip('` \n')

            if cleaned in ('quit', 'exit', 'exit()'):
                await ctx.send('Exiting.')
                self._sessions.remove(ctx.channel.id)
                return

            executor = exec
            if cleaned.count('\n') == 0:
                # single statement, potentially 'eval'
                try:
                    code = compile(cleaned, '<repl session>', 'eval')
                except SyntaxError:
                    pass
                else:
                    executor = eval

            if executor is exec:
                try:
                    code = compile(cleaned, '<repl session>', 'exec')
                except SyntaxError as e:
                    if e.text is None:
                        await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')
                    else:
                        await ctx.send(f'```py\n{e.text}{"^":>{e.offset}}\n{e.__class__.__name__}: {e}```')
                    continue

            variables['message'] = response

            fmt = None
            stdout = io.StringIO()

            try:
                with redirect_stdout(stdout):
                    result = executor(code, variables)
                    if inspect.isawaitable(result):
                        result = await result
            except Exception as e:
                value = stdout.getvalue()
                fmt = f'```py\n{value}{traceback.format_exc()}\n```'
            else:
                value = stdout.getvalue()
                if result is not None:
                    fmt = f'```py\n{value}{result}\n```'
                    variables['_'] = result
                elif value:
                    fmt = f'```py\n{value}\n```'

            try:
                if fmt is not None:
                    if len(fmt) > 2000:
                        await ctx.send('Content too big to be printed.')
                    else:
                        await ctx.send(fmt)
            except discord.Forbidden:
                pass
            except discord.HTTPException as e:
                await ctx.send(f'Unexpected error: `{e}`')


def setup(bot: Bot):
    bot.add_cog(ManagementCog(bot))
