import discord
import requests
import json
import config
from util import log


def is_active():
    return True


_sessions = {}


async def talk(msg: discord.Message, msg_text):
    if not is_active():
        return

    body = {
        'user': config.CLEVERBOT_USER,
        'key': config.CLEVERBOT_KEY,
        'nick': str(msg.author.id),
    }

    if not _sessions.get(msg.author):
        async with msg.channel.typing():
            requests.post('https://cleverbot.io/1.0/create', json=body)
        _sessions[msg.author] = True

    body['text'] = msg_text

    response = ''
    attempt = 0
    while not response and attempt < 50:
        attempt += 1
        async with msg.channel.typing():
            r = requests.post('https://cleverbot.io/1.0/ask', json=body)
            r = json.loads(r.text)
        if r['status'] == 'success':
            response = r['response']
        else:
            response = 'error :cry:'

    log("response to {}: {}".format(msg.author, response), tag="cleverbot")

    if msg.guild:
        await msg.channel.send("{0} {1}".format(msg.author.mention, response))
    else:
        await msg.channel.send(response)
