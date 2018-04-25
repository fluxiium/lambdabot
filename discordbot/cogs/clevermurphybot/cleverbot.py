import discord
import asyncio
import config
from util import log, log_exc
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.common.keys import Keys
from django.utils import timezone
from datetime import timedelta


_cb_conversations = {}
_waiting = {}
_last_msg = {}


def is_active():
    return config.CLEVERBOT_TIMEOUT != 0


def start(client):
    client.loop.create_task(_cb_cleanup_task())


async def _cb_cleanup_task():
    while True:
        for user, when in _last_msg.items():
            if when and timezone.now() - timedelta(seconds=config.CLEVERBOT_SESSION_TIMEOUT) > when:
                _end_session(user)
        await asyncio.sleep(10)


def _get_driver(user: discord.User, attempt=10):
    try:
        driver = _cb_conversations.get(user)
        if not driver:
            log("creating session for {}".format(user), tag="cleverbot")
            if config.DEBUG:
                driver = webdriver.Firefox()
            else:
                driver = webdriver.PhantomJS()
            driver.get('http://www.cleverbot.com/')
            _cb_conversations[user] = driver
            return driver
        else:
            assert 'Cleverbot.com' in driver.title
            return driver
    except WebDriverException as exc:
        _cb_conversations[user] = None
        if attempt > 0:
            return _get_driver(user, attempt - 1)
        else:
            log_exc(exc)
            raise exc


def _end_session(user: discord.User):
    driver = _cb_conversations.get(user)
    if driver:
        log("ending session for {}".format(user), tag="cleverbot")
        driver.quit()
        _waiting[user] = None
        _last_msg[user] = None
        _cb_conversations[user] = None


async def talk(msg: discord.Message, msg_text):
    if not is_active():
        return

    user = msg.author

    if _waiting.get(user):
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
            _waiting[user] = True
            while attempt > 0:
                await asyncio.sleep(1)
                try:
                    driver.find_element_by_id('snipTextIcon')
                    response_elem = driver.find_element_by_xpath('//*[@id="line1"]/span[1]')
                    response = response_elem.text
                    _last_msg[user] = timezone.now()
                    break
                except NoSuchElementException:
                    attempt -= 1
            if attempt == 0:
                driver.quit()
            _waiting[user] = None
            log("response to {}: {}".format(user, response), tag="cleverbot")
        except WebDriverException:
            pass

    if msg.guild is None:
        await channel.send(response)
    else:
        await channel.send("{0} {1}".format(user.mention, response))
