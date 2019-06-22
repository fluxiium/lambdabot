import aiohttp
import discord
import json
import lamdabotweb.settings as config
import logging


def is_active():
    return True


sessions = {}


async def talk(msg: discord.Message, msg_text):
    body = {
        'user': config.CLEVERBOT_USER,
        'key': config.CLEVERBOT_KEY,
        'nick': str(msg.author.id),
    }

    if not sessions.get(msg.author):
        async with msg.channel.typing(), aiohttp.ClientSession() as http_ses:
            await http_ses.post('https://cleverbot.io/1.0/create', json=body)
        sessions[msg.author] = True

    body['text'] = msg_text

    response = ''
    attempt = 0
    while not response and attempt < 50:
        attempt += 1
        async with msg.channel.typing(), aiohttp.ClientSession() as http_ses:
            async with http_ses.post('https://cleverbot.io/1.0/ask', json=body) as r:
                r = json.loads(await r.text())
        if r['status'] == 'success':
            response = r['response']
        else:
            response = 'error :cry:'

    if msg.guild:
        await msg.channel.send(f"{msg.author.mention} {response}")
    else:
        await msg.channel.send(response)

    logging.info(f"cleverbot to {msg.author}: {response}")
