import os
import asyncio
import traceback
import uuid
import discord
import requests

from discord import Member
from django.utils import timezone
from tempfile import mkdtemp

from discordbot.models import DiscordServer, DiscordServerUser


headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Cafari/537.36'
}


class DelayedTask:
    def __init__(self, delay, callback, args=(), kwargs=None):
        self._delay = delay
        self._callback = callback
        self._args = args
        self._kwargs = kwargs if kwargs is not None else {}
        self._task = None

    def run(self):
        self._task = asyncio.ensure_future(self._job())

    async def _job(self):
        await asyncio.sleep(self._delay)
        await self._callback(*self._args, **self._kwargs)

    def cancel(self):
        if self._task is not None:
            self._task.cancel()


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


async def delay_send(func, *args, **kwargs):
    try:
        await func(*args, **kwargs)
    except discord.Forbidden:
        # if func != client.send_typing:
        #     log("channel forbidden")
        pass
    except Exception as e:
        log_exc(e)


def get_server_and_member(message):
    server_id = message.server.id
    server = DiscordServer.get_by_id(server_id)
    if server is not None:
        server.update(name=message.server.name)

    member = DiscordServerUser.get_by_id(message.author.id, server)
    if member is not None:
        member.update(nickname=(message.author.nick if message.author is Member else message.author.name))
        member.user.update(name=message.author.name)

    return server, member


def get_attachment(message):
    att = None
    dl_embed_url = None

    if len(message.attachments) > 0:
        att = message.attachments[0]

    elif len(message.embeds) > 0:
        emb = message.embeds[0]
        url = emb.get('url')
        if url is not None:
            att = emb.get('image')
            if att is None:
                att = emb.get('thumbnail')
            if att is not None:
                dl_embed_url = emb['url']

    return att, dl_embed_url


def save_attachment(att):
    tmpdir = mkdtemp(prefix="lambdabot_attach_")
    filename = os.path.join(tmpdir, str(uuid.uuid4()))
    log('received attachment: {0} {1}'.format(att['url'], filename))
    # noinspection PyShadowingNames
    try:
        attachment = requests.get(att['proxy_url'], headers=headers)
        with open(filename, 'wb') as attachment_file:
            attachment_file.write(attachment.content)
        return filename
    except Exception as exc:
        log_exc(exc)
        return None
