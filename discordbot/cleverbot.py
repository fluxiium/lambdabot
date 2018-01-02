import random
from cleverwrap import CleverWrap
from json.decoder import JSONDecodeError

from discordbot.util import DelayedTask, delay_send, log
from memeviewer.models import AccessToken

CP_ID = "289816859002273792"
BOT_COMMANDS_CHANNEL = "297518974730764288"
CP_HELLOS = ['hi', 'hello', 'sup', 'yo', 'waddup', 'wuss poppin b', 'good morning', 'greetings']
CP_BYES = ['ok bye', 'cya', 'see ya', 'bye', 'later', 'gtg bye']

cb_conversations = {}


async def cptalk_say(client, channel, sender_id, message, delay):
    if delay > 0:
        DelayedTask(delay, delay_send, (client.send_typing, channel)).run()
        delay += min(0.17 * len(message), 4)
    DelayedTask(delay, delay_send, (client.send_message, channel, "<@{0}> {1}".format(sender_id, message))).run()


async def cb_talk(client, channel, user, message, nodelay=False):
    if cb_conversations.get(user.user.user_id) is None:
        log("creating session for {}".format(user), tag="cleverbot")
        cb_conversations[user.user.user_id] = CleverWrap(AccessToken.objects.get(name="cleverbot").token)

    try:
        response = cb_conversations[user.user.user_id].say(message)
    except JSONDecodeError:
        response = "error"
    log("response: {}".format(response), tag="cleverbot")
    await cptalk_say(client, channel, user.user.user_id, response, 0 if nodelay else 0.2 + min(0.04 * len(message), 4))


async def start_cptalk(client):
    global cb_conversations
    if cb_conversations.get(CP_ID) is None:
        cb_conversations[CP_ID] = CleverWrap(AccessToken.objects.get(name="cleverbot").token)
        await cptalk_say(client, client.get_channel(BOT_COMMANDS_CHANNEL), CP_ID, random.choice(CP_HELLOS), 0.1)
    else:
        cb_conversations[CP_ID] = None
