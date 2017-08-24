import datetime
import os
import django
import discord

from lamdabotweb.settings import MEMES_DIR, DATA_DIR

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lamdabotweb.settings")
django.setup()

from memeviewer.models import Meem, DiscordMeem
from memeviewer.preview import preview_meme

PREFIX = '!'
SERVER_WHITELIST = {
    '154305477323390976': 'hldiscord',
    '257494913623523329': 'arschschmerz',
    '291537367452614658': 'testserver',
    '257193139561824256': 'abs',
}

MEEM_LIMIT_COUNT = 3
MEEM_LIMIT_TIME = 10  # minutes

client = discord.Client()


# noinspection PyCompatibility
@client.event
async def cmd_help(message):
    helpstr = "{0} available commands:".format(message.author.mention)
    for cmd, cmd_data in COMMANDS.items():
        server_whitelist = cmd_data.get('servers')
        if server_whitelist is not None and message.server.id not in server_whitelist:
            continue
        helpstr += "\n**{0}{1}**".format(PREFIX, cmd)
        if cmd_data.get('help'):
            helpstr += " - {0}".format(cmd_data['help'])
    await client.send_message(message.channel, helpstr)


# noinspection PyCompatibility
@client.event
async def cmd_hypersad(message):
    await client.send_message(message.channel,
                              ':cry: https://soundcloud.com/morchkovalski/triage-at-dawn-bass-boosted/s-22Aa2')


# noinspection PyCompatibility
@client.event
async def cmd_choo(message):
    await client.send_message(message.channel,
                              'https://soundcloud.com/breadcrab/whydididothis/s-6dZ0y')


# noinspection PyCompatibility
@client.event
async def cmd_meem(message):
    await client.send_typing(message.channel)

    meme_time_id = "{0}{1}".format(message.author.id, message.server.id)
    if meme_times.get(meme_time_id) is not None:
        if len(meme_times[meme_time_id]) == MEEM_LIMIT_COUNT:
            meme_delta = datetime.timedelta(minutes=MEEM_LIMIT_TIME)
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
                        MEEM_LIMIT_COUNT,
                        MEEM_LIMIT_TIME,
                        timestr,
                        message.author.mention,
                    )
                )
                return
        meme_times[meme_time_id].append(datetime.datetime.now())
    else:
        meme_times[meme_time_id] = [datetime.datetime.now()]

    meme = Meem.generate(context=SERVER_WHITELIST.get(message.server.id, 'default'))
    preview_meme(meme)

    discord_meme = DiscordMeem(meme=meme, server=message.server.id)
    discord_meme.save()

    await client.send_file(
        message.channel,
        meme.get_local_path(),
        content="{0} here's a meme:\n<{1}>".format(
            message.author.mention, meme.get_info_url())
    )

    print('meme generated:', message.author.name, meme)


meme_times = {}

COMMANDS = {
    'help': {
        'fun': cmd_help,
        'help': 'show this text'
    },
    'meem': {
        'fun': cmd_meem,
        'help': 'generate a random meme'
    },
    'hypersad': {
        'fun': cmd_hypersad,
        'servers': [
            '154305477323390976'  # hldiscord
        ]
    },
    'choo': {
        'fun': cmd_choo
    }
}


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


# noinspection PyCompatibility
@client.event
async def on_message(message):
    server_id = message.server.id

    if server_id not in list(SERVER_WHITELIST):
        return

    msg = message.content

    if not msg.startswith(PREFIX):
        return

    splitcmd = msg[len(PREFIX):].split(' ')
    cmd_data = COMMANDS.get(splitcmd[0])
    server_whitelist = cmd_data.get('servers')

    if cmd_data and (server_whitelist is None or server_id in server_whitelist):
        await COMMANDS[splitcmd[0]]['fun'](message)


# noinspection PyCompatibility
@client.event
async def on_ready():
    await client.change_presence(game=discord.Game(name='lambdabot.morchkovalski.com'))


token_file = open(os.path.join(DATA_DIR, 'discordtoken.txt'), 'r')
TOKEN = token_file.read()
token_file.close()
client.run(TOKEN)
