import config
from cleverwrap import CleverWrap
from json.decoder import JSONDecodeError
from discordbot.util import DelayedTask, log

_cb_conversations = {}
_cb_active = bool(config.CLEVERBOT_TOKEN)


def is_active():
    return _cb_active


async def talk(client, channel, user, message, nodelay=False):
    global _cb_active
    if not _cb_active:
        return None

    sender_id = user.user.user_id
    if _cb_conversations.get(sender_id) is None:
        log("creating session for {}".format(user), tag="cleverbot")
        _cb_conversations[sender_id] = CleverWrap(config.CLEVERBOT_TOKEN)

    response = "error :cry:"
    success = False
    retries = 5
    while not success and retries > 0:
        try:
            response = _cb_conversations[sender_id].say(message)
            success = True
        except JSONDecodeError:
            log("error! recreating session for {}".format(user), tag="cleverbot")
            _cb_conversations[sender_id] = CleverWrap(config.CLEVERBOT_TOKEN)
            retries -= 1

    if response is None:
        log("cleverbot request failed".format(response), tag="cleverbot")
        return None

    log("response: {}".format(response), tag="cleverbot")
    delay = 0 if nodelay else 0.2 + min(0.04 * len(message), 4)
    if delay > 0:
        DelayedTask(delay, client.send_typing, (channel,)).run()
        delay += min(0.17 * len(response), 4)
    DelayedTask(delay, client.send_message, (channel, "<@{0}> {1}".format(sender_id, response))).run()

    return response
