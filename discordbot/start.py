import os
import asyncio
import random
import textwrap
from tempfile import mkdtemp

import django
import discord
import datetime

import shutil
from cleverwrap import CleverWrap
from discord import Member, Status, Server, Game, Channel
from discord.state import ConnectionState
from django.utils import timezone
from telethon import TelegramClient
from telethon.tl.types import UpdateShortMessage


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

@client.event
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

@client.event
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

    print('meme generated:', meme)

CMD_FUN['meem'] = cmd_meem


# ------------------------------------------------

async def delay_message(data):
    await client.send_message(*data)


async def delay_typing(channel):
    await client.send_typing(channel)


@client.event
async def cmd_meme_hl(message, **_):
    DelayedTask(1.4, delay_typing, message.channel).run()
    DelayedTask(1.7, delay_message, (message.channel, "<@238650794679730178> kys")).run()

CMD_FUN['meme'] = cmd_meme_hl


# ------------------------------------------------

CP_MENTION = "<@289816859002273792>"
CP_HELLOS = ['hi', 'hello', 'sup', 'yo', 'waddup', 'wuss poppin b', 'good morning', 'greetings']
CP_BYES = ['ok bye', 'cya', 'see ya', 'bye', 'later', 'gtg bye']

cptalk = None


async def cptalk_say(channel, message, delay):
    DelayedTask(delay, delay_typing, channel).run()
    DelayedTask(delay + min(0.2 * len(message), 4), delay_message, (channel, "{0} {1}".format(CP_MENTION, message))).run()


@client.event
async def cmd_cptalk(message, **_):
    global cptalk
    if cptalk is None:
        cptalk = CleverWrap(AccessToken.objects.get(name="cleverbot").token)
        await cptalk_say(message.channel, random.choice(CP_HELLOS), 0)
    else:
        cptalk = None

CMD_FUN['cptalk'] = cmd_cptalk


# ============================================================================================

from memeviewer.models import Meem, MemeTemplate, AccessToken, sourceimg_count
from discordbot.models import DiscordServer, DiscordCommand, DiscordServerUser, MurphyRequest


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

    if msg == client.user.mention:
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

        if cptalk is not None and message.author.id == "289816859002273792":
            response = cptalk.say(msg)
            await cptalk_say(message.channel, response, 0.5 + min(0.07 * len(msg), 4))
            return

        elif msg.lower().startswith("what if ") and member.check_permission("murphybot"):
            MurphyRequest.ask(question=msg, server_user=member, channel_id=message.channel.id)
            print(datetime.datetime.now(), "{0}, {1}: {2}".format(server.context, message.author.name, msg))
            return

        return

    elif not msg.startswith(server.prefix):
        return
    else:
        splitcmd = msg[len(server.prefix):].split(' ')

    cmd = DiscordCommand.get_cmd(splitcmd[0])

    if cmd is not None and cmd.check_permission(member):
        print(datetime.datetime.now(), "{0}, {1}: {2}{3}".format(
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
    print(datetime.datetime.now(), 'Logged in as', client.user.name, client.user.id)
    await client.change_presence(game=discord.Game(name='lambdabot.morchkovalski.com'))


# ============================================================================================

murphybot_request = None
murphybot_media = None
TELEGRAM_TOKENS = AccessToken.objects.get(name="telegram-murphybot").token.splitlines()
telegram_client = TelegramClient('murphy', int(TELEGRAM_TOKENS[0]), TELEGRAM_TOKENS[1])

async def process_murphy():
    global murphybot_media, murphybot_request
    await client.wait_until_ready()
    while not client.is_closed:
        if murphybot_request is None:
            request = MurphyRequest.objects.filter(
                processed=False,
                ask_date__gte=(timezone.now() - datetime.timedelta(minutes=5))
            ).order_by('ask_date').first()
            if request is not None:
                murphybot_request = request
                print(datetime.datetime.now(), 'sending murphybot request {0}', murphybot_request)
                telegram_client.send_message("@ProjectMurphy_bot", murphybot_request.request)
        elif murphybot_media is not None:
            print(datetime.datetime.now(), 'sending murphybot response')
            tmpdir = mkdtemp()
            output = telegram_client.download_media(murphybot_media, file=tmpdir)
            await client.send_file(client.get_channel(murphybot_request.channel_id), output,
                                   content="<@{0}>".format(murphybot_request.server_user.user.user_id))
            shutil.rmtree(tmpdir)
            murphybot_request.mark_processed()
            murphybot_request = None
            murphybot_media = None
        await asyncio.sleep(1)


def murphybot_handler(update_object):
    global murphybot_media, murphybot_request
    if isinstance(update_object, UpdateShortMessage) and not update_object.out:
        print(datetime.datetime.now(), 'received murphybot message: {0}',
              textwrap.shorten(update_object.message, width=30))
        if not update_object.message.startswith("You asked:"):
            murphybot_request = None
            murphybot_media = None

    if murphybot_request is None or not hasattr(update_object, 'updates') or len(update_object.updates) == 0 or \
            not hasattr(update_object.updates[0], 'message') or not hasattr(update_object.updates[0].message, 'media'):
        return

    print(datetime.datetime.now(), 'received murphybot media')
    murphybot_media = update_object.updates[0].message.media


murphybot_active = False

# noinspection PyBroadException
try:
    telegram_client.connect()
    if telegram_client.is_user_authorized():
        murphybot_active = True

except Exception as e:
    print(e)

if murphybot_active:
    print(datetime.datetime.now(), 'murphybot active')
    telegram_client.add_update_handler(murphybot_handler)
    client.loop.create_task(process_murphy())
else:
    print(datetime.datetime.now(), 'murphybot not active')

# ============================================================================================

client.run(AccessToken.objects.get(name="discord").token)
