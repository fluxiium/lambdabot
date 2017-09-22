import os
import asyncio
import random
import textwrap
import traceback
import uuid
import django
import discord
import datetime
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

client = discord.Client()

CMD_FUN = {}


# ------------------------------------------------

async def cmd_help(server, member, message, **_):
    helpstr = "{0} available commands:".format(message.author.mention)
    for cmd_data in member.get_commands():
        if cmd_data.hidden:
            continue
        helpstr += "\n**{0}{1}**".format(server.prefix, cmd_data.cmd)
        if cmd_data.help:
            helpstr += " - {0}".format(cmd_data.help)
    await client.send_message(message.channel, helpstr)

CMD_FUN['help'] = cmd_help


# ------------------------------------------------

async def cmd_meem(server, member, message, **_):
    from memeviewer.models import Meem
    from memeviewer.preview import preview_meme
    from discordbot.models import DiscordMeem

    await client.send_typing(message.channel)

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

    meme = Meem.generate(context=server.context)
    preview_meme(meme)

    discord_meme = DiscordMeem(meme=meme, server_user=member)
    discord_meme.save()

    await client.send_message(
        message.channel,
        content="{0} here's a meme:\n{1}".format(message.author.mention, meme.get_info_url())
    )

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

CP_MENTION = "<@289816859002273792>"
CP_HELLOS = ['hi', 'hello', 'sup', 'yo', 'waddup', 'wuss poppin b', 'good morning', 'greetings']
CP_BYES = ['ok bye', 'cya', 'see ya', 'bye', 'later', 'gtg bye']

cptalk = None


async def cptalk_say(channel, message, delay):
    DelayedTask(delay, delay_typing, channel).run()
    DelayedTask(delay + min(0.2 * len(message), 4), delay_message, (channel, "{0} {1}".format(CP_MENTION, message))).run()


async def cmd_cptalk(message, **_):
    global cptalk
    if cptalk is None:
        cptalk = CleverWrap(AccessToken.objects.get(name="cleverbot").token)
        await cptalk_say(message.channel, random.choice(CP_HELLOS), 0)
    else:
        cptalk = None

CMD_FUN['cptalk'] = cmd_cptalk


# ------------------------------------------------

murphybot_active = False
murphybot_request = None
murphybot_media = None
murphybot_error = False


async def cmd_murphybot(message, **_):
    global murphybot_active, murphybot_request, murphybot_media
    if murphybot_error:
        return
    murphybot_active = not murphybot_active
    murphybot_request = None
    murphybot_media = None
    if murphybot_active:
        log("activated", tag="murphy")
        await client.send_message(message.channel, "MurphyBot activated")
    else:
        log("deactivated", tag="murphy")
        await client.send_message(message.channel, "MurphyBot deactivated")

CMD_FUN['murphybot'] = cmd_murphybot


# ============================================================================================

from memeviewer.models import Meem, MemeTemplate, AccessToken, sourceimg_count
from discordbot.models import DiscordServer, DiscordCommand, DiscordServerUser, MurphyRequest

tmpdir = mkdtemp(prefix="lambdabot_")


