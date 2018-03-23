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


def log_exc(exc):
    log("--- ERROR ---")
    print(exc)
    print(traceback.format_exc())


async def discord_send(func, *args, **kwargs):
    try:
        return await func(*args, **kwargs)
    except discord.Forbidden:
        # if func != client.send_typing:
        #     log("channel forbidden")
        pass
    except Exception as e:
        log_exc(e)


def get_server(message):
    server_id = message.server.id
    server = DiscordServer.get_by_id(server_id)
    if server is not None:
        server.update(name=message.server.name)
    return server


def get_member(message, server):
    member = DiscordServerUser.get_by_id(message.author.id, server)
    if member is not None:
        member.update(nickname=(message.author.nick if message.author is Member else message.author.name))
        member.user.update(name=message.author.name)
    return member


def get_attachments(message, get_embeds=True):
    atts = []

    for att in message.attachments:
        att['is_embed'] = False
        att['real_url'] = att['proxy_url']
        atts.append(att)

    if not get_embeds:
        return atts

    for emb in message.embeds:
        url = emb.get('url')
        if url is not None:
            att = emb.get('image')
            if att is None:
                att = emb.get('thumbnail')
            if att is not None:
                att['is_embed'] = True
                att['real_url'] = emb['url']
                atts.append(att)

    return atts


def save_attachment(url, filename=None):
    if filename is None:
        filename = str(uuid.uuid4())
    tmpdir = mkdtemp(prefix="lambdabot_attach_")
    filename = os.path.join(tmpdir, filename)
    log('received attachment: {0} -> {1}'.format(url, filename))
    try:
        attachment = requests.get(url, headers=headers)
        with open(filename, 'wb') as attachment_file:
            attachment_file.write(attachment.content)
        return filename
    except Exception as exc:
        log_exc(exc)
        return None


def get_timeout_str(message, limit, timeout, left):
    if left >= 3 * 60:
        timestr = "{0} more minutes".format(int(left / 60) + 1)
    else:
        timestr = "{0} more seconds".format(left)
    return message.format(limit, timeout, timestr)
