# some stuff for the half-life discord, for logging message edits and deleted attachments

import discord
import textwrap
import os
import django
import config

from discord import Embed
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lamdabotweb.settings")
django.setup()

from discordbot.util import get_attachments, save_attachment, log

_IMG_ARCHIVE_CHANNEL = '395615705048809492'
if config.DEBUG:
    _SERVER_ID = '395615515101495299'
    _LOG_CHANNEL = '395616760302141450'
else:
    _SERVER_ID = '154305477323390976'
    _LOG_CHANNEL = '154637540341710848'

_client = discord.Client(max_messages=10000)


@_client.event
async def on_message_edit(old_message, message):
    if message.server.id != _SERVER_ID or old_message.content == message.content:
        return

    embed = Embed(
        description="**Message sent by {0} edited in <#{1}>**".format(message.author.mention, message.channel.id),
        color=0x117EA6,
    )
    embed.set_author(
        name=str(message.author),
        icon_url=message.author.avatar_url
    )
    embed.set_footer(
        text="ID: {0} | {1}".format(message.author.id, timezone.now().strftime("%a, %d %b %Y %I:%M %p")),
    )
    embed.add_field(
        name="Old message",
        value=textwrap.shorten(old_message.content, width=1000),
        inline=False,
    )
    embed.add_field(
        name="New message",
        value=textwrap.shorten(message.content, width=1000),
        inline=False,
    )

    await _client.send_message(_client.get_channel(_LOG_CHANNEL), embed=embed)


@_client.event
async def on_message_delete(message):
    if message.server.id != _SERVER_ID:
        return

    atts = get_attachments(message, get_embeds=False)

    if len(atts) == 0:
        return

    for att in atts:
        att_path = save_attachment(att['real_url'], att['filename'])
        msg_archived = await _client.send_file(_client.get_channel(_IMG_ARCHIVE_CHANNEL), att_path)
        att = get_attachments(msg_archived)[0]

        embed = Embed(
            description="**Attachment sent by {0} deleted in <#{1}>**\n{2}".format(
                message.author.mention, message.channel.id, att['real_url']
            ),
            color=0xFF470F,
        )
        embed.set_author(
            name=str(message.author),
            icon_url=message.author.avatar_url
        )
        embed.set_footer(
            text="ID: {0} | {1}".format(message.author.id, timezone.now().strftime("%a, %d %b %Y %I:%M %p")),
        )

        await _client.send_message(_client.get_channel(_LOG_CHANNEL), embed=embed)


@_client.event
async def on_ready():
    log('Logged in as', _client.user.name, _client.user.id)

_client.run(config.DISCORD_TOKEN)
