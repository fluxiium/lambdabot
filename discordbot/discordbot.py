import datetime

import discord

from lambdabot.preview import preview_meme
from lambdabot.db import make_meme, meme_info
from lambdabot.settings import *

LIMIT_COUNT = 3
LIMIT_TIME = 30  # minutes

SERVER_CONTEXTS = {
    '154305477323390976': 'hldiscord',
    '257494913623523329': 'arschschmerz',
    '291537367452614658': 'testserver',
}

token_file = open(os.path.join(DATA_DIR, 'discordtoken.txt'), 'r')
TOKEN = token_file.read()
token_file.close()

client = discord.Client()
meme_times = {}


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


# noinspection PyCompatibility
@client.event
async def on_message(message):
    if message.content == '!help' or client.user in message.mentions:
        await client.send_message(message.channel, 'available commands:\n'
                                                   '`!meme` - generate a random meme\n'
                                                   '`!help` - show this text')

    elif message.content.startswith('!meme'):
        await client.send_typing(message.channel)

        if meme_times.get(message.author.id) is not None:
            if len(meme_times[message.author.id]) == LIMIT_COUNT:
                meme_delta = datetime.timedelta(minutes=LIMIT_TIME)
                meme_time = meme_times[message.author.id][0]
                if datetime.datetime.now() - meme_delta > meme_time:
                    meme_times[message.author.id].pop(0)
                else:
                    await client.send_message(
                        message.channel,
                        "You can only generate {0} memes every {1} minutes. Please wait {2} more minutes.".format(
                            LIMIT_COUNT,
                            LIMIT_TIME,
                            int(((meme_time + meme_delta) - datetime.datetime.now()).total_seconds() / 60)
                        )
                    )
                    return
            meme_times[message.author.id].append(datetime.datetime.now())
        else:
            meme_times[message.author.id] = [datetime.datetime.now()]

        meme_id = make_meme(context=SERVER_CONTEXTS.get(message.server.id, 'default'))
        minfo = meme_info(meme_id)
        preview_meme(meme_id)

        await client.send_file(
            message.channel,
            os.path.join(DATA_DIR, 'previews', meme_id + '.jpg'),
            content="{0} here's a meme:\nhttps://lambdabot.morchkovalski.com/meme_info/{1}".format(
                message.author.mention, meme_id)
        )

        print('meme generated:', message.author.name, meme_id, minfo)


client.run(TOKEN)