@client.event
async def process_message(message):

    server_id = message.server.id
    server = DiscordServer.get_by_id(server_id)

    if server is None:
        return

    server.update(name=message.server.name)

    member = DiscordServerUser.get_by_id(message.author.id, server)
    member.update(nickname=(message.author.nick if message.author is Member else message.author.name))
    member.user.update(name=message.author.name)

    msg = message.content

    if msg == client.user.mention and len(message.attachments) == 0:
        await client.send_typing(message.channel)
        await client.send_message(
            message.channel,
            "{0} LambdaBot is a bot which generates completely random Half-Life memes. It does this by picking a "
            "random meme template and combining it with one or more randomly picked source images related to "
            "Half-Life. Currently there are **{1:,}** available templates and **{2:,}** available source images, for a "
            "total of **{3:,}** possible combinations.\n"
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

    elif client.user in message.mentions and msg.startswith(client.user.mention):

        msg = msg.replace(client.user.mention, "", 1).strip()
        log("{0}, {1}: {2}".format(server.context, message.author.name, msg))

        if cptalk is not None and message.author.id == "289816859002273792":
            response = cptalk.say(msg)
            await cptalk_say(message.channel, response, 0.5 + min(0.07 * len(msg), 4))
            return

        if len(message.attachments) > 0:
            att = message.attachments[0]
            attachment_filename = os.path.join(tmpdir, "{0}{1}".format(str(uuid.uuid4()), att['filename']))
            log('received attachment: {0} {1}'.format(att['url'], attachment_filename))
            downloaded = False

            # noinspection PyShadowingNames
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Cafari/537.36'}
                attachment = requests.get(att['proxy_url'], headers=headers)
                with open(attachment_filename, 'wb') as attachment_file:
                    attachment_file.write(attachment.content)
                downloaded = True
            except Exception as exc:
                print(exc)
                print(traceback.format_exc())

            if murphybot_active and downloaded:
                MurphyRequest.ask(question="ipic:{0}".format(attachment_filename), server_user=member, channel_id=message.channel.id)

        if msg.lower().startswith("what if ") and member.check_permission("murphybot") and murphybot_active:
            MurphyRequest.ask(question=msg, server_user=member, channel_id=message.channel.id)
            return

        return

    elif not msg.startswith(server.prefix):
        return
    else:
        splitcmd = msg[len(server.prefix):].split(' ')

    cmd = DiscordCommand.get_cmd(splitcmd[0])

    if cmd is not None and cmd.check_permission(member):
        log("{0}, {1}: {2}{3}".format(
            server.context, message.author.name, server.prefix, cmd.cmd
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
            )


@client.event
async def on_message(message):
    await process_message(message)


@client.event
async def on_message_edit(_, message):
    await process_message(message)


@client.event
async def on_ready():
    log('Logged in as', client.user.name, client.user.id)
    await client.change_presence(game=discord.Game(name='lambdabot.morchkovalski.com'))


# ============================================================================================

TELEGRAM_TOKENS = AccessToken.objects.get(name="telegram-murphybot").token.splitlines()
telegram_client = TelegramClient('murphy', int(TELEGRAM_TOKENS[0]), TELEGRAM_TOKENS[1])

async def process_murphy():
    global murphybot_media, murphybot_request, murphybot_active
    await client.wait_until_ready()

    while not client.is_closed:
        if not murphybot_active:
            await asyncio.sleep(4)

        elif murphybot_request is None:
            request = MurphyRequest.get_next(minutes=5)
            if request is not None:
                murphybot_request = request
                murphybot_request.start_process()
                log('sending request: ', murphybot_request, tag="murphy")
                await client.send_typing(client.get_channel(murphybot_request.channel_id))
                if request.is_i_pic_request():
                    telegram_client.send_file("@ProjectMurphy_bot", murphybot_request.request[5:])
                else:
                    telegram_client.send_message("@ProjectMurphy_bot", murphybot_request.request)

        elif murphybot_media is not None:
            await client.send_typing(client.get_channel(murphybot_request.channel_id))
            log('sending response', tag="murphy")
            channel = client.get_channel(murphybot_request.channel_id)
            mention = "<@{0}>".format(murphybot_request.server_user.user.user_id)

            if murphybot_request.is_i_pic_request():
                if not murphybot_media:
                    await client.send_message(channel, "{0} no face detected :cry:".format(mention))
                    log('no face detected in i pic', tag="murphy")
                else:
                    await client.send_message(channel, "{0} face accepted :thumbsup:".format(mention))
                    log('i pic accepted', tag="murphy")
            else:
                if not murphybot_media:
                    await client.send_message(
                        channel,
                        "{0}\n"
                        "```{1}```\n"
                        ":thinking:".format(mention, murphybot_request.request)
                    )
                    log('2edgy4me', tag="murphy")

                else:
                    output = telegram_client.download_media(murphybot_media, file=tmpdir)
                    await client.send_file(channel, output, content=mention)
                    log('answered', tag="murphy")

            murphybot_request.mark_processed()
            murphybot_request = None
            murphybot_media = None

        elif (timezone.now() - datetime.timedelta(seconds=15) > murphybot_request.process_date and murphybot_request.accept_date is None) or \
                (timezone.now() - datetime.timedelta(seconds=40) > murphybot_request.process_date and murphybot_request.accept_date is not None):

            # it's time to stop

            channel = client.get_channel(murphybot_request.channel_id)
            mention = "<@{0}>".format(murphybot_request.server_user.user.user_id)
            await client.send_message(
                channel,
                "{0}\n"
                "```{1}```\n"
                "idk ¯\_(ツ)_/¯".format(mention, murphybot_request.request)
            )
            murphybot_request.mark_processed()
            murphybot_request = None
            murphybot_media = None

            log('idk', tag="murphy")

        await asyncio.sleep(1)


def murphybot_handler(update_object):
    global murphybot_media, murphybot_request

    if not murphybot_active:
        return

    elif isinstance(update_object, UpdateShortMessage) and not update_object.out:

        # received text message

        log('received message: ', textwrap.shorten(update_object.message, width=70), tag="murphy")

        if murphybot_request is not None:
            if murphybot_request.is_i_pic_request():
                if update_object.message.startswith("Thanks, I will keep this photo"):
                    murphybot_media = True
                    murphybot_request.accept()
                elif update_object.message.startswith("Here's an idea"):
                    murphybot_request.accept()
                elif not update_object.message.startswith("Attachment received"):
                    murphybot_media = False
            else:
                if update_object.message.startswith("You asked:") or update_object.message.startswith("Here's an idea") or\
                        update_object.message.startswith("Trying another photo"):
                    murphybot_request.accept()
                elif not update_object.message.startswith("Wait, I'm still learning"):
                    murphybot_media = False
        return

    elif murphybot_request is not None and hasattr(update_object, 'updates') and len(update_object.updates) > 0 and\
            hasattr(update_object.updates[0], 'message') and hasattr(update_object.updates[0].message, 'media'):

        # received media
        log('received media', tag="murphy")
        if murphybot_request.is_i_pic_request():
            murphybot_media = True
        else:
            murphybot_media = update_object.updates[0].message.media


# noinspection PyBroadException
try:
    telegram_client.connect()
    if telegram_client.is_user_authorized():
        murphybot_active = True
    else:
        log("no telegram session file", tag="murphy")
        murphybot_error = True

except Exception as exc:
    print(exc)
    print(traceback.format_exc())
    murphybot_error = True

if murphybot_active:
    log('active', tag="murphy")
    telegram_client.add_update_handler(murphybot_handler)
    client.loop.create_task(process_murphy())
else:
    log('not active', tag="murphy")

# ============================================================================================

client.run(AccessToken.objects.get(name="discord").token)
