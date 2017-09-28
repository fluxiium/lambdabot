import os
import asyncio
import random
import shlex
import textwrap
import traceback
import uuid
import django
import discord
import datetime

import re
import requests

from tempfile import mkdtemp
from cleverwrap import CleverWrap
from discord import Member, Status, Server, Game, Channel
from discord.state import ConnectionState
from django.utils import timezone
from telethon import TelegramClient
from telethon.tl.types import UpdateShortMessage


def log(*args, tag=None):
    if tag is not None:
        tag = "[{}]".format(tag)
    else:
        tag = ""
    print(timezone.now(), tag, *args)


# noinspection PyShadowingNames
def log_exc(exc):
    log("--- ERROR ---")
    print(exc)
    print(traceback.format_exc())


class DelayedTask:
    def __init__(self, delay, callback, data):
        self._delay = delay
        self._callback = callback
        self._data = data
        self._task = None

    def run(self):
        self._task = asyncio.ensure_future(self._job())

    async def _job(self):
        await asyncio.sleep(self._delay)
        await self._callback(self._data)

    def cancel(self):
        if self._task is not None:
            self._task.cancel()


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


# ============================================================================================

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lamdabotweb.settings")
django.setup()

log("")
log("##############################")
log("#  LambdaBot 3883 - Discord  #")
log("##############################")
log("")

client = discord.Client()

CMD_FUN = {}


# ------------------------------------------------

async def cmd_help(server, member, message, **_):
    helpstr = "{0} available commands:".format(message.author.mention)
    for cmd_data in member.get_commands():
        if cmd_data.hidden:
            continue

        helpstr += "\n`{0}{1}".format(server.prefix, cmd_data.cmd)

        if cmd_data.help_params:
            helpstr += " {}`".format(cmd_data.help_params)
        else:
            helpstr += "`"

        if cmd_data.help:
            helpstr += " - {0}".format(cmd_data.help)

    await client.send_message(message.channel, helpstr)

CMD_FUN['help'] = cmd_help


# ------------------------------------------------

from memeviewer.preview import preview_meme
from discordbot.models import DiscordMeem, ProcessedMessage, MurphyFacePic


async def cmd_meem(server, member, message, args, **_):

    await client.send_typing(message.channel)

    template = None
    if len(args) > 1:
        template_name = ' '.join(args[1:]).strip()
        if template_name == '^':
            template = MemeTemplate.find(server.context)
        else:
            template = MemeTemplate.find(template_name)
            if template is None:
                await client.send_message(
                    message.channel,
                    content="{0} template `{1}` not found :cry:".format(message.author.mention, template_name)
                )
                return

    meme_limit_count, meme_limit_time = member.get_meme_limit()
    last_user_memes = member.get_memes(limit=meme_limit_count)
    if last_user_memes.count() >= meme_limit_count:
        meme_delta = datetime.timedelta(minutes=meme_limit_time)
        meme_time = last_user_memes[meme_limit_count - 1].meme.gen_date
        if timezone.now() - meme_delta <= meme_time:
            seconds_left = int(((meme_time + meme_delta) - timezone.now()).total_seconds()) + 1
            if seconds_left >= 3 * 60:
                timestr = "{0} more minutes".format(int(seconds_left / 60) + 1)
            else:
                timestr = "{0} more seconds".format(seconds_left)
            await client.send_message(
                message.channel,
                "{3} you can only generate {0} memes every {1} minutes. Please wait {2}.".format(
                    meme_limit_count,
                    meme_limit_time,
                    timestr,
                    message.author.mention,
                )
            )
            return

    meme = Meem.generate(context=server.context, template=template)
    preview_meme(meme)

    discord_meme = DiscordMeem(meme=meme, server_user=member, channel_id=message.channel.id)
    discord_meme.save()

    await client.send_message(
        message.channel,
        content="{0} here's a meme (using template `{2}`)\n{1}".format(message.author.mention, meme.get_info_url(), meme.template_link.name)
    )

    discord_meme.mark_sent()

    log('meme generated:', meme)

CMD_FUN['meem'] = cmd_meem


# ------------------------------------------------

async def delay_message(data):
    await client.send_message(*data)


async def delay_typing(channel):
    await client.send_typing(channel)


async def cmd_meme_hl(message, **_):
    DelayedTask(1.9, delay_typing, message.channel).run()
    DelayedTask(2.3, delay_message, (message.channel, "<@238650794679730178> kys")).run()

CMD_FUN['meme'] = cmd_meme_hl


# ------------------------------------------------

CP_ID = "289816859002273792"
CP_HELLOS = ['hi', 'hello', 'sup', 'yo', 'waddup', 'wuss poppin b', 'good morning', 'greetings']
CP_BYES = ['ok bye', 'cya', 'see ya', 'bye', 'later', 'gtg bye']

