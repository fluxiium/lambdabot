import os
import asyncio
import requests
import shlex
import textwrap
import django
import discord
import re

from discord import Embed
from discord import Status, Server, Game, Channel
from discord.state import ConnectionState
from django.utils import timezone

# noinspection PyBroadException,PyArgumentList
def _sync_patched(self, data):
    if 'large' in data:
        self.large = data['large']

    for presence in data.get('presences', []):
        user_id = presence['user']['id']
        member = self.get_member(user_id)
        if member is not None:
            member.status = presence['status']
            try:
                member.status = Status(member.status)
            except:
                pass
            game = presence.get('game', {})
            try:
                member.game = Game(**game) if game else None
            except:
                member.game = None

    if 'channels' in data:
        channels = data['channels']
        for c in channels:
            channel = Channel(server=self, **c)
            self._add_channel(channel)


# noinspection PyBroadException,PyProtectedMember,PyArgumentList
def parse_presence_update_patched(self, data):
    server = self._get_server(data.get('guild_id'))
    if server is None:
        return

    status = data.get('status')
    user = data['user']
    member_id = user['id']
    member = server.get_member(member_id)
    if member is None:
        if 'username' not in user:
            # sometimes we receive 'incomplete' member data post-removal.
            # skip these useless cases.
            return

        member = self._make_member(server, data)
        server._add_member(member)

    old_member = member._copy()
    member.status = data.get('status')
    try:
        member.status = Status(member.status)
    except:
        pass

    game = data.get('game', {})
    try:
        member.game = Game(**game) if game else None
    except:
        member.game = None
    member.name = user.get('username', member.name)
    member.avatar = user.get('avatar', member.avatar)
    member.discriminator = user.get('discriminator', member.discriminator)

    self.dispatch('member_update', old_member, member)


# noinspection PyUnresolvedReferences
Server._sync = _sync_patched
ConnectionState.parse_presence_update = parse_presence_update_patched


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lamdabotweb.settings")
django.setup()

from discordbot.cleverbot import cb_talk
from discordbot.murphybot import start_murphy, is_murphy_active
from discordbot.util import log, get_server_and_member, get_attachment, delay_send, save_attachment, headers
from discordbot.commands import init_commands, get_command
from discordbot.models import ProcessedMessage, DiscordCommand, MurphyRequest
from memeviewer.models import Meem, MemeTemplate, AccessToken, MemeSourceImage, Setting

log("")
log("##############################")
log("#  LambdaBot 3883 - Discord  #")
log("##############################")
log("")

client = discord.Client(max_messages=10000)
init_commands()


