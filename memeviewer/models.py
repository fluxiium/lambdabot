import imghdr
import json
import operator
import os
import re
import uuid
import config
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.files import File
from functools import reduce
from PIL import Image
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from colorfield.fields import ColorField

from util.admin_utils import object_url


def struuid4():
    return str(uuid.uuid4())


def next_meme_number():
    return (Meem.objects.all().aggregate(largest=models.Max('number'))['largest'] or 0) + 1


class MemeContext(models.Model):

    class Meta:
        verbose_name = "Context"

    short_name = models.CharField(max_length=32, primary_key=True, verbose_name='ID')
    name = models.CharField(max_length=64, verbose_name='Name')
    recent_threshold = models.IntegerField(default=14, verbose_name='Recent threshold (days)')
    is_public = models.BooleanField(default=False, verbose_name='Is public?')
    meme_count = models.IntegerField(default=0, verbose_name='Generated memes')

    @classmethod
    def by_id(cls, name):
        return cls.objects.get(short_name=name)

    @classmethod
    def by_id_or_create(cls, name, friendly_name, is_public=False):
        context = cls.objects.get_or_create(short_name=name, defaults={'name': friendly_name, 'is_public': is_public})
        return context[0]

    def get_reset_url(self):
        return reverse('memeviewer:context_reset_view', kwargs={'context': self.short_name})

    def next_image(self, image_type):
        # read queue from db
        result = ImageInContext.objects.filter(image_type=image_type, context_link=self)
        objects = MemeSourceImage.objects if image_type == ImageInContext.IMAGE_TYPE_SOURCEIMG else MemeTemplate.objects

        # if empty, make new queue
        if result.count() == 0:

            queue_length = config.IMG_QUEUE_LENGTH
            recent_threshold = timezone.now() - timezone.timedelta(days=self.recent_threshold)

            img_queue_db = objects.filter(accepted=True).filter(Q(contexts=self) | Q(contexts=None)).order_by('?')
            img_queue_recent = img_queue_db.filter(change_date__gte=recent_threshold)[
                               0:(min(queue_length, objects.count()) / 2)]
            img_queue_old = img_queue_db[0:(min(queue_length, objects.count()) - img_queue_recent.count())]

            # save queue to db
            for s in img_queue_recent:
                ImageInContext.objects.create(image_name=s.name, image_type=image_type, context_link=self)

            for s in img_queue_old:
                if s not in img_queue_recent:
                    ImageInContext.objects.create(image_name=s.name, image_type=image_type, context_link=self)

            result = ImageInContext.objects.filter(image_type=image_type, context_link=self)

        img_in_context = result.order_by('?').first()
        sourceimg = img_in_context.image_name
        img_in_context.delete()

        img_obj = objects.filter(name=sourceimg, accepted=True).filter(Q(contexts=self) | Q(contexts=None)).first()

        if img_obj is None:
            return self.next_image(image_type)
        else:
            return img_obj

    def next_template(self):
        return self.next_image(ImageInContext.IMAGE_TYPE_TEMPLATE)

    def next_sourceimg(self):
        return self.next_image(ImageInContext.IMAGE_TYPE_SOURCEIMG)

    def _add_meem(self):
        self.meme_count += 1
        self.save()

    def __str__(self):
        return self.short_name


