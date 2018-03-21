# some stuff for the half-life discord, for logging message edits and deleted attachments

import discord
import textwrap
import os
import django
from discord import Embed
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lamdabotweb.settings")
django.setup()

from discordbot.util import get_attachments, discord_send, save_attachment, log, log_exc
from lamdabotweb.settings import DEBUG, DISCORD_TOKEN

IMG_ARCHIVE_CHANNEL = '395615705048809492'
if DEBUG:
    SERVER_ID = '395615515101495299'
    LOG_CHANNEL = '395616760302141450'
else:
    SERVER_ID = '154305477323390976'
    LOG_CHANNEL = '154637540341710848'

client = discord.Client(max_messages=10000)


@client.event
async def on_message_edit(old_message, message):
    if message.server.id != SERVER_ID or old_message.content == message.content:
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

    await discord_send(client.send_message, client.get_channel(LOG_CHANNEL), embed=embed)


@client.event
async def on_message_delete(message):
    if message.server.id != SERVER_ID:
        return

    atts = get_attachments(message, get_embeds=False)

    if len(atts) == 0:
        return

    for att in atts:
        att_path = save_attachment(att['real_url'], att['filename'])
        msg_archived = await discord_send(client.send_file, client.get_channel(IMG_ARCHIVE_CHANNEL), att_path)
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

        await discord_send(client.send_message, client.get_channel(LOG_CHANNEL), embed=embed)


@client.event
async def on_ready():
    log('Logged in as', client.user.name, client.user.id)

client.run(DISCORD_TOKEN)
