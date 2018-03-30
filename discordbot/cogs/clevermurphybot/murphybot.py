# this module is one big hack, don't read too deep into it

import os
import asyncio
import textwrap
import discord
import datetime
import discordbot.util
import config

from collections import deque
from tempfile import mkdtemp
from django.utils import timezone
from telethon import TelegramClient, events
from discordbot.cogs.clevermurphybot import cleverbot

_MURPHYBOT_HANDLE = "@ProjectMurphy_bot"
_MURPHYBOT_IGNORE_MSG = (
    "You asked:",
    "Here's an idea",
    "Trying another photo",
    "Wait, I'm still learning",
    "Attachment received",
    "POST to MorphiBot"
)


_murphybot = None
_state = "0"
_prevstate = "0"
_request = None
_media = None
_last_update = timezone.now()
_channel_facepic = None
_facepics = {}
_request_queue = deque()


def _log(*args):
    discordbot.util.log(*args, tag="murphy")


def is_active():
    return _murphybot is not None


class _MurphyRequest:
    def __init__(self, msg: discord.Message, question=None, face_pic=None):
        self.msg = msg
        self.mention = msg.author.mention
        self.channel = msg.channel
        self.question = question
        self.face_pic = face_pic


def ask(msg: discord.Message, question=None, face_pic=None):
    _request_queue.append(_MurphyRequest(msg, question, face_pic))


def start(client):
    global _murphybot

    if not config.TELEGRAM_API_ID:
        return

    _murphybot = TelegramClient('murphy', config.TELEGRAM_API_ID, config.TELEGRAM_API_HASH, update_workers=1)
    # noinspection PyBroadException
    try:
        _murphybot.start()
    except Exception:
        _log("authentication failed")
        _murphybot = None
        return

    @_murphybot.on(events.NewMessage(chats="ProjectMurphy_bot", incoming=True))
    def murphybot_handler(event):
        global _state, _last_update, _media

        _last_update = timezone.now()

        if event.photo is None:
            _log("received message: {}".format(textwrap.shorten(event.raw_text, width=128)))

            if event.raw_text.startswith(_MURPHYBOT_IGNORE_MSG):
                return

            if _state in ["1", "3"]:
                if event.raw_text.startswith("Thanks, I will keep this photo"):
                    _state = "{}.2".format(_state)
                else:
                    _state = "no face"

            elif _state == "2":
                if event.raw_text.startswith("Please upload a photo"):
                    _state = "reupload face"
                else:
                    _state = "idk"

        else:
            _log("received media")

            if _state == "1":
                _media = event.photo
                _state = "1.2"

            elif _state == "2":
                _media = event.photo
                _state = "2.2"

            elif _state == "3":
                _state = "3.2"

    client.loop.create_task(_murphy_task())


async def _murphy_task():
    global _state, _request, _last_update, _prevstate,\
        _channel_facepic

    while True:

        if _state != _prevstate:
            _log("[ state {0} -> {1} ]".format(_prevstate, _state))
            _last_update = timezone.now()
            _prevstate = _state

        if _state != "0":
            try:
                async with _request.channel.typing():
                    if not await _process_request():
                        continue
            except discord.Forbidden:
                pass

        _state = "0"
        await _wait_for_request()


async def _wait_for_request():
    global _state, _request, _last_update, _prevstate, \
        _channel_facepic

    await asyncio.sleep(1)

    if len(_request_queue) == 0:
        return

    _request = _request_queue.popleft()
    _channel_facepic = _facepics.get(_request.channel.id)

    _log("processing request: {}".format(_request))

    if not _request.question and _request.face_pic and os.path.isfile(_request.face_pic):
        _log("sending face pic")
        try:
            _murphybot.send_file(_MURPHYBOT_HANDLE, _request.face_pic)
            _state = "1"
        except Exception as ex:
            discordbot.util.log_exc(ex)
            _state = "error"
        return

    elif _request.question.lower().startswith("what if i "):

        if not _request.face_pic:

            if not _channel_facepic:
                _log("ERROR: channel face pic null")

            elif _channel_facepic == _facepics.get('current'):
                _log("channel face pic = current face pic, sending question")
                _murphybot.send_message(_MURPHYBOT_HANDLE, _request.question)
                _state = "2"
                return

            else:
                _log("channel face pic =/= current face pic")
                _state = "different channel face"
                return

        elif os.path.isfile(_request.face_pic):
            _log("sending face pic from request")
            try:
                _murphybot.send_file(_MURPHYBOT_HANDLE, _request.face_pic)
                _state = "3"
                return
            except Exception as ex:
                discordbot.util.log_exc(ex)

        else:
            _log("ERROR: request face pic file doesn't exist: {}".format(_request.face_pic))

        _state = "upload face"

    else:
        _log("sending question")
        _murphybot.send_message(_MURPHYBOT_HANDLE, _request.question)
        _state = "2"


async def _process_request():
    global _state, _request, _last_update, _prevstate, \
        _channel_facepic

    if _state in ["reupload face", "different channel face"]:

        if _channel_facepic is None or not os.path.isfile(_channel_facepic):
            _log("ERROR: can't read channel face pic: {}".format(_channel_facepic))
            _state = "upload face"

        else:
            _log("reuploading channel face pic")
            try:
                _murphybot.send_file(_MURPHYBOT_HANDLE, _channel_facepic)
                _state = "1" if _state == "reupload face" else "3"
            except Exception as ex:
                discordbot.util.log_exc(ex)
                _state = "error"

        return False

    elif _state in ["1", "3"]:
        await asyncio.sleep(1)
        if timezone.now() - datetime.timedelta(seconds=config.MURPHYBOT_TIMEOUT) > _last_update:
            _log("state {} timeout".format(_state))
            _state = "no face"
        return False

    elif _state == "2":
        await asyncio.sleep(1)
        if timezone.now() - datetime.timedelta(seconds=config.MURPHYBOT_TIMEOUT) > _last_update:
            _log("state 2 timeout")
            _state = "idk"
        return False

    elif _state == "1.2":
        _log("face accepted")
        _facepics[_request.channel.id] = _request.face_pic
        _facepics['current'] = _request.face_pic
        if not _request.question:
            await _request.channel.send("{} face accepted :+1:".format(_request.mention))
        else:
            _state = "2.2"
            return False

    elif _state == "2.2":
        _log("sending answer")
        tmpdir = mkdtemp(prefix="lambdabot_murphy_")
        output = _murphybot.download_media(_media, file=tmpdir)
        await _request.channel.send(_request.mention, file=discord.File(output))

    elif _state == "3.2":
        _log("face accepted, sending question")
        _facepics[_request.channel.id] = _request.face_pic
        _facepics['current'] = _request.face_pic
        _murphybot.send_message(_MURPHYBOT_HANDLE, _request.question)
        _state = "2"
        return False

    elif _state == "upload face":
        _log("no channel face pic")
        await _request.channel.send("{} please upload a face first".format(_request.mention))

    elif _state == "no face":
        _log("no face detected")
        await _request.channel.send("{} no face detected :cry:".format(_request.mention))

    elif _state == "idk":
        _log("idk")
        if cleverbot.is_active():
            await cleverbot.talk(_request.msg, _request.question, nodelay=True)
        else:
            await _request.channel.send("{} :thinking:".format(_request.mention))

    elif _state == "error":
        _log("error")
        await _request.channel.send("{} error :cry:".format(_request.mention))

    return True
