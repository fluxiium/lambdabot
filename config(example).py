WEBSITE_URL = 'https://lambdabot.morchkovalski.com/'
TIME_ZONE = 'UTC'
SECRET_KEY = '**********************'
DEBUG = False
ALLOWED_HOSTS = ['lambdabot.morchkovalski.com']
STATIC_ROOT = '/srv/static.morchkovalski.com'
STATIC_URL = 'https://static.morchkovalski.com/'
MEDIA_ROOT = '/srv/media.morchkovalski.com/lambdabot'
MEDIA_URL = 'https://media.morchkovalski.com/lambdabot/'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'lambdabot',
        'USER': 'lambdabot',
        'PASSWORD': '**********************',
        'HOST': 'localhost',
        'PORT': '',
    },
}
DISCORD_TOKEN = '**********************'
DISCORD_STATUS = '!help | lambdabot.morchkovalski.com'
DISCORD_CMD_PREFIX = '!'
DISCORD_COGS = [
    'help',
    'meem',
    'clevermurphybot',
    'extra',
    'faceapp',
]
IMG_QUEUE_LENGTH = 100
MAX_SRCIMG_SIZE = 1500000
RECENT_THRESHOLD = 5
IMAGEMAGICK_PATH = '/usr/bin/convert'
DISCORD_MEME_LIMIT = 5
DISCORD_MEME_COOLDOWN = 60
DANCE_MAX_W = 1000
DANCE_MAX_LEN = 40
DANCE_LIMIT = 2
DANCE_COOLDOWN = 10
CLEVERBOT_TIMEOUT = 120
CLEVERBOT_SESSION_TIMEOUT = 3600
TELEGRAM_API_ID = 0
TELEGRAM_API_HASH = '**********************'
MURPHYBOT_TIMEOUT = 20
