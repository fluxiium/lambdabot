import json
import operator
import os
import random
import re
import uuid

from functools import reduce

from PIL import Image
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone

from lamdabotweb.settings import MEMES_DIR, STATIC_URL, WEBSITE, SOURCEIMG_DIR, ALLOWED_EXTENSIONS, TEMPLATE_DIR

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

        queue_length = Setting.objects.filter(key='template queue length').first()
        queue_length = 77 if queue_length is None else int(queue_length.value)
        template_queue = MemeTemplate.objects.filter(disabled=False).filter(Q(contexts=context) | Q(contexts=None))\
            .order_by('?')[0:(min(queue_length, MemeTemplate.objects.count()))]

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


def sourceimg_count(context):
    available_sourceimgs = 0
    for file in os.listdir(SOURCEIMG_DIR):
        if re.match(ALLOWED_EXTENSIONS, file, re.IGNORECASE):
            available_sourceimgs += 1

    if os.path.isdir(os.path.join(SOURCEIMG_DIR, context.short_name)):
        for file in os.listdir(os.path.join(SOURCEIMG_DIR, context.short_name)):
            if re.match(ALLOWED_EXTENSIONS, file, re.IGNORECASE):
                available_sourceimgs += 1

    return available_sourceimgs


def next_sourceimg(context):
    """ returns next source image filename """

    # read queue from db
    result = ImageInContext.objects.filter(image_type=ImageInContext.IMAGE_TYPE_SOURCEIMG, context_link=context)

    # if empty, make new queue
    if result.count() == 0:

        queue_length = Setting.objects.filter(key='sourceimg queue length').first()
        queue_length = 133 if queue_length is None else int(queue_length.value)
        sourceimg_queue = MemeSourceImageOverride.objects.filter(accepted=True).filter(Q(contexts=context) | Q(contexts=None))\
            .order_by('?')[0:(min(queue_length, MemeSourceImageOverride.objects.count()))]

        # save queue to db
        for s in sourceimg_queue:
            sourceimg_in_context = ImageInContext(image_name=s, image_type=ImageInContext.IMAGE_TYPE_SOURCEIMG,
                                                  context_link=context)
            sourceimg_in_context.save()

        result = ImageInContext.objects.filter(image_type=ImageInContext.IMAGE_TYPE_SOURCEIMG, context_link=context)

    sourceimg_in_context = result.first()
    sourceimg = sourceimg_in_context.image_name
    sourceimg_in_context.delete()

    sourceimg_obj = MemeSourceImageOverride.objects\
        .filter(name=sourceimg, accepted=True)\
        .filter(Q(contexts=context) | Q(contexts=None))\
        .first()

    if sourceimg_obj is None:
        return next_sourceimg(context)
    elif not os.path.isfile(os.path.join(SOURCEIMG_DIR, sourceimg)):
        raise FileNotFoundError
    else:
        return sourceimg_obj


# MODELS --------------------------------------------------------------------------------------------------------

class Setting(models.Model):

    class Meta:
        verbose_name = "Setting"

    key = models.CharField(max_length=64, verbose_name='Key')
    value = models.CharField(max_length=64, verbose_name='Value')


class MemeContext(models.Model):

    class Meta:
        verbose_name = "Context"

    short_name = models.CharField(max_length=32, primary_key=True, verbose_name='Short name')
    name = models.CharField(max_length=64, verbose_name='Name')

    @classmethod
    def by_id(cls, name):
        return cls.objects.get(short_name=name)

    def get_reset_url(self):
        return reverse('memeviewer:context_reset_view', kwargs={'context': self.short_name})

    def __str__(self):
        return self.name


class MemeSourceImageOverride(models.Model):

    class Meta:
        verbose_name = "Source image override"

    name = models.CharField(max_length=64, primary_key=True, verbose_name='File name')
    friendly_name = models.CharField(max_length=64, default='', blank=True, verbose_name='Friendly name')
    contexts = models.ManyToManyField(MemeContext, blank=True, verbose_name='Contexts')
    accepted = models.BooleanField(default=False, verbose_name='Accepted')
    add_date = models.DateTimeField(default=timezone.now, verbose_name='Date added')

    def is_in_context(self, context):
        return self.contexts.count() == 0 or self.contexts.filter(short_name=context.short_name).first() is not None

    def get_image_url(self):
        return STATIC_URL + 'lambdabot/resources/sourceimg/' + self.name

    def __str__(self):
        return self.friendly_name if self.friendly_name != '' else self.name

    @classmethod
    def search(cls, term):
        return cls.objects.filter(Q(name__contains=term) | Q(contexts__short_name__contains=term))

    @classmethod
    def submit(cls, path):
        filename = "{}.jpg".format(str(uuid.uuid4()))
        image = Image.open(path)
        image = image.convert('RGB')
        image.save(os.path.join(SOURCEIMG_DIR, filename))
        srcimg = MemeSourceImageOverride(name=filename)
        srcimg.save()
        return srcimg

    @classmethod
    def count(cls, context):
        return cls.by_context(context).count()

    @classmethod
    def by_context(cls, context):
        return cls.objects.filter(Q(contexts=context) | Q(contexts=None))


