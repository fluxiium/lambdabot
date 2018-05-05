import asyncio
import itertools
from discord.ext.commands.bot import _default_help_command
from discord.ext.commands.core import Command
from discord.ext.commands import HelpFormatter, Bot, Paginator, Context
from discordbot.util import discord_command
import lamdabotweb.settings as config


class CustomHelpFormatter(HelpFormatter):
    def _add_subcommands_to_page(self, _, commands):
        for name, command in commands:
            if name in command.aliases:
                continue
            entry = '  {} {}'.format(command.name, command.parameter_help)
            self._paginator.add_line(entry)

    @asyncio.coroutine
    def format(self):
        self._paginator = Paginator(prefix='```', suffix='```')

        if isinstance(self.command, Command):
            # <signature portion>
            self._paginator.add_line('{} {}'.format(self.command.name, self.command.parameter_help))
            if len(self.command.aliases) > 0:
                self._paginator.add_line('aliases: ' + ', '.join(self.command.aliases))
            self._paginator.add_line()

            # <long doc> section
            if self.command.help:
                self._paginator.add_line(self.command.help, empty=True)

            # end it here if it's just a regular command
            if not self.has_subcommands():
                self._paginator.close_page()
                return self._paginator.pages

        def category(tup):
            cog = tup[1].cog_name
            # we insert the zero width space there to give it approximate
            # last place sorting position.
            return cog if cog is not None else '\u200bOther'

        filtered = yield from self.filter_command_list()
        if self.is_bot():
            data = sorted(filtered, key=category)
            for category, commands in itertools.groupby(data, key=category):
                # there simply is no prettier way of doing this.
                commands = sorted(commands)
                if len(commands) > 0:
                    self._paginator.add_line(category)
                    self._add_subcommands_to_page(0, commands)
        else:
            filtered = sorted(filtered)
            if filtered:
                self._paginator.add_line('Commands:')
                self._add_subcommands_to_page(0, filtered)

        self._paginator.add_line('Visit lambdabot.morchkovalski.com for more info')
        return self._paginator.pages

@discord_command(name='invite')
async def _cmd_invite(ctx: Context):
    await ctx.send('{} use this link to add the bot to your server: {}invite'.format(ctx.author.mention, config.WEBSITE_URL))

def setup(bot: Bot):
    bot.remove_command('help')
    cmd_help = discord_command(name='help', help='show more info about command', usage='[command]')(_default_help_command)
    bot.add_command(cmd_help)
    bot.formatter = CustomHelpFormatter(show_check_failure=True)
    bot.add_command(_cmd_invite)
