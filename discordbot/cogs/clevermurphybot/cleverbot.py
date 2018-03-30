import discord

import asyncio

import config
from cleverwrap import CleverWrap
from json.decoder import JSONDecodeError
from discordbot.util import log


_cb_conversations = {}
_cb_active = bool(config.CLEVERBOT_TOKEN)


def is_active():
    return _cb_active


async def talk(msg: discord.Message, message, nodelay=False):
    global _cb_active
    if not _cb_active:
        return None

    user = msg.author
    channel = msg.channel

    if _cb_conversations.get(user.id) is None:
        log("creating session for {}".format(user), tag="cleverbot")
        _cb_conversations[user.id] = CleverWrap(config.CLEVERBOT_TOKEN)

    response = "error :cry:"
    success = False
    retries = 5
    while not success and retries > 0:
        try:
            response = _cb_conversations[user.id].say(message)
            success = True
        except JSONDecodeError:
            log("error! recreating session for {}".format(user), tag="cleverbot")
            _cb_conversations[user.id] = CleverWrap(config.CLEVERBOT_TOKEN)
            retries -= 1

    if response is None:
        log("cleverbot request failed".format(response), tag="cleverbot")
        return None

    log("response: {}".format(response), tag="cleverbot")
    delay = 0 if nodelay else 0.2 + min(0.04 * len(message), 4)
    if delay > 0:
        await asyncio.sleep(delay)
        async with channel.typing():
            await asyncio.sleep(min(0.17 * len(response), 4))
    await channel.send("{0} {1}".format(user.mention, response))
