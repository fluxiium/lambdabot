import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, '.env'))

DEBUG = bool(int(os.getenv('DEBUG', False)))

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

if DEBUG:
    WEBSITE_URL = 'http://192.168.0.20:8000/'
    ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]', '192.168.0.20']
    STATIC_ROOT = None
    STATIC_URL = '/static/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
    MEDIA_URL = '/media/'
    IMAGEMAGICK_PATH = "C:\Program Files\ImageMagick-7.0.4-Q16\convert.exe"
    BOT_INVITE_URL = 'https://discordapp.com/api/oauth2/authorize?client_id=347870501194170368&permissions=51264&scope=bot'
    DATA_UPLOAD_MAX_NUMBER_FIELDS = None
else:
    WEBSITE_URL = 'https://lambdabot.morchkovalski.com/'
    ALLOWED_HOSTS = ['lambdabot.morchkovalski.com']
    STATIC_ROOT = '/srv/static.morchkovalski.com'
    STATIC_URL = 'https://static.morchkovalski.com/'
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    MEDIA_ROOT = '/srv/media.morchkovalski.com/lambdabot'
    MEDIA_URL = 'https://media.morchkovalski.com/lambdabot/'
    IMAGEMAGICK_PATH = '/usr/bin/convert'
    BOT_INVITE_URL = 'https://discordapp.com/api/oauth2/authorize?client_id=347798135214702603&permissions=51264&scope=bot'

# django settings
SECRET_KEY = os.getenv('SECRET_KEY')
ROOT_URLCONF = 'lamdabotweb.urls'
FIXTURE_DIRS = {os.path.join(BASE_DIR, "fixtures")}
WSGI_APPLICATION = 'lamdabotweb.wsgi.application'
AUTH_PASSWORD_VALIDATORS = []
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = False
USE_L10N = True
USE_TZ = True

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'colorfield',
    'discordbot',
    'facebookbot',
    'twitterbot',
    'memeviewer',
    'captcha',
    'website',
    'django.contrib.admin',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'website.middleware.discord_oauth2_middleware',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
    },
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'memeviewer/../templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# discord api stuff for website
OAUTH2_CLIENT_ID = os.getenv('OAUTH2_CLIENT_ID')
OAUTH2_CLIENT_SECRET = os.getenv('OAUTH2_CLIENT_SECRET')

DISCORD_API_ROOT = 'https://discordapp.com/api'
OAUTH2_AUTH_URL = DISCORD_API_ROOT + '/oauth2/authorize'
OAUTH2_TOKEN_URL = DISCORD_API_ROOT + '/oauth2/token'
OAUTH2_REVOKE_URL = DISCORD_API_ROOT + '/oauth2/token/revoke'
OAUTH2_REDIRECT_URI = WEBSITE_URL + 'oauth2_callback'

DISCORD_SERVER_URL = 'https://discord.gg/J85Rhhd'

RECAPTCHA_PUBLIC_KEY = os.getenv('RECAPTCHA_SITE_KEY')
RECAPTCHA_PRIVATE_KEY = os.getenv('RECAPTCHA_SECRET_KEY')
NOCAPTCHA = True

# meme generator settings
MAX_SRCIMG_SIZE = 1500000
MEEM_CLEANUP_DAYS = 30

# discord bot settings
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
DISCORD_STATUS = '!help'
DISCORD_MEME_LIMIT = 5
DISCORD_MEME_COOLDOWN = 60
DANCE_MAX_W = 1000
DANCE_MAX_LEN = 40
DANCE_LIMIT = 2
DANCE_COOLDOWN = 10

CLEVERBOT_USER = os.getenv('CLEVERBOT_USER')
CLEVERBOT_KEY = os.getenv('CLEVERBOT_KEY')

TELEGRAM_API_ID = int(os.getenv('TELEGRAM_API_ID'))
TELEGRAM_API_HASH = os.getenv('TELEGRAM_API_ID')
MURPHYBOT_TIMEOUT = 20