class MemeSourceImage(models.Model):

    class Meta:
        verbose_name = "Source image"

    name = models.CharField(max_length=256, primary_key=True, verbose_name='Unique ID', default=struuid4)
    image_file = models.ImageField(upload_to=config.MEDIA_SUBDIR + '/sourceimg/', max_length=256)
    friendly_name = models.CharField(max_length=64, default='', blank=True, verbose_name='Friendly name')
    contexts = models.ManyToManyField(MemeContext, blank=True, verbose_name='Contexts')
    accepted = models.BooleanField(default=False, verbose_name='Accepted')
    add_date = models.DateTimeField(default=timezone.now, verbose_name='Date added')
    change_date = models.DateTimeField(default=timezone.now, verbose_name='Last changed')
    meme_count = models.IntegerField(default=0, verbose_name='Memes')

    def clean(self):
        self.change_date = timezone.now()
        self.save()

    # add image to queues of all its contexts
    def enqueue(self):
        query = ImageInContext.objects.filter(image_name=self.name, image_type=ImageInContext.IMAGE_TYPE_SOURCEIMG)
        for imq in query:
            imq.delete()
        if self.accepted:
            contexts = self.contexts.all()
            if len(contexts) == 0:
                contexts = MemeContext.objects.all()
            for c in contexts:
                ImageInContext.objects.create(image_name=self.name, image_type=ImageInContext.IMAGE_TYPE_SOURCEIMG,
                                              context_link=c)

    def get_image_url(self):
        return self.image_file and self.image_file.url or''

    def __str__(self):
        return self.friendly_name or self.name

    def contexts_string(self):
        contexts = self.contexts.all()
        if contexts.count() == 0:
            return "*"
        result = ""
        for context in contexts:
            result += context.short_name + " "
        return result.strip()

    def _add_meem(self):
        self.meme_count += 1
        self.save()

    @classmethod
    def submit(cls, filepath, filename=None, friendly_name=None):
        try:
            image = Image.open(filepath)
        except OSError:
            return None

        imgid = struuid4()
        saved_filename = "{0}.{1}".format(imgid, imghdr.what(filepath))

        stat = os.stat(filepath)
        if stat.st_size > config.MAX_SRCIMG_SIZE and image.mode == "RGBA":
            image = image.convert('RGB')
            saved_filename += ".jpeg"
            filepath += ".jpeg"
            image.save(filepath)
            stat = os.stat(filepath)

        if stat.st_size > config.MAX_SRCIMG_SIZE:
            return None

        if friendly_name is None:
            friendly_name = filename and os.path.splitext(filename.replace('_', ' ').rstrip())[0] or ''
        srcimg = MemeSourceImage(name=imgid, friendly_name=friendly_name)
        srcimg.image_file.save(saved_filename, File(open(filepath, "rb")))
        srcimg.save()
        return srcimg

    @classmethod
    def count(cls, context):
        return cls.by_context(context).count()

    @classmethod
    def by_context(cls, context):
        return cls.objects.filter(Q(contexts=context) | Q(contexts=None)).filter(accepted=True)

    @classmethod
    def by_id(cls, name):
        return cls.objects.get(name=name)


class MemeTemplate(models.Model):

    class Meta:
        verbose_name = "Template"

    name = models.CharField(max_length=64, primary_key=True, verbose_name='Unique ID', default=struuid4)
    bg_image_file = models.ImageField(upload_to=config.MEDIA_SUBDIR + '/templates/', max_length=256, null=True, default=None,
                                      blank=True, verbose_name="Template background")
    image_file = models.ImageField(upload_to=config.MEDIA_SUBDIR + '/templates/', max_length=256, null=True, default=None,
                                   blank=True, verbose_name="Template overlay")
    friendly_name = models.CharField(max_length=64, default='', blank=True, verbose_name='Friendly name')
    contexts = models.ManyToManyField(MemeContext, blank=True, verbose_name='Contexts')
    bg_color = ColorField(default='', blank=True, verbose_name='Background color')
    accepted = models.BooleanField(default=False, verbose_name='Accepted')
    add_date = models.DateTimeField(default=timezone.now, verbose_name='Date added')
    change_date = models.DateTimeField(default=timezone.now, verbose_name='Last changed')
    meme_count = models.IntegerField(default=0, verbose_name='Memes')

    def clean(self):
        if not self.bg_image_file and not self.image_file:
            raise ValidationError('Please upload a template background and/or overlay image')
        if self.bg_image_file and self.image_file and (self.bg_image_file.width != self.image_file.width or self.bg_image_file.height != self.image_file.height):
            raise ValidationError('The background and overlay images have to have the same dimensions')
        self.change_date = timezone.now()
        self.save()

    # add image to queues of all its contexts
    def enqueue(self):
        query = ImageInContext.objects.filter(image_name=self.name, image_type=ImageInContext.IMAGE_TYPE_TEMPLATE)
        for imq in query:
            imq.delete()
        if self.accepted:
            contexts = self.contexts.all()
            if len(contexts) == 0:
                contexts = MemeContext.objects.all()
            for c in contexts:
                ImageInContext.objects.create(image_name=self.name, image_type=ImageInContext.IMAGE_TYPE_TEMPLATE,
                                              context_link=c)

    def _add_meem(self):
        self.meme_count += 1
        self.save()

    @classmethod
    def count(cls, context):
        return cls.by_context(context).count()

    @classmethod
    def by_context(cls, context):
        return cls.objects.filter(Q(contexts=context) | Q(contexts=None)).filter(accepted=True)

    @classmethod
    def find(cls, name, allow_disabled=False):
        if isinstance(name, MemeContext):
            # find the last meme generated in that context and return the template that was used
            found = Meem.objects.filter(context_link=name).order_by('-gen_date').first()
            return found and found.template_link

        # find template by string
        obj = cls.objects
        if not allow_disabled:
            obj = obj.filter(accepted=True)
        found = \
            obj.filter(name__iexact=name).first() or \
            obj.filter(friendly_name__iexact=name).first() or \
            obj.filter(name__istartswith=name).first() or \
            obj.filter(friendly_name__istartswith=name).first() or \
            obj.filter(name__icontains=name).first() or \
            obj.filter(friendly_name__icontains=name).first()
        if found is not None:
            return found
        name_words = re.split('[ ./]', name)
        found = \
            obj.filter(reduce(operator.and_, (Q(name__icontains=x) for x in name_words))).first() or \
            obj.filter(reduce(operator.and_, (Q(friendly_name__icontains=x) for x in name_words))).first()
        return found

    def get_preview_url(self):
        return self.pk and reverse('memeviewer:template_preview_view', kwargs={'template_name': self.name}) or ''

    def get_image_url(self):
        return self.image_file and self.image_file.url or ''

    def get_bgimage_url(self):
        return self.bg_image_file and self.bg_image_file.url or ''

    def contexts_string(self):
        contexts = self.contexts.all()
        if contexts.count() == 0:
            return "*"
        result = ""
        for context in contexts:
            result += "{} ".format(context.short_name)
        return result.strip()

    def __str__(self):
        return self.friendly_name or self.name