cb_conversations = {}


async def cptalk_say(channel, sender_id, message, delay):
    if delay > 0:
        DelayedTask(delay, delay_typing, channel).run()
        delay += min(0.17 * len(message), 4)
    DelayedTask(delay, delay_message, (channel, "<@{0}> {1}".format(sender_id, message))).run()


async def cmd_cptalk(message, **_):
    global cb_conversations
    if cb_conversations.get(CP_ID) is None:
        cb_conversations[CP_ID] = CleverWrap(AccessToken.objects.get(name="cleverbot").token)
        await cptalk_say(message.channel, CP_ID, random.choice(CP_HELLOS), 0.1)
    else:
        cb_conversations[CP_ID] = None

CMD_FUN['cptalk'] = cmd_cptalk


async def cb_talk(channel, user, message, nodelay=False):
    if cb_conversations.get(user.user.user_id) is None:
        if user.user.user_id == CP_ID:
            return
        log("creating session for {}".format(user), tag="cleverbot")
        cb_conversations[user.user.user_id] = CleverWrap(AccessToken.objects.get(name="cleverbot").token)

    response = cb_conversations[user.user.user_id].say(message)
    log("response: {}".format(response), tag="cleverbot")
    await cptalk_say(channel, user.user.user_id, response, 0 if nodelay else 0.2 + min(0.04 * len(message), 4))


# ============================================================================================

from memeviewer.models import Meem, MemeTemplate, AccessToken, sourceimg_count
from discordbot.models import DiscordServer, DiscordCommand, DiscordServerUser, MurphyRequest

tmpdir = mkdtemp(prefix="lambdabot_")


@client.event
async def process_message(message, old_message=None):
    global cb_conversations

    server_id = message.server.id
    server = DiscordServer.get_by_id(server_id)

    if server is None or ProcessedMessage.was_id_processed(message.id):
        return

    server.update(name=message.server.name)

    member = DiscordServerUser.get_by_id(message.author.id, server)
    member.update(nickname=(message.author.nick if message.author is Member else message.author.name))
    member.user.update(name=message.author.name)

    msg = message.content.strip()

    if client.user in message.mentions:

        if msg.startswith(client.user.mention):
            msg = msg.replace(client.user.mention, "", 1).strip()
        elif msg.endswith(client.user.mention):
            msg = msg.rsplit(client.user.mention, 1)[0].strip()
        else:
            return

        log("{0}, {1}: {2}".format(server.context, message.author.name, msg))
        ProcessedMessage.process_id(message.id)
        downloaded_attachment = None
        dl_embed_url = None

        if re.search("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", msg) is not None:
            await asyncio.sleep(2)

        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Cafari/537.36'}

        if len(message.attachments) > 0:
            att = message.attachments[0]
            attachment_filename = os.path.join(tmpdir, "{0}{1}".format(str(uuid.uuid4()), att['filename']))
            log('received attachment: {0} {1}'.format(att['url'], attachment_filename))

            # noinspection PyShadowingNames
            try:
                attachment = requests.get(att['proxy_url'], headers=headers)
                with open(attachment_filename, 'wb') as attachment_file:
                    attachment_file.write(attachment.content)
                downloaded_attachment = attachment_filename
            except Exception as exc:
                log_exc(exc)

        elif len(message.embeds) > 0:
            emb = message.embeds[0]
            att = emb.get('image')
            if att is None:
                att = emb.get('thumbnail')

            if att is not None:
                attachment_filename = os.path.join(tmpdir, str(uuid.uuid4()))
                log('received embed: {0} {1}'.format(att['url'], attachment_filename))

                # noinspection PyShadowingNames
                try:
                    attachment = requests.get(att['proxy_url'], headers=headers)
                    with open(attachment_filename, 'wb') as attachment_file:
                        attachment_file.write(attachment.content)
                    downloaded_attachment = attachment_filename
                    dl_embed_url = emb['url']
                except Exception as exc:
                    log_exc(exc)

        elif msg == "":
            await client.send_typing(message.channel)
            await client.send_message(
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
                    sourceimg_count(server.context),
                    Meem.possible_combinations(server.context)
                )
            )
            return

        answered = False

        if member.check_permission("murphybot"):
            answered = True

            if dl_embed_url is not None:
                msg = msg.replace(dl_embed_url, "", 1).strip()

            if msg.lower().startswith("what if i ") or (msg == "" and downloaded_attachment is not None):
                if msg == "" and downloaded_attachment is not None:
                    MurphyRequest.ask(question=None, server_user=member, channel_id=message.channel.id, face_pic=downloaded_attachment)
                elif msg != "":
                    MurphyRequest.ask(question=msg, server_user=member, channel_id=message.channel.id, face_pic=downloaded_attachment)

            elif msg.lower().startswith("what if "):
                MurphyRequest.ask(question=msg, server_user=member, channel_id=message.channel.id)

            else:
                answered = False

        if not answered and member.check_permission("cleverbot"):
            await cb_talk(message.channel, member, msg)

        return

    elif not msg.startswith(server.prefix):
        return

    else:
        splitcmd = shlex.split(msg[len(server.prefix):])

    cmd = DiscordCommand.get_cmd(splitcmd[0])

    if cmd is not None and cmd.check_permission(member):

        ProcessedMessage.process_id(message.id)

        log("{0}, {1}: {2}".format(
            server.context, message.author.name, msg
        ))

        if cmd.message is not None and len(cmd.message) > 0:
            await client.send_typing(message.channel)
            await client.send_message(message.channel, cmd.message)

        cmd_fun = CMD_FUN.get(cmd.cmd)
        if cmd_fun is not None:
            await cmd_fun(
                server=server,
                member=member,
                message=message,
                args=splitcmd,
            )


