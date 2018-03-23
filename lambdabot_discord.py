import os
import asyncio
import shlex
import django
import discord
import re
import lamdabotweb.settings as config

from importlib import import_module

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lamdabotweb.settings")
django.setup()

import discordbot.murphybot as murphy
import discordbot.cleverbot as cleverboi
from discordbot.util import log, get_server, get_member, get_attachments, save_attachment
from discordbot.models import MurphyRequest
from discordbot.classes import DiscordSyntaxException, DiscordCommandException, DiscordCommandResponse

log("")
log("##############################")
log("#  LambdaBot 3883 - Discord  #")
log("##############################")
log("")

_client = discord.Client(max_messages=10000)


_COMMANDS = {}
_COMMAND_ALIASES = {}
for file in os.listdir(os.path.join(config.BASE_DIR, 'discordbot', 'commands')):
    if file.startswith('__') or not file.endswith('.py'):
        continue
    md = import_module('discordbot.commands.' + os.path.splitext(file)[0])
    _COMMANDS.update(md.COMMANDS)
    _COMMAND_ALIASES.update(md.COMMAND_ALIASES)


# noinspection PyShadowingNames
async def _cmd_help(server, message, **_):
    helpstr = "available commands:".format(message.author.mention)

    for cmd_name, cmd_data in _COMMANDS.items():

        helpstr += "\n`{0}{1}".format(server.prefix, cmd_name)

        if cmd_data.get('usage'):
            helpstr += " {}`".format(cmd_data['usage'])
        else:
            helpstr += "`"

        if cmd_data.get('help'):
            helpstr += " - {0}".format(cmd_data['help'])

    for cmd_data in server.get_commands():
        helpstr += "\n`{0}{1}`".format(server.prefix, cmd_data.cmd)

    return DiscordCommandResponse(helpstr)

_COMMANDS['help'] = {
    'function': _cmd_help,
}


@_client.event
async def process_message(message):
    msg = message.content.strip()

    server = get_server(message)

    if re.search("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", msg) is not None:
        await asyncio.sleep(2)

    if server is None or message.author.id == _client.user.id:
        return

    member = get_member(message, server)
    atts = get_attachments(message)

    if _client.user in message.mentions:

        if msg.startswith(_client.user.mention):
            msg = msg.replace(_client.user.mention, "", 1).strip()
        elif msg.endswith(_client.user.mention):
            msg = msg.rsplit(_client.user.mention, 1)[0].strip()
        else:
            return

        log("{0}, {1} mention: {2}".format(server.name, message.author.name, msg))

        answered = True

        for att in atts:
            if att['is_embed']:
                msg = msg.replace(att['real_url'], "", 1).strip()

        if murphy.is_active() and not message.author.bot:
            att = atts[0] if len(atts) > 0 else None
            if msg.lower().startswith("what if i ") or (msg == "" and att is not None):
                face_pic = save_attachment(att['real_url']) if att is not None else ''
                if msg == "" and att is not None:
                    MurphyRequest.ask(server_user=member, channel_id=message.channel.id, face_pic=face_pic)
                elif msg != "":
                    MurphyRequest.ask(question=msg, server_user=member, channel_id=message.channel.id, face_pic=face_pic)

            elif msg.lower().startswith("what if "):
                MurphyRequest.ask(question=msg, server_user=member, channel_id=message.channel.id)

            else:
                answered = False

        if msg and (not answered or not murphy.is_active()) and cleverboi.is_active():
            await cleverboi.talk(_client, message.channel, member, msg)

        if not msg and len(atts) == 0:
            msg = server.prefix + "help"
        else:
            return

    if not msg.startswith(server.prefix) or message.author.bot:
        return

    try:
        splitcmd = shlex.split(msg[len(server.prefix):])
    except ValueError:
        splitcmd = msg[len(server.prefix):].split(' ')

    if len(splitcmd) == 0:
        return

    cmd = server.get_cmd(splitcmd[0])

    if cmd is not None:
        await _client.send_typing(message.channel)
        await _client.send_message(message.channel, cmd.message)
        return

    cmd = _COMMANDS.get(_COMMAND_ALIASES.get(splitcmd[0]) or splitcmd[0])
    if cmd is None:
        return

    cmd_fun = cmd.get('function')
    if cmd_fun is None:
        return

    await _client.send_typing(message.channel)

    try:
        response = await cmd_fun(
            client=_client,
            server=server,
            member=member,
            message=message,
            args=splitcmd,
            argstr=msg[(len(server.prefix) + len(splitcmd[0])):].strip(),
            attachments=atts,
        )
    except DiscordSyntaxException:
        response = DiscordCommandResponse("usage: `{}{} {}`".format(server.prefix, splitcmd[0], cmd.get('usage', '')))
    except DiscordCommandException:
        response = DiscordCommandResponse("error :cry:")

    await response.send(_client, message)


@_client.event
async def on_message(message):
    await process_message(message)


@_client.event
async def on_message_edit(old_message, message):
    pass


@_client.event
async def on_message_delete(message):
    pass


@_client.event
async def on_ready():
    log('Logged in as', _client.user.name, _client.user.id)
    await _client.change_presence(game=discord.Game(name=config.DISCORD_STATUS))

murphy.start(_client)
_client.run(config.DISCORD_TOKEN)
