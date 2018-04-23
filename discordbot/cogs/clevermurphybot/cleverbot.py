import discord
import asyncio
import config
from util import log
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.common.keys import Keys


_cb_conversations = {}


def is_active():
    return config.CLEVERBOT_ENABLED


def _get_driver(user: discord.User):
    if _cb_conversations.get(user.id) is None:
        log("creating session for {}".format(user), tag="cleverbot")
        try:
            driver = webdriver.Firefox()
            driver.get('http://www.cleverbot.com/')
            _cb_conversations[user.id] = driver
            return driver
        except WebDriverException:
            asyncio.sleep(1)
            return _get_driver(user)
    else:
        driver = _cb_conversations[user.id]
        try:
            assert 'Cleverbot.com' in driver.title
            return driver
        except WebDriverException:
            _cb_conversations.pop(user.id)
            return _get_driver(user)


async def talk(msg: discord.Message, msg_text):
    if not is_active():
        return None

    user = msg.author
    channel = msg.channel

    async with msg.channel.typing():
        driver = _get_driver(user)
        input_box = driver.find_element_by_name('stimulus')
        input_box.clear()
        input_box.send_keys(msg_text)
        input_box.send_keys(Keys.RETURN)
        while True:
            asyncio.sleep(1)
            try:
                driver.find_element_by_id('snipTextIcon')
                break
            except NoSuchElementException:
                pass
        response_elem = driver.find_element_by_xpath('//*[@id="line1"]/span[1]')
        response = response_elem.text

    if msg.guild is None:
        await channel.send(response)
    else:
        await channel.send("{0} {1}".format(user.mention, response))
