import asyncio
import itertools
from discord.ext.commands.core import Command
from discord.ext.commands import HelpFormatter, Bot, Paginator
from django.core.exceptions import ObjectDoesNotExist
from discordbot.models import DiscordServer


# noinspection PyAttributeOutsideInit,PyTypeChecker
class CustomHelpFormatter(HelpFormatter):
    def _add_subcommands_to_page(self, _, commands):
        for name, command in commands:
            if name in command.aliases:
                continue
            entry = '{}{} {}{}{}'.format(
                self.context.prefix,
                command.name,
                command.parameter_help,
                command.short_doc and ' - ' or '',
                command.short_doc
            )
            self._paginator.add_line(entry)

    @asyncio.coroutine
    def format(self):
        self._paginator = Paginator(prefix='', suffix='')

        if isinstance(self.command, Command):
            # <signature portion>
            signature = self.get_command_signature()
            self._paginator.add_line("```{}```".format(signature))

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
                    self._paginator.add_line("**:: {} ::**".format(category))
                    self._paginator.add_line("```")
                    self._add_subcommands_to_page(0, commands)
                    self._paginator.add_line("```")
            server_commands = self.context.server_data and self.context.server_data.get_commands() or []
            if len(server_commands) > 0:
                self._paginator.add_line("**:: Custom ::**".format(self.context.guild.name))
                self._paginator.add_line("```")
                cmds = ""
                for cmd_data in server_commands:
                    cmds += '{0}{1}, '.format(self.context.prefix, cmd_data.cmd)
                self._paginator.add_line(cmds[:-2])
                self._paginator.add_line("```")
        else:
            filtered = sorted(filtered)
            if filtered:
                self._paginator.add_line('Commands:')
                self._paginator.add_line("```")
                self._add_subcommands_to_page(0, filtered)
                self._paginator.add_line("```")

        return self._paginator.pages


def setup(bot: Bot):
    bot.formatter = CustomHelpFormatter()
