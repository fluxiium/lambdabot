import discord
import asyncio
import config
from util import log, log_exc
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.common.keys import Keys


_cb_conversations = {}
_waiting = {}


def is_active():
    return config.CLEVERBOT_TIMEOUT != 0


def _get_driver(user: discord.User, attempt=5):
    try:
        driver = _cb_conversations.get(user.id)
        if not driver:
            log("creating session for {}".format(user), tag="cleverbot")
            driver = webdriver.Firefox()
            driver.get('http://www.cleverbot.com/')
            _cb_conversations[user.id] = driver
            return driver
        else:
            assert 'Cleverbot.com' in driver.title
            return driver
    except WebDriverException as exc:
        _cb_conversations[user.id] = None
        if attempt > 0:
            return _get_driver(user, attempt - 1)
        else:
            log_exc(exc)
            raise exc


async def talk(msg: discord.Message, msg_text):
    if not is_active():
        return

    user = msg.author

    if _waiting.get(user.id):
        return

    channel = msg.channel
    response = 'error :cry:'

    async with msg.channel.typing():
        try:
            driver = _get_driver(user)
            input_box = driver.find_element_by_name('stimulus')
            input_box.clear()
            input_box.send_keys(msg_text)
            input_box.send_keys(Keys.RETURN)
            attempt = config.CLEVERBOT_TIMEOUT
            _waiting[user.id] = True
            while True:
                if attempt == 0:
                    break
                await asyncio.sleep(1)
                try:
                    driver.find_element_by_id('snipTextIcon')
                    response_elem = driver.find_element_by_xpath('//*[@id="line1"]/span[1]')
                    response = response_elem.text
                    break
                except NoSuchElementException:
                    attempt -= 1
            _waiting.pop(user.id)
            log("response to {}: {}".format(user, response), tag="cleverbot")
        except WebDriverException:
            pass

    if msg.guild is None:
        await channel.send(response)
    else:
        await channel.send("{0} {1}".format(user.mention, response))
