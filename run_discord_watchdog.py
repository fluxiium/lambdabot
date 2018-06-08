# this will run the bot and kill the process when it detects it froze (which happens way too often for some
# fuckin magical reason)

import discord
import logging
import subprocess
import os
import sys
import lamdabotweb.settings as config

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')

bot_process = subprocess.Popen([sys.executable, os.path.join(config.BASE_DIR, "run_discord_bot.py")])
logging.info(f'bot process started: {bot_process.pid}')

class WatchdogClient(discord.Client):

    async def on_member_update(self, _, member: discord.Member):
        global bot_process
        if str(member.id) == config.DISCORD_BOT_ID and member.status == discord.Status.offline:
            bot_process.kill()
            bot_process = subprocess.Popen([sys.executable, os.path.join(config.BASE_DIR, "run_discord_bot.py")])
            logging.info(f'bot process restarted')

bot = WatchdogClient()
bot.run(config.DISCORD_WATCHDOG_TOKEN)