@client.event
async def on_message(message):
    await process_message(message)


@client.event
async def on_message_edit(old_message, message):
    await process_message(message, old_message)


@client.event
async def on_ready():
    log('Logged in as', client.user.name, client.user.id)
    await client.change_presence(game=discord.Game(name='lambdabot.morchkovalski.com'))


# ============================================================================================

MURPHYBOT_HANDLE = "@ProjectMurphy_bot"
TELEGRAM_TOKENS = AccessToken.objects.get(name="telegram-murphybot").token.splitlines()
murphybot = TelegramClient('murphy', int(TELEGRAM_TOKENS[0]), TELEGRAM_TOKENS[1])
murphybot_state = "0"
murphybot_prevstate = "0"
murphybot_request = None
murphybot_media = None
channel_facepic = None
murphybot_last_update = timezone.now()


def log_murphy(*args):
    log(*args, tag="murphy")


async def process_murphy():
    global murphybot_state, murphybot_request, murphybot_last_update, murphybot_prevstate,\
        channel_facepic
    await client.wait_until_ready()

    while not client.is_closed:

        if murphybot_state != murphybot_prevstate:
            log_murphy("[ state {0} -> {1} ]".format(murphybot_prevstate, murphybot_state))
            murphybot_last_update = timezone.now()
            murphybot_prevstate = murphybot_state

        if murphybot_state != "0":
            channel = client.get_channel(murphybot_request.channel_id)
            mention = "<@{}>".format(murphybot_request.server_user.user.user_id)
            await client.send_typing(channel)

        if murphybot_state == "0":
            await asyncio.sleep(1)
            murphybot_request = MurphyRequest.get_next_unprocessed(minutes=5)

            if murphybot_request is None:
                continue

            log_murphy("processing request: {}".format(murphybot_request))

            channel_facepic = MurphyFacePic.get(murphybot_request.channel_id)

            if murphybot_request.question is None and murphybot_request.face_pic is not None and \
                    os.path.isfile(murphybot_request.face_pic):
                log_murphy("sending face pic")
                try:
                    murphybot.send_file(MURPHYBOT_HANDLE, murphybot_request.face_pic)
                    murphybot_state = "1"
                except Exception as ex:
                    log_exc(ex)
                    murphybot_state = "error"
                continue

            elif murphybot_request.question.startswith("what if i "):

                if murphybot_request.face_pic is None:

                    if channel_facepic is None:
                        log_murphy("ERROR: channel face pic null")

                    elif MurphyFacePic.get_last_used() == channel_facepic:
                        log_murphy("channel face pic = current face pic, sending question")
                        murphybot.send_message(MURPHYBOT_HANDLE, murphybot_request.question)
                        murphybot_state = "2"
                        continue

                    else:
                        log_murphy("channel face pic =/= current face pic")
                        murphybot_state = "different channel face"
                        continue

                elif os.path.isfile(murphybot_request.face_pic):
                    log_murphy("sending face pic from request")
                    try:
                        murphybot.send_file(MURPHYBOT_HANDLE, murphybot_request.face_pic)
                        murphybot_state = "3"
                    except Exception as ex:
                        log_exc(ex)
                        murphybot_state = "error"
                    continue

                else:
                    log_murphy("ERROR: request face pic file doesn't exist: {}".format(murphybot_request.face_pic))

                murphybot_state = "upload face"
                continue

            else:
                log_murphy("sending question")
                murphybot.send_message(MURPHYBOT_HANDLE, murphybot_request.question)
                murphybot_state = "2"
                continue

        elif murphybot_state in ["reupload face", "different channel face"]:

            if channel_facepic is None or not os.path.isfile(channel_facepic):
                log_murphy("ERROR: can't read channel face pic: {}".format(channel_facepic))
                murphybot_state = "upload face"
                continue

            else:
                log_murphy("reuploading channel face pic")
                try:
                    murphybot.send_file(MURPHYBOT_HANDLE, channel_facepic)
                    murphybot_state = "1" if murphybot_state == "reupload face" else "3"
                except Exception as ex:
                    log_exc(ex)
                    murphybot_state = "error"
                continue

        elif murphybot_state in ["1", "3"]:
            await asyncio.sleep(1)
            if timezone.now() - datetime.timedelta(seconds=15) > murphybot_last_update:
                log_murphy("state {} timeout".format(murphybot_state))
                murphybot_state = "no face"
            continue

        elif murphybot_state == "2":
            await asyncio.sleep(1)
            if timezone.now() - datetime.timedelta(seconds=15) > murphybot_last_update:
                log_murphy("state 2 timeout")
                murphybot_state = "idk"
            continue

        elif murphybot_state == "1.2":
            log_murphy("face accepted")
            MurphyFacePic.set(murphybot_request.channel_id, murphybot_request.face_pic)
            if murphybot_request.question is None:
                await client.send_message(channel, "{} face accepted :+1:".format(mention))
            else:
                murphybot_state = "2.2"
                continue

        elif murphybot_state == "2.2":
            log_murphy("sending answer")
            output = murphybot.download_media(murphybot_media, file=tmpdir)
            await client.send_file(channel, output, content=mention)

        elif murphybot_state == "3.2":
            log_murphy("face accepted, sending question")
            MurphyFacePic.set(murphybot_request.channel_id, murphybot_request.face_pic)
            murphybot.send_message(MURPHYBOT_HANDLE, murphybot_request.question)
            murphybot_state = "2"
            continue

        elif murphybot_state == "upload face":
            log_murphy("no channel face pic")
            await client.send_message(channel, "{} please upload a face first".format(mention))

        elif murphybot_state == "no face":
            log_murphy("no face detected")
            await client.send_message(channel, "{} no face detected :cry:".format(mention))

        elif murphybot_state == "idk":
            log_murphy("idk")
            if murphybot_request.server_user.check_permission("cleverbot"):
                await cb_talk(channel, murphybot_request.server_user, murphybot_request.question, nodelay=True)
            else:
                await client.send_message(channel, "{0}\n```{1}```\n:thinking:".format(mention, murphybot_request.question))

        elif murphybot_state == "error":
            log_murphy("error")
            await client.send_message(channel, "{} error :cry:".format(mention))

        murphybot_request.mark_processed()
        murphybot_state = "0"


