import datetime

import discord

from lambdabot.preview import preview_meme
from lambdabot.db import make_meme, meme_info
from lambdabot.settings import *

LIMIT_COUNT = 3
LIMIT_TIME = 10  # minutes

SERVER_WHITELIST = {
    '154305477323390976': 'hldiscord',
    '257494913623523329': 'arschschmerz',
    '291537367452614658': 'testserver',
    '257193139561824256': 'abs',
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

    if message.server.id not in list(SERVER_WHITELIST):
        return

    if message.content == '!help' or client.user in message.mentions:
        await client.send_message(message.channel, '{0} available commands:\n'
                                                   '`!meem` - generate a random meme\n'
                                                   '`!hypersad`\n'
                                                   '`!help` - show this text'.format(message.author.mention))

    elif message.content == '!hypersad':
        await client.send_message(message.channel,
                                  ':cry: https://soundcloud.com/morchkovalski/triage-at-dawn-bass-boosted/s-22Aa2')

    elif message.content in ['!meem', '!goodmeme', '!goodmeem']:

        await client.send_typing(message.channel)

        meme_time_id = "{0}{1}".format(message.author.id, message.server.id)
        if meme_times.get(meme_time_id) is not None:
            if len(meme_times[meme_time_id]) == LIMIT_COUNT:
                meme_delta = datetime.timedelta(minutes=LIMIT_TIME)
                meme_time = meme_times[meme_time_id][0]
                if datetime.datetime.now() - meme_delta > meme_time:
                    meme_times[meme_time_id].pop(0)
                else:
                    seconds_left = int(((meme_time + meme_delta) - datetime.datetime.now()).total_seconds()) + 1
                    if seconds_left >= 3 * 60:
                        timestr = "{0} more minutes".format(int(seconds_left / 60) + 1)
                    else:
                        timestr = "{0} more seconds".format(seconds_left)
                    await client.send_message(
                        message.channel,
                        "{3} you can only generate {0} memes every {1} minutes. Please wait {2}.".format(
                            LIMIT_COUNT,
                            LIMIT_TIME,
                            timestr,
                            message.author.mention,
                        )
                    )
                    return
            meme_times[meme_time_id].append(datetime.datetime.now())
        else:
            meme_times[meme_time_id] = [datetime.datetime.now()]

        meme_id = make_meme(context=SERVER_WHITELIST.get(message.server.id, 'default'))
        minfo = meme_info(meme_id)
        preview_meme(meme_id)

        await client.send_file(
            message.channel,
            os.path.join(DATA_DIR, 'previews', meme_id + '.jpg'),
            content="{0} here's a meme:\n<https://lambdabot.morchkovalski.com/meme_info/{1}>".format(
                message.author.mention, meme_id)
        )

        print('meme generated:', message.author.name, meme_id, minfo)


# noinspection PyCompatibility
@client.event
async def on_ready():
    await client.change_presence(game=discord.Game(name='lambdabot.morchkovalski.com'))


client.run(TOKEN)
