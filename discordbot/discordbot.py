import datetime
import os
from collections import OrderedDict

import django
import discord

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lamdabotweb.settings")
django.setup()

from memeviewer.models import Meem, DiscordMeem, AccessToken, MemeContext, MemeTemplate, sourceimg_count
from memeviewer.preview import preview_meme

PREFIX = '!'
SERVER_WHITELIST = {
    '154305477323390976': 'hldiscord',
    '257494913623523329': 'arschschmerz',
    '291537367452614658': 'testserver',
    '257193139561824256': 'abs',
}

NO_LIMIT_WHITELIST = [
    '257499042039332866',  # yackson
]

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
async def cmd_about(message):
    context = MemeContext.by_id(SERVER_WHITELIST.get(message.server.id))
    await client.send_message(
        message.channel,
        "{0} LambdaBot is a bot which generates completely random Half-Life memes. It does this by picking a "
        "random meme template and combining it with one or more randomly picked source images related to "
        "Half-Life. Currently there are **{1:,}** available templates and **{2:,}** available source images, for a "
        "total of **{3:,}** possible combinations.\n"
        "\n"
        "Type **!help** to see a list of available commands.\n"
        "\n"
        "*Homepage: https://lambdabot.morchkovalski.com\n"
        "Created by morch kovalski (aka yackson): https://morchkovalski.com*".format(
            message.author.mention,
            MemeTemplate.count(context),
            sourceimg_count(context),
            Meem.possible_combinations(context)
        )
    )


# noinspection PyCompatibility
@client.event
async def cmd_meem(message):
    context = MemeContext.by_id(SERVER_WHITELIST.get(message.server.id))

    await client.send_typing(message.channel)

    if message.author.id not in NO_LIMIT_WHITELIST:
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

    meme = Meem.generate(context=context)
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

COMMANDS = OrderedDict([
    ('help', {
        'fun': cmd_help,
        'help': 'show this text'
    }),
    ('meem', {
        'fun': cmd_meem,
        'help': 'generate a random meme'
    }),
    ('hypersad', {
        'fun': cmd_hypersad,
        # 'servers': [
        #     '154305477323390976'  # hldiscord
        # ]
    }),
    ('choo', {
        'fun': cmd_choo
    }),
    ('about', {
        'fun': cmd_about
    })
])


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

    if client.user in message.mentions:
        splitcmd = ['about']
    elif not msg.startswith(PREFIX):
        return
    else:
        splitcmd = msg[len(PREFIX):].split(' ')

    cmd_data = COMMANDS.get(splitcmd[0])
    server_whitelist = cmd_data.get('servers')

    if cmd_data and (server_whitelist is None or server_id in server_whitelist):
        await COMMANDS[splitcmd[0]]['fun'](message)


# noinspection PyCompatibility
@client.event
async def on_ready():
    await client.change_presence(game=discord.Game(name='lambdabot.morchkovalski.com'))


client.run(AccessToken.objects.get(name="discord").token)