class MemeTemplate(models.Model):

    class Meta:
        verbose_name = "Template"

    name = models.CharField(max_length=64, primary_key=True, verbose_name='File name')
    contexts = models.ManyToManyField(MemeContext, blank=True, verbose_name='Contexts')
    bg_color = models.CharField(max_length=16, default='', blank=True, verbose_name='Background color')
    bg_img = models.CharField(max_length=64, default='', blank=True, verbose_name='Background image')
    disabled = models.BooleanField(default=False, verbose_name='Disabled')
    add_date = models.DateTimeField(default=timezone.now, verbose_name='Date added')

    @classmethod
    def count(cls, context):
        return cls.by_context(context).count()

    @classmethod
    def by_context(cls, context):
        return cls.objects.filter(Q(contexts=context) | Q(contexts=None))

    @classmethod
    def find(cls, name):
        if isinstance(name, MemeContext):
            found = Meem.objects.filter(context_link=name).order_by('-gen_date').first()
            return found.template_link if found is not None else None
        found = cls.objects.filter(name=name).first()
        if found is not None:
            return found
        found = cls.objects.filter(name__startswith=name).first()
        if found is not None:
            return found
        found = cls.objects.filter(name__contains=name).first()
        if found is not None:
            return found
        name = re.split(' |\.|/', name)
        found = cls.objects.filter(reduce(operator.and_, (Q(name__contains=x) for x in name))).first()
        if found is not None:
            return found
        found = cls.objects.filter(reduce(lambda x, y: x | y, [Q(name=word) for word in name])).first()
        if found is not None:
            return found
        found = cls.objects.filter(reduce(lambda x, y: x | y, [Q(name__startswith=word) for word in name])).first()
        if found is not None:
            return found
        found = cls.objects.filter(reduce(lambda x, y: x | y, [Q(name__contains=word) for word in name])).first()
        return found

    @classmethod
    def search(cls, term):
        return cls.objects.filter(Q(name__contains=term) | Q(contexts__short_name__contains=term))

    def possible_combinations(self, context):
        possible = 1
        slots = MemeTemplateSlot.objects.filter(template=self)
        srcimgs = MemeSourceImageOverride.count(context)
        prev_slot_id = None
        for slot in slots:
            if slot.slot_order == prev_slot_id:
                continue
            possible *= srcimgs
            srcimgs -= 1
        return possible

    def get_preview_url(self):
        return reverse('memeviewer:template_preview_view', kwargs={'template_name': self.name})

    def get_image_url(self):
        return STATIC_URL + 'lambdabot/resources/templates/' + self.name

    def contexts_string(self):
        contexts = self.contexts.all()
        if contexts.count() == 0:
            return "*"
        result = ""
        for context in contexts:
            result += "{} ".format(context.short_name)
        return result.strip()

    def __str__(self):
        return self.name


class MemeTemplateSlot(models.Model):

    class Meta:
        verbose_name = "Template slot"

    template = models.ForeignKey(MemeTemplate, on_delete=models.CASCADE, verbose_name='Template')
    slot_order = models.IntegerField(verbose_name='Slot order')
    x = models.IntegerField()
    y = models.IntegerField()
    w = models.PositiveIntegerField()
    h = models.PositiveIntegerField()
    rotate = models.IntegerField(default=0, verbose_name='Rotation')
    mask = models.BooleanField(default=False, verbose_name='Mask')
    blur = models.BooleanField(default=False, verbose_name='Blur')
    grayscale = models.BooleanField(default=False, verbose_name='Grayscale')
    cover = models.BooleanField(default=False, verbose_name='Cover')

    def __str__(self):
        return "{0} - slot #{1}".format(self.template, self.slot_order)


class Meem(models.Model):

    class Meta:
        verbose_name = "Meme"

    number = models.IntegerField(default=next_meme_number, verbose_name='Number')
    meme_id = models.CharField(primary_key=True, max_length=36, default=struuid4, verbose_name='ID')
    template_link = models.ForeignKey(MemeTemplate, verbose_name='Template')
    sourceimgs = models.TextField(verbose_name='Source images')
    context_link = models.ForeignKey(MemeContext, verbose_name='Context')
    gen_date = models.DateTimeField(default=timezone.now, verbose_name='Date generated')

    @classmethod
    def create(cls, template, sourceimgs, context):
        meem = cls(template_link=template, sourceimgs=json.dumps(sourceimgs), context_link=context)
        meem.save()
        return meem

    @classmethod
    def generate(cls, context, template=None):
        if template is None:
            template = next_template(context)
        source_files = []
        prev_slot_id = None
        for slot in template.memetemplateslot_set.order_by('slot_order').all():
            if slot.slot_order == prev_slot_id:
                continue
            # pick source file that hasn't been used
            while True:
                source_file = next_sourceimg(context).name
                if source_file not in source_files:
                    break
            source_files.append(source_file)
            prev_slot_id = slot.slot_order
        meem = cls.create(template, source_files, context)
        return meem

    @classmethod
    def possible_combinations(cls, context):
        possible = 0
        for template in MemeTemplate.by_context(context):
            possible += template.possible_combinations(context)
        return possible

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


class ImageInContext(models.Model):

    class Meta:
        verbose_name = "Queued image"

    IMAGE_TYPE_TEMPLATE = 0
    IMAGE_TYPE_SOURCEIMG = 1
    IMAGE_TYPE_CHOICES = (
        (IMAGE_TYPE_TEMPLATE, "Template"),
        (IMAGE_TYPE_SOURCEIMG, "Source Image"),
    )
    image_type = models.IntegerField(choices=IMAGE_TYPE_CHOICES, verbose_name='Image type')
    image_name = models.CharField(max_length=64, verbose_name='File name')
    context_link = models.ForeignKey(MemeContext, on_delete=models.CASCADE, verbose_name='Context')

    def __str__(self):
        return "{0} - {1} ({2})"\
            .format(self.image_name, self.context_link.short_name, self.IMAGE_TYPE_CHOICES[self.image_type][1])


class AccessToken(models.Model):

    class Meta:
        verbose_name = "Access token"

    name = models.CharField(max_length=32, primary_key=True, verbose_name='Name')
    token = models.TextField(verbose_name='Token')

    def __str__(self):
        return self.name
