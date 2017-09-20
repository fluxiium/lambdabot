import os
import asyncio
import random
import django
import discord
import datetime

from cleverwrap import CleverWrap
from discord import Status, Server, Game, Channel
from django.utils import timezone


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


# noinspection PyUnresolvedReferences
Server._sync = _sync_patched


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
from discordbot.models import DiscordServer, DiscordCommand, DiscordServerUser


@client.event
async def process_message(message):

    server_id = message.server.id
    server = DiscordServer.get_by_id(server_id)

    if server is None:
        return

    server.update(name=message.server.name)

    member = DiscordServerUser.get_by_id(message.author.id, server)
    member.update(nickname=(message.author.nick if message.author.nick is not None else message.author.name))
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

    elif cptalk is not None and client.user in message.mentions and message.author.id == "289816859002273792":
        cpmessage = msg.replace(client.user.mention, "")
        response = cptalk.say(cpmessage)
        await cptalk_say(message.channel, response, 0.5 + min(0.07 * len(cpmessage), 4))
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


client.run(AccessToken.objects.get(name="discord").token)
