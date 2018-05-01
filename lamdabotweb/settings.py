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

if DEBUG:
    WEBSITE_URL = 'http://127.0.0.1:8000/'
    ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]']
    STATIC_ROOT = None
    STATIC_URL = '/static/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
    MEDIA_URL = '/media/'
    DATABASES = {
        # 'default': {
        #     'ENGINE': 'django.db.backends.postgresql_psycopg2',
        #     'NAME': DB_NAME,
        #     'USER': DB_USER,
        #     'PASSWORD': DB_PASSWORD,
        #     'HOST': DB_HOST,
        #     'PORT': DB_PORT,
        # },
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
    IMAGEMAGICK_PATH = "C:\Program Files\ImageMagick-7.0.4-Q16\convert.exe"
else:
    WEBSITE_URL = 'https://lambdabot.morchkovalski.com/'
    ALLOWED_HOSTS = ['lambdabot.morchkovalski.com']
    STATIC_ROOT = '/srv/static.morchkovalski.com'
    STATIC_URL = 'https://static.morchkovalski.com/'
    MEDIA_ROOT = '/srv/media.morchkovalski.com/lambdabot'
    MEDIA_URL = 'https://media.morchkovalski.com/lambdabot/'
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
    IMAGEMAGICK_PATH = '/usr/bin/convert'

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
    'django.contrib.admin',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'lamdabotweb.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'memeviewer/../templates')]
        ,
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

FIXTURE_DIRS = {
    os.path.join(BASE_DIR, "fixtures"),
}

WSGI_APPLICATION = 'lamdabotweb.wsgi.application'


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = False
USE_L10N = True
USE_TZ = True

IMG_QUEUE_LENGTH = 100
MAX_SRCIMG_SIZE = 1500000
RECENT_THRESHOLD = 10

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
