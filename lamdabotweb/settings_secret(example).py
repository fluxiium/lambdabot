# this appears on the meme web pages, in django admin and some other places
BOT_NAME = "LambdaBot"

# bot's twitter handle
BOT_NAME_TWITTER = "LambdaBot3883"

# bot's facebook username
BOT_NAME_FACEBOOK = "LambdaBot"

# bot's website url
WEBSITE_URL = 'https://change.this.com/'

# the bot will keep all its media (source images, templates, generated memes) in this subdirectory of MEDIA_ROOT
MEDIA_SUBDIR = 'lambdabot'

# how many source images and templates should be queued to be used in memes (to prevent the same ones
# being used many times in a row)
IMG_QUEUE_LENGTH = 100

# how many seconds the bot should wait for an answer from murphybot
MURPHYBOT_TIMEOUT = 20

# maximum size for submitted source images. PNG images that exceed this will be converted to
# JPG and their size will be checked again
MAX_SRCIMG_SIZE = 1500000

# django-specific settings ( more info: https://docs.djangoproject.com/en/2.0/ref/settings/ )
SECRET_KEY = 'change this'
DEBUG = False
ALLOWED_HOSTS = ['change.this.com']
STATIC_ROOT = '/change/this'
STATIC_URL = 'https://change.this.com/really/do/it'
MEDIA_ROOT = '/also/change/this'
MEDIA_URL = 'https://change.this.com/as/well'
DATABASES = {
    'default': {
        # i advise against using sqlite cause i had problems with it when
        # many people were using the bot at the same time
    },
}
