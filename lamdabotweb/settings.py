import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, '.env'))

DEBUG = bool(int(os.getenv('DEBUG', False)))
SECRET_KEY = os.getenv('SECRET_KEY')

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

# discord api stuff for website
DISCORD_OAUTH2_CLIENT_ID = os.getenv('DISCORD_OAUTH2_CLIENT_ID')
DISCORD_OAUTH2_CLIENT_SECRET = os.getenv('DISCORD_OAUTH2_CLIENT_SECRET')

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
DISCORD_STATUS = os.getenv('DISCORD_STATUS')

CLEVERBOT_USER = os.getenv('CLEVERBOT_USER')
CLEVERBOT_KEY = os.getenv('CLEVERBOT_KEY')

TELEGRAM_API_ID = int(os.getenv('TELEGRAM_API_ID'))
TELEGRAM_API_HASH = os.getenv('TELEGRAM_API_HASH')
MURPHYBOT_TIMEOUT = int(os.getenv('MURPHYBOT_TIMEOUT'))

RECAPTCHA_PUBLIC_KEY = os.getenv('RECAPTCHA_SITE_KEY')
RECAPTCHA_PRIVATE_KEY = os.getenv('RECAPTCHA_SECRET_KEY')
NOCAPTCHA = True

MEEM_MAX_SRCIMG_SIZE = int(os.getenv('MEEM_MAX_SRCIMG_SIZE'))
MEEM_CLEANUP_DAYS = int(os.getenv('MEEM_CLEANUP_DAYS'))
MEEM_LIMIT = int(os.getenv('MEEM_LIMIT'))
MEEM_COOLDOWN = int(os.getenv('MEEM_COOLDOWN'))
MEEM_QUEUE_LENGTH = int(os.getenv('MEEM_QUEUE_LENGTH'))

DANCE_MAX_W = int(os.getenv('DANCE_MAX_W'))
DANCE_MAX_LEN = int(os.getenv('DANCE_MAX_LEN'))
DANCE_LIMIT = int(os.getenv('DANCE_LIMIT'))
DANCE_COOLDOWN = int(os.getenv('DANCE_COOLDOWN'))

FACEBOOK_APP_ID = os.getenv('FACEBOOK_APP_ID')
FACEBOOK_APP_SECRET = os.getenv('FACEBOOK_APP_SECRET')


if DEBUG:
    WEBSITE_URL = 'http://192.168.100.11:8000/'
    ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]', '192.168.100.11']
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')
    STATIC_URL = '/static/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
    MEDIA_URL = '/media/'
    IMAGEMAGICK_PATH = 'C:\\Program Files\\ImageMagick-7.0.4-Q16\\convert.exe'
    DATA_UPLOAD_MAX_NUMBER_FIELDS = None
else:
    WEBSITE_URL = 'https://lambda.bot.nu/'
    ALLOWED_HOSTS = ['lambda.bot.nu', 'lambdabot.morchkovalski.com']
    STATIC_ROOT = '/srv/static.morchkovalski.com/lambdabot'
    STATIC_URL = 'https://static.morchkovalski.com/lambdabot/'
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    STATICFILES_FINDERS = (
        'django.contrib.staticfiles.finders.FileSystemFinder',
        'django.contrib.staticfiles.finders.AppDirectoriesFinder',
        'compressor.finders.CompressorFinder',
    )
    COMPRESS_ENABLED = True
    COMPRESS_OFFLINE = True
    COMPRESS_CSS_FILTERS = ['compressor.filters.css_default.CssAbsoluteFilter', 'compressor.filters.cssmin.CSSMinFilter']
    MEDIA_ROOT = '/srv/media.morchkovalski.com/lambdabot'
    MEDIA_URL = 'https://media.morchkovalski.com/lambdabot/'
    IMAGEMAGICK_PATH = '/usr/bin/convert'

LOGIN_URL = WEBSITE_URL + 'discord_oauth2/'
DISCORD_OAUTH2_REDIRECT_URI = WEBSITE_URL + 'discord_oauth2/callback'
BOT_INVITE_URL = f'https://discordapp.com/api/oauth2/authorize?client_id={DISCORD_OAUTH2_CLIENT_ID}&permissions=51264&scope=bot'

ROOT_URLCONF = 'lamdabotweb.urls'
FIXTURE_DIRS = {os.path.join(BASE_DIR, "fixtures")}
WSGI_APPLICATION = 'lamdabotweb.wsgi.application'
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = False
USE_L10N = True
USE_TZ = True

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'compressor',
    'colorfield',
    'discordbot',
    'facebookbot',
    'twitterbot',
    'memeviewer',
    'captcha',
    'discord_oauth2',
    'website',
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
    'discord_oauth2.middleware.discord_oauth2_middleware',
    'website.middleware.website_middleware',
]

AUTHENTICATION_BACKENDS = [
    'discord_oauth2.auth.DiscordOAuth2Backend',
    'django.contrib.auth.backends.ModelBackend',
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
