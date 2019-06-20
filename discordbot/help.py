from discord.ext.commands import DefaultHelpCommand


class HelpCommand(DefaultHelpCommand):
    def get_ending_note(self):
        return f"Type {self.clean_prefix}{self.invoked_with} [command] for more info on a command."
