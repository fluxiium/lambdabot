from discordbot.util import delay_send


SAY_CHANNEL = ''


async def cmd_saych(client, message, args, **_):
    global SAY_CHANNEL

    if len(args) != 2:
        await delay_send(
            client.send_message,
            message.channel,
            "{0} usage: `{1} (channel ID)`".format(message.author.mention, args[0]),
        )
        return

    SAY_CHANNEL = args[1]
    if client.get_channel(SAY_CHANNEL) is None:
        SAY_CHANNEL = message.channel.id

    await delay_send(
        client.send_message,
        message.channel,
        "{0} say channel set to <#{1}>".format(message.author.mention, SAY_CHANNEL),
    )


async def cmd_say(client, message, argstr, args, **_):
    global SAY_CHANNEL

    if len(args) < 2:
        await delay_send(
            client.send_message,
            message.channel,
            "{0} usage: `{1} (text)`".format(message.author.mention, args[0]),
        )
        return

    channel = client.get_channel(SAY_CHANNEL)
    if channel is None:
        SAY_CHANNEL = message.channel.id
        channel = client.get_channel(SAY_CHANNEL)

    await delay_send(
        client.send_message,
        channel,
        argstr,
    )

    await delay_send(
        client.send_message,
        message.channel,
        "{0} message sent in channel <#{1}>".format(message.author.mention, SAY_CHANNEL),
    )
