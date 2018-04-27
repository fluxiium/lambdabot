# ---- GENERAL SETTINGS ----
# this appears on the meme web pages, in django admin and some other places
BOT_NAME = 'LambdaBot'

# how many source images and templates should be queued to be used in memes (to prevent the same ones
# being used many times in a row)
IMG_QUEUE_LENGTH = 100

# maximum size in bytes for submitted images. PNG images that exceed this limit will be converted to
# JPG and their size will be checked again
MAX_SRCIMG_SIZE = 1500000

# how many times an image has to be used by the meme generator for it to stop being considered "recent"
RECENT_THRESHOLD = 5

# public root url of the bot web app
WEBSITE_URL = 'http://example.com/'

# path to imagemagick executable
IMAGEMAGICK_PATH = '/usr/bin/convert'


# ---- DJANGO SETTINGS - more info: https://docs.djangoproject.com/en/2.0/ref/settings/
TIME_ZONE = 'UTC'
SECRET_KEY = ''
DEBUG = False
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]']
STATIC_ROOT = ''
STATIC_URL = ''
MEDIA_ROOT = ''
MEDIA_URL = ''
DATABASES = {
    'default': {
        # database info
    },
}


# ---- FACEBOOK SETTINGS - ignore if you're not going to use the facebook script ----
FACEBOOK_USERNAME = 'LambdaBot'
FACEBOOK_PAGE_ID = ''
FACEBOOK_APP_ID = ''
FACEBOOK_APP_SECRET = ''
# fill the 3 settings above, then run `python manage.py get_facebook_token (app user access token)`
# and the setting below will be filled automatically
FACEBOOK_PAGE_TOKEN = ''


# ---- TWITTER SETTINGS - ignore if you're not going to use the twitter script ----
TWITTER_USERNAME = 'LambdaBot3883'
TWITTER_CONSUMER_KEY = ''
TWITTER_CONSUMER_SECRET = ''
TWITTER_ACCESS_TOKEN_KEY = ''
TWITTER_ACCESS_TOKEN_SECRET = ''


# ---- DISCORD SETTINGS - ignore if you're not going to use the discord bot ----
DISCORD_TOKEN = ''
DISCORD_STATUS = '!help | ' + WEBSITE_URL
DISCORD_SEND_ATTACHMENTS = True  # will use embeds otherwise
DISCORD_CMD_PREFIX = '!'
DISCORD_COGS = [
    'help',
    'meem',
    'clevermurphybot',
    'customcmd',
    'extra',
]
DISCORD_MEME_LIMIT = 5
DISCORD_MEME_COOLDOWN = 60

# !dance command
DANCE_MAX_W = 1000
DANCE_MAX_LEN = 40
DANCE_LIMIT = 2
DANCE_COOLDOWN = 10

# set to 0 if you don't want the discord bot to have cleverbot functionality
CLEVERBOT_TIMEOUT = 120
CLEVERBOT_SESSION_TIMEOUT = 3600

# ignore if you don't want the discord bot to have murphybot functionality
TELEGRAM_API_ID = 0
TELEGRAM_API_HASH = ''

# how many seconds the bot should wait for an answer from murphybot
MURPHYBOT_TIMEOUT = 20