@client.event
async def process_message(message, old_message=None):
    msg = message.content.strip()

    server, member = get_server_and_member(message)

    if re.search("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", msg) is not None:
        await asyncio.sleep(2)

    if server is None or ProcessedMessage.was_id_processed(message.id) or message.author.id == client.user.id:
        return

    att, dl_embed_url = get_attachment(message)
    control_channel = Setting.get("control channel")

    if att is not None:
        if dl_embed_url is None:
            requests.get(att['proxy_url'], headers=headers)
        ProcessedMessage.process_id(message.id)

    if client.user in message.mentions and message.channel.id != control_channel:

        if msg.startswith(client.user.mention):
            msg = msg.replace(client.user.mention, "", 1).strip()
        elif msg.endswith(client.user.mention):
            msg = msg.rsplit(client.user.mention, 1)[0].strip()
        else:
            return

        log("{0}, {1}: {2}".format(server.context, message.author.name, msg))
        ProcessedMessage.process_id(message.id)

        if msg == "" and att is None:
            await delay_send(client.send_typing, message.channel)
            await delay_send(
                client.send_message,
                message.channel,
                "{0} LambdaBot is a bot which generates completely random Half-Life memes. It does this by picking a "
                "random meme template and combining it with one or more randomly picked source images related to "
                "Half-Life. Currently there are **{1:,}** available templates and **{2:,}** available source images,"
                "for a total of **{3:,}** possible combinations.\n"
                "\n"
                "Type **!help** to see a list of available commands.\n"
                "\n"
                "*Homepage: https://lambdabot.morchkovalski.com\n"
                "Created by morch kovalski (aka yackson): https://morchkovalski.com*".format(
                    message.author.mention,
                    MemeTemplate.count(server.context),
                    MemeSourceImage.count(server.context),
                    Meem.possible_combinations(server.context)
                )
            )
            return

        answered = False

        if member.check_permission("murphybot") and is_murphy_active():
            answered = True

            if dl_embed_url is not None:
                msg = msg.replace(dl_embed_url, "", 1).strip()

            if msg.lower().startswith("what if i ") or (msg == "" and att is not None):
                face_pic = save_attachment(att['proxy_url'] if dl_embed_url is None else dl_embed_url)\
                    if att is not None else ''
                if msg == "" and att is not None:
                    MurphyRequest.ask(server_user=member, channel_id=message.channel.id, face_pic=face_pic)
                elif msg != "":
                    MurphyRequest.ask(question=msg, server_user=member, channel_id=message.channel.id, face_pic=face_pic)

            elif msg.lower().startswith("what if "):
                MurphyRequest.ask(question=msg, server_user=member, channel_id=message.channel.id)

            else:
                answered = False

        if not answered and member.check_permission("cleverbot"):
            await cb_talk(client, message.channel, member, msg)

        return

    if not msg.startswith(server.prefix):
        return

    try:
        splitcmd = shlex.split(msg[len(server.prefix):])
    except ValueError:
        splitcmd = msg[len(server.prefix):].split(' ')

    cmd = DiscordCommand.get_cmd(splitcmd[0])

    if cmd is None:
        return

    if cmd.check_permission(member):

        if cmd.is_control and message.channel.id != control_channel:
            return

        ProcessedMessage.process_id(message.id)

        log("{0}, {1}: {2}".format(
            server.context, message.author.name, msg
        ))

        if cmd.message is not None and len(cmd.message) > 0:
            await delay_send(client.send_typing, message.channel)
            await delay_send(client.send_message, message.channel, cmd.message)

        cmd_fun = get_command(cmd.cmd)
        if cmd_fun is not None:
            await cmd_fun(
                server=server,
                member=member,
                message=message,
                args=splitcmd,
                argstr=msg[(len(server.prefix) + len(splitcmd[0])):].strip(),
                attachment=att,
                dl_embed_url=dl_embed_url,
                client=client,
            )

        return

    if cmd.denied_message != "":
        await delay_send(client.send_typing, message.channel)
        await delay_send(client.send_message, message.channel, cmd.denied_message.replace("{user}", message.author.mention))


@client.event
async def on_message(message):
    await process_message(message)


@client.event
async def on_message_edit(old_message, message):
    server, member = get_server_and_member(message)
    att_old, _ = get_attachment(old_message)
    att_new, _ = get_attachment(message)

    if server is not None and server.log_channel != "" and (old_message.content != message.content) and \
            not member.check_permission('no edits log'):
        embed = Embed(
            description="**Message sent by {0} edited in <#{1}>**".format(message.author.mention, message.channel.id),
            color=0x117EA6,
        )
        embed.set_author(
            name=str(message.author),
            icon_url=message.author.avatar_url
        )
        embed.set_footer(
            text="ID: {0} | {1}".format(message.author.id, timezone.now().strftime("%a, %d %b %Y %I:%M %p")),
        )
        embed.add_field(
            name="Old message",
            value=textwrap.shorten(old_message.content, width=1000),
            inline=False,
        )
        embed.add_field(
            name="New message",
            value=textwrap.shorten(message.content, width=1000),
            inline=False,
        )

        await delay_send(client.send_message, client.get_channel(server.log_channel), embed=embed)

    await process_message(message, old_message)


@client.event
async def on_message_delete(message):
    server, member = get_server_and_member(message)
    att, dl_embed_url = get_attachment(message)

    if server is not None and server.log_channel != "" and not member.check_permission('no edits log') and \
            att is not None and dl_embed_url is None:
        att_path = save_attachment(att['proxy_url'], att['filename'])
        img_archive = Setting.get("img archive channel")
        if img_archive is not None:
            msg_archived = await delay_send(client.send_file, client.get_channel(img_archive), att_path)
            att, _ = get_attachment(msg_archived)

        embed = Embed(
            description="**Attachment sent by {0} deleted in <#{1}>**\n{2}".format(
                message.author.mention, message.channel.id, att['proxy_url']
            ),
            color=0xFF470F,
        )
        embed.set_author(
            name=str(message.author),
            icon_url=message.author.avatar_url
        )
        embed.set_footer(
            text="ID: {0} | {1}".format(message.author.id, timezone.now().strftime("%a, %d %b %Y %I:%M %p")),
        )

        await delay_send(client.send_message, client.get_channel(server.log_channel), embed=embed)


@client.event
async def on_ready():
    log('Logged in as', client.user.name, client.user.id)
    await client.change_presence(game=discord.Game(name='lambdabot.morchkovalski.com'))

start_murphy(client)
client.run(AccessToken.objects.get(name="discord").token)