class MemeTemplateSlot(models.Model):

    class Meta:
        verbose_name = "Template slot"

    template = models.ForeignKey(MemeTemplate, on_delete=models.CASCADE, verbose_name='Template')
    slot_order = models.IntegerField(verbose_name='Slot flavor', choices=tuple(zip(
        range(0, 12),
        ["Blue", "Yellow", "Green", "Red", "Cyan", "Orange", "Lime", "Pink", "Purple", "Brown", "Black", "White"]
    )))
    x = models.IntegerField()
    y = models.IntegerField()
    w = models.PositiveIntegerField()
    h = models.PositiveIntegerField()
    rotate = models.IntegerField(default=0, verbose_name='Rotation')
    blur = models.BooleanField(default=False, verbose_name='Blur')
    grayscale = models.BooleanField(default=False, verbose_name='Grayscale')
    cover = models.BooleanField(default=False, verbose_name='Cover')

    def __str__(self):
        return "{0} - slot ({1}, {2})".format(self.template, self.x, self.y)

    @classmethod
    def get(cls, template, slot_order):
        return cls.objects.get(template=template, slot_order=slot_order)


# noinspection PyProtectedMember
class Meem(models.Model):

    class Meta:
        verbose_name = "Meme"

    number = models.IntegerField(default=next_meme_number, unique=True, verbose_name='Number')
    meme_id = models.CharField(primary_key=True, max_length=36, default=struuid4, verbose_name='ID')
    template_link = models.ForeignKey(MemeTemplate, verbose_name='Template', on_delete=models.SET_NULL, null=True)
    context_link = models.ForeignKey(MemeContext, verbose_name='Context', on_delete=models.SET_DEFAULT, default='default')
    gen_date = models.DateTimeField(default=timezone.now, verbose_name='Date generated')
    source_images = models.TextField(verbose_name='Source images')

    @classmethod
    def generate(cls, context, template=None, saveme=True):
        if MemeTemplate.count(context) == 0:
            raise FileNotFoundError("No templates")
        if MemeSourceImage.count(context) == 0:
            raise FileNotFoundError("No source images")
        if template is None:
            template = context.next_template()
        template._add_meem()
        source_files = {}
        prev_slot_id = None
        source_file = None
        for slot in template.memetemplateslot_set.order_by('slot_order').all():
            if slot.slot_order == prev_slot_id:
                source_files[slot] = source_file
                continue
            # pick source file that hasn't been used
            while True:
                source_file = context.next_sourceimg()
                if source_file not in source_files.values():
                    break
            source_files[slot.slot_order] = source_file.name
            source_file._add_meem()
            prev_slot_id = slot.slot_order
        meem = cls(template_link=template, context_link=context, source_images=json.dumps(source_files))
        if saveme:
            meem.save()
        return meem

    def get_sourceimgs_in_slots(self):
        rawimgs = json.loads(self.source_images)
        imgs = {}
        for slot in self.template_link.memetemplateslot_set.all():
            imgs[slot] = MemeSourceImage.by_id(rawimgs[str(slot.slot_order)])
        return imgs

    def get_sourceimgs(self):
        return list(map(lambda x: MemeSourceImage.by_id(x[1]), json.loads(self.source_images).items()))

    def get_local_path(self):
        return os.path.join(config.MEDIA_ROOT, config.MEDIA_SUBDIR, 'memes', self.meme_id + '.jpg')

    def get_url(self):
        return config.MEDIA_URL + config.MEDIA_SUBDIR + '/memes/' + self.meme_id + '.jpg'

    def get_info_url(self):
        return config.WEBSITE_URL + 'meme/' + self.meme_id

    def get_admin_link(self):
        return object_url(Meem, self.meme_id, 'Admin')

    def __str__(self):
        return str(self.number)


class ImageInContext(models.Model):
    IMAGE_TYPE_TEMPLATE = 0
    IMAGE_TYPE_SOURCEIMG = 1
    image_type = models.IntegerField()
    image_name = models.CharField(max_length=256)
    context_link = models.ForeignKey(MemeContext, on_delete=models.CASCADE)
