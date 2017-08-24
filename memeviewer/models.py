import json
import os
import random
import re
import uuid

from django.db import models
from django.utils import timezone

from lamdabotweb.settings import MEMES_DIR, STATIC_URL, WEBSITE, SOURCEIMG_DIR, SOURCEIMG_BLACKLIST, \
    SOURCEIMG_QUEUE_LENGTH, ALLOWED_EXTENSIONS, TEMPLATE_QUEUE_LENGTH, TEMPLATE_DIR, MEME_TEMPLATES

SYS_RANDOM = random.SystemRandom()


def struuid4():
    return str(uuid.uuid4())


def next_meme_number():
    return (Meem.objects.all().aggregate(largest=models.Max('number'))['largest'] or 0) + 1


def next_template(context):
    """ returns next template filename """

    # read queue from db
    result = ImageInContext.objects.filter(image_type=ImageInContext.IMAGE_TYPE_TEMPLATE, context=context)

    # if empty, make new queue
    if len(result) == 0:

        # get list of templates
        available_templates = []
        for template_name, template_data in MEME_TEMPLATES.items():
            template_context = template_data.get('context')
            if template_context is None or template_context == context or \
                    (type(template_context) is list and context in template_context):
                available_templates.append(template_name)

        # create queue
        SYS_RANDOM.shuffle(available_templates)
        template_queue = available_templates[0:(min(TEMPLATE_QUEUE_LENGTH, len(available_templates)))]

        # get one template and remvoe it from queue
        template = template_queue.pop()

        # save queue to db
        for t in template_queue:
            template_in_context = ImageInContext(image_name=t, image_type=ImageInContext.IMAGE_TYPE_TEMPLATE,
                                                 context=context)
            template_in_context.save()

    # otherwise, get one template and remove it from queue
    else:
        template_in_context = result.first()
        template = template_in_context.image_name
        template_in_context.delete()

    if MEME_TEMPLATES.get(template) is None or MEME_TEMPLATES[template].get('context', context) != context:
        return next_template(context)
    elif not os.path.isfile(os.path.join(TEMPLATE_DIR, template)):
        raise FileNotFoundError
    else:
        return template


def next_sourceimg(context):
    """ returns next source image filename """

    # read queue from db
    result = ImageInContext.objects.filter(image_type=ImageInContext.IMAGE_TYPE_SOURCEIMG, context=context)

    # if empty, make new queue
    if len(result) == 0:

        # add common source images to list
        available_sourceimgs = \
            [file for file in os.listdir(SOURCEIMG_DIR) if re.match(ALLOWED_EXTENSIONS, file, re.IGNORECASE)]

        # add context's source images to list
        if os.path.isdir(os.path.join(SOURCEIMG_DIR, context)):
            available_sourceimgs += \
                (os.path.join(context, file) for file in os.listdir(os.path.join(SOURCEIMG_DIR, context))
                 if re.match(ALLOWED_EXTENSIONS, file, re.IGNORECASE))

        if len(available_sourceimgs) == 0:
            raise FileNotFoundError

        # create queue
        SYS_RANDOM.shuffle(available_sourceimgs)
        sourceimg_queue = available_sourceimgs[0:(min(SOURCEIMG_QUEUE_LENGTH, len(available_sourceimgs)))]

        # get one source image and remvoe it from queue
        sourceimg = sourceimg_queue.pop()

        # save queue to db
        for s in sourceimg_queue:
            sourceimg_in_context = ImageInContext(image_name=s, image_type=ImageInContext.IMAGE_TYPE_SOURCEIMG,
                                                  context=context)
            sourceimg_in_context.save()

    # otherwise, get one source image and remove it from queue
    else:
        sourceimg_in_context = result.first()
        sourceimg = sourceimg_in_context.image_name
        sourceimg_in_context.delete()

    if not os.path.isfile(os.path.join(SOURCEIMG_DIR, sourceimg)) or sourceimg in SOURCEIMG_BLACKLIST:
        return next_sourceimg(context)
    else:
        return sourceimg


class Meem(models.Model):
    number = models.IntegerField(default=next_meme_number)
    meme_id = models.CharField(primary_key=True, max_length=36, default=struuid4)
    template = models.CharField(max_length=64)
    sourceimgs = models.TextField()
    context = models.CharField(max_length=32)
    gen_date = models.DateTimeField(default=timezone.now)

    @classmethod
    def create(cls, template, sourceimgs, context):
        meem = cls(template=template, sourceimgs=json.dumps(sourceimgs), context=context)
        meem.save()
        return meem

    @classmethod
    def generate(cls, template_file=None, context='default'):
        template_file = template_file or next_template(context)
        source_files = []
        for _ in MEME_TEMPLATES[template_file]['src']:
            # pick source file that hasn't been used
            while True:
                source_file = next_sourceimg(context)
                if source_file not in source_files:
                    break
            source_files.append(source_file)
        meem = cls.create(template_file, source_files, context)
        return meem

    def get_sourceimgs(self):
        return json.loads(self.sourceimgs)

    def get_local_path(self):
        return os.path.join(MEMES_DIR, self.meme_id + '.jpg')

    def get_url(self):
        return STATIC_URL + 'lambdabot/resources/memes/' + self.meme_id + '.jpg'

    def get_info_url(self):
        return WEBSITE + 'meme/' + self.meme_id

    def __str__(self):
        return "{0} - #{1}, {2}".format(self.meme_id, self.number, self.gen_date)


class FacebookMeem(models.Model):
    meme = models.ForeignKey(Meem, on_delete=models.CASCADE)
    post = models.CharField(max_length=40)

    def __str__(self):
        return "{0} - {1}".format(self.meme.number, self.post)


class TwitterMeem(models.Model):
    meme = models.ForeignKey(Meem, on_delete=models.CASCADE)
    post = models.CharField(max_length=40)

    def __str__(self):
        return "{0} - {1}".format(self.meme.number, self.post)


class DiscordMeem(models.Model):
    meme = models.ForeignKey(Meem, on_delete=models.CASCADE)
    server = models.CharField(max_length=64)

    def __str__(self):
        return "{0} - {1}".format(self.meme.number, self.server)


class ImageInContext(models.Model):
    IMAGE_TYPE_TEMPLATE = 0
    IMAGE_TYPE_SOURCEIMG = 1
    IMAGE_TYPE_CHOICES = (
        (IMAGE_TYPE_TEMPLATE, "Template"),
        (IMAGE_TYPE_SOURCEIMG, "Source Image"),
    )
    image_type = models.IntegerField(choices=IMAGE_TYPE_CHOICES)
    image_name = models.CharField(max_length=64)
    context = models.CharField(max_length=32)

    def __str__(self):
        return "{0} ({1}) - {2}".format(self.image_name, self.image_type, self.context)
