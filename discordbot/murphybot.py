# this module is one big hack, don't read too deep into it

import os
import asyncio
import textwrap
import discord
import datetime

from tempfile import mkdtemp
from django.utils import timezone
from telethon import TelegramClient
from telethon.tl.types import UpdateShortMessage
from discordbot.cleverbot import cb_talk
from discordbot.models import MurphyRequest, MurphyFacePic
from discordbot.permissions import PERM_CLEVERBOT
from discordbot.util import log, discord_send, log_exc
from lamdabotweb.settings import MURPHYBOT_TIMEOUT, TELEGRAM_API_ID, TELEGRAM_API_HASH

MURPHYBOT_HANDLE = "@ProjectMurphy_bot"

murphybot = TelegramClient('murphy', TELEGRAM_API_ID, TELEGRAM_API_HASH)
murphybot_state = "0"
murphybot_prevstate = "0"
murphybot_request = None
murphybot_media = None
murphybot_error = True
channel_facepic = ''
murphybot_last_update = timezone.now()


def log_murphy(*args):
    log(*args, tag="murphy")


def start_murphy(client):
    global murphybot_error
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
        client.loop.create_task(process_murphy(client))


def is_murphy_active():
    return not murphybot_error


async def process_murphy(client):
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
            try:
                await discord_send(client.send_typing, channel)
            except discord.Forbidden:
                log("can't send message to channel")

        if murphybot_state == "0":
            await asyncio.sleep(1)
            murphybot_request = MurphyRequest.get_next_unprocessed(minutes=5)

            if murphybot_request is None:
                continue

            log_murphy("processing request: {}".format(murphybot_request))

            channel_facepic = MurphyFacePic.get(murphybot_request.channel_id)

            if murphybot_request.question == '' and murphybot_request.face_pic != '' and \
                    os.path.isfile(murphybot_request.face_pic):
                log_murphy("sending face pic")
                try:
                    murphybot.send_file(MURPHYBOT_HANDLE, murphybot_request.face_pic)
                    murphybot_state = "1"
                except Exception as ex:
                    log_exc(ex)
                    murphybot_state = "error"
                continue

            elif murphybot_request.question.lower().startswith("what if i "):

                if murphybot_request.face_pic == '':

                    if channel_facepic == '':
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
                        continue
                    except Exception as ex:
                        log_exc(ex)

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
            if timezone.now() - datetime.timedelta(seconds=MURPHYBOT_TIMEOUT) > murphybot_last_update:
                log_murphy("state {} timeout".format(murphybot_state))
                murphybot_state = "no face"
            continue

        elif murphybot_state == "2":
            await asyncio.sleep(1)
            if timezone.now() - datetime.timedelta(seconds=MURPHYBOT_TIMEOUT) > murphybot_last_update:
                log_murphy("state 2 timeout")
                murphybot_state = "idk"
            continue

        elif murphybot_state == "1.2":
            log_murphy("face accepted")
            MurphyFacePic.set(murphybot_request.channel_id, murphybot_request.face_pic)
            if murphybot_request.question == '':
                await discord_send(client.send_message, channel, "{} face accepted :+1:".format(mention))
            else:
                murphybot_state = "2.2"
                continue

        elif murphybot_state == "2.2":
            log_murphy("sending answer")
            tmpdir = mkdtemp(prefix="lambdabot_murphy_")
            output = murphybot.download_media(murphybot_media, file=tmpdir)
            await discord_send(client.send_file, channel, output, content=mention)

        elif murphybot_state == "3.2":
            log_murphy("face accepted, sending question")
            MurphyFacePic.set(murphybot_request.channel_id, murphybot_request.face_pic)
            murphybot.send_message(MURPHYBOT_HANDLE, murphybot_request.question)
            murphybot_state = "2"
            continue

        elif murphybot_state == "upload face":
            log_murphy("no channel face pic")
            await discord_send(client.send_message, channel, "{} please upload a face first".format(mention))

        elif murphybot_state == "no face":
            log_murphy("no face detected")
            await discord_send(client.send_message, channel, "{} no face detected :cry:".format(mention))

        elif murphybot_state == "idk":
            log_murphy("idk")
            if murphybot_request.server_user.check_permission(PERM_CLEVERBOT):
                await cb_talk(client, channel, murphybot_request.server_user, murphybot_request.question, nodelay=True)
            else:
                await discord_send(client.send_message, channel, "{0}\n```{1}```\n:thinking:".format(mention, murphybot_request.question))

        elif murphybot_state == "error":
            log_murphy("error")
            await discord_send(client.send_message, channel, "{} error :cry:".format(mention))

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
