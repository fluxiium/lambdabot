import json
import os
import random
import re
import uuid

from django.db import models
from django.db.models import Q
from django.utils import timezone

from lamdabotweb.settings import MEMES_DIR, STATIC_URL, WEBSITE, SOURCEIMG_DIR, SOURCEIMG_BLACKLIST, \
    SOURCEIMG_QUEUE_LENGTH, ALLOWED_EXTENSIONS, TEMPLATE_QUEUE_LENGTH, TEMPLATE_DIR

SYS_RANDOM = random.SystemRandom()


def struuid4():
    return str(uuid.uuid4())


def next_meme_number():
    return (Meem.objects.all().aggregate(largest=models.Max('number'))['largest'] or 0) + 1


def next_template(context):
    """ returns next template filename """

    # read queue from db
    result = ImageInContext.objects.filter(image_type=ImageInContext.IMAGE_TYPE_TEMPLATE, context_link=context)

    # if empty, make new queue
    if result.count() == 0:

        template_queue = MemeTemplate.objects\
                             .order_by('?')[0:(min(TEMPLATE_QUEUE_LENGTH, MemeTemplate.objects.count()))]

        # save queue to db
        for t in template_queue:
            template_in_context = ImageInContext(image_name=t.name, image_type=ImageInContext.IMAGE_TYPE_TEMPLATE,
                                                 context_link=context)
            template_in_context.save()

        result = ImageInContext.objects.filter(image_type=ImageInContext.IMAGE_TYPE_TEMPLATE, context_link=context)

    template_in_context = result.first()
    template = template_in_context.image_name
    template_in_context.delete()

    template_obj = MemeTemplate.objects\
        .filter(name=template, disabled=False)\
        .filter(Q(contexts=context) | Q(contexts=None))\
        .first()

    if template_obj is None:
        return next_template(context)
    elif not os.path.isfile(os.path.join(TEMPLATE_DIR, template)):
        raise FileNotFoundError
    else:
        return template_obj


def next_sourceimg(context):
    """ returns next source image filename """

    # read queue from db
    result = ImageInContext.objects.filter(image_type=ImageInContext.IMAGE_TYPE_SOURCEIMG, context_link=context)

    # if empty, make new queue
    if len(result) == 0:

        # add common source images to list
        available_sourceimgs = \
            [file for file in os.listdir(SOURCEIMG_DIR) if re.match(ALLOWED_EXTENSIONS, file, re.IGNORECASE)]

        # add context's source images to list
        if os.path.isdir(os.path.join(SOURCEIMG_DIR, context.short_name)):
            available_sourceimgs += \
                (os.path.join(context.short_name, file)
                 for file in os.listdir(os.path.join(SOURCEIMG_DIR, context.short_name))
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
                                                  context_link=context)
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


class MemeContext(models.Model):
    short_name = models.CharField(max_length=32, primary_key=True)
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class MemeTemplate(models.Model):
    name = models.CharField(max_length=64, primary_key=True)
    contexts = models.ManyToManyField(MemeContext)
    bg_color = models.CharField(max_length=16, null=True, default=None)
    bg_img = models.CharField(max_length=64, null=True, default=None)
    disabled = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class MemeTemplateSlot(models.Model):
    template = models.ForeignKey(MemeTemplate, on_delete=models.CASCADE)
    slot_order = models.IntegerField()
    x = models.IntegerField()
    y = models.IntegerField()
    w = models.PositiveIntegerField()
    h = models.PositiveIntegerField()
    rotate = models.IntegerField(default=0)
    mask = models.BooleanField(default=False)
    blur = models.BooleanField(default=False)
    grayscale = models.BooleanField(default=False)
    cover = models.BooleanField(default=False)

    def __str__(self):
        return "{0} - slot #{1}".format(self.template, self.slot_order)


class Meem(models.Model):
    number = models.IntegerField(default=next_meme_number)
    meme_id = models.CharField(primary_key=True, max_length=36, default=struuid4)
    template_link = models.ForeignKey(MemeTemplate)
    sourceimgs = models.TextField()
    context_link = models.ForeignKey(MemeContext)
    gen_date = models.DateTimeField(default=timezone.now)

    @classmethod
    def create(cls, template, sourceimgs, context):
        meem = cls(template_link=template, sourceimgs=json.dumps(sourceimgs), context_link=context)
        meem.save()
        return meem

    @classmethod
    def generate(cls, context, template_file=None):
        context_obj = MemeContext.objects.get(short_name=context)
        template = template_file and MemeTemplate.objects.get(name=template_file) or next_template(context_obj)
        source_files = []
        prev_slot_id = None
        for slot in template.memetemplateslot_set.order_by('slot_order').all():
            if slot.slot_order == prev_slot_id:
                continue
            # pick source file that hasn't been used
            while True:
                source_file = next_sourceimg(context_obj)
                if source_file not in source_files:
                    break
            source_files.append(source_file)
            prev_slot_id = slot.slot_order
        meem = cls.create(template, source_files, context_obj)
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
    context_link = models.ForeignKey(MemeContext, on_delete=models.CASCADE)

    def __str__(self):
        return "{0} - {1} ({2})".format(self.image_name, self.context, self.IMAGE_TYPE_CHOICES[self.image_type][1])


class AccessToken(models.Model):
    name = models.CharField(max_length=32, primary_key=True)
    token = models.TextField()

    def __str__(self):
        return self.name
