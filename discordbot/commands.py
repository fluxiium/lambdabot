from discordbot.cmd_control_fun import cmd_say, cmd_saych
from discordbot.cmd_fun import cmd_help, cmd_meem, cmd_led, cmd_mario, cmd_noviews, cmd_wiki, cmd_test, cmd_eval2

COMMANDS = {}


def add_command(fun):
    COMMANDS[fun.__name__] = fun


def get_command(name):
    return COMMANDS.get('cmd_' + name)


def init_commands():
    add_command(cmd_help)
    add_command(cmd_meem)
    add_command(cmd_led)
    add_command(cmd_mario)
    add_command(cmd_noviews)
    add_command(cmd_wiki)
    add_command(cmd_test)
    add_command(cmd_eval2)

    add_command(cmd_saych)
    add_command(cmd_say)