def is_murphy_message(update_object):
    return isinstance(update_object, UpdateShortMessage) and not update_object.out


def is_murphy_media(update_object):
    return hasattr(update_object, 'updates') and len(update_object.updates) > 0 and \
           hasattr(update_object.updates[0], 'message') and hasattr(update_object.updates[0].message, 'media')

MURPHYBOT_IGNORE_MSG = (
    "You asked:",
    "Here's an idea",
    "Trying another photo",
    "Wait, I'm still learning",
    "Attachment received",
    "POST to MorphiBot"
)


def murphybot_handler(msg):
    global murphybot_state, murphybot_request, murphybot_last_update, murphybot_media

    if is_murphy_message(msg) or is_murphy_media(msg):
        murphybot_last_update = timezone.now()
    else:
        return

    if is_murphy_message(msg):
        log_murphy("received message: {}".format(textwrap.shorten(msg.message, width=128)))

        if msg.message.startswith(MURPHYBOT_IGNORE_MSG):
            return

        if murphybot_state in ["1", "3"]:
            if msg.message.startswith("Thanks, I will keep this photo"):
                murphybot_state = "{}.2".format(murphybot_state)
            else:
                murphybot_state = "no face"

        elif murphybot_state == "2":
            if msg.message.startswith("Please upload a photo"):
                murphybot_state = "reupload face"
            else:
                murphybot_state = "idk"

    else:
        log_murphy("received media")

        if murphybot_state == "1":
            murphybot_media = msg.updates[0].message.media
            murphybot_state = "1.2"

        elif murphybot_state == "2":
            murphybot_media = msg.updates[0].message.media
            murphybot_state = "2.2"

        elif murphybot_state == "3":
            murphybot_state = "3.2"


murphybot_error = False
# noinspection PyBroadException
try:
    murphybot.connect()
    if not murphybot.is_user_authorized():
        log_murphy("no telegram session file")
        murphybot_error = True

except Exception as exc:
    log_exc(exc)
    murphybot_error = True

if not murphybot_error:
    log_murphy('active')
    murphybot.add_update_handler(murphybot_handler)
    client.loop.create_task(process_murphy())

# ============================================================================================

client.run(AccessToken.objects.get(name="discord").token)
