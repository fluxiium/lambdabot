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
        indexes = [
            models.Index(fields=['meme_count'], name='idx_context_mcount')
        ]

    short_name = models.CharField(max_length=32, primary_key=True, verbose_name='ID')
    name = models.CharField(max_length=64, verbose_name='Name')
    recent_threshold = models.IntegerField(default=10, verbose_name='Recent threshold')
    is_public = models.BooleanField(default=False, verbose_name='Is public?')

    @classmethod
    def by_id(cls, name):
        return cls.objects.get(short_name=name)

    @classmethod
    def by_id_or_create(cls, name, friendly_name, is_public=False):
        context, _ = cls.objects.get_or_create(short_name=name, defaults={'name': friendly_name, 'is_public': is_public})
        return context

    def get_reset_url(self):
        return reverse('memeviewer:context_reset_view', kwargs={'context': self.short_name})

    def next_image(self, image_class, increment_counter=True):
        in_context_class = image_class.in_context_class

        # read queue from db
        result = in_context_class.objects.filter(context=self, queued=True)

        # if empty, make new queue
        if result.count() == 0:

            for i in image_class.objects.filter(accepted=True).filter(Q(contexts=self) | Q(contexts=None)):
                in_context_class.objects.get_or_create(context=self, image=i)

            queue_length = config.IMG_QUEUE_LENGTH
            recent_threshold = self.recent_threshold

            img_queue_db = in_context_class.objects.filter(context=self, image__accepted=True).order_by('?')
            img_queue_recent = img_queue_db.filter(random_usages__lte=recent_threshold)[
                               0:(min(queue_length, img_queue_db.count()) / 2)]
            img_queue_old = img_queue_db[0:(min(queue_length, img_queue_db.count()) - img_queue_recent.count())]

            queue_list = list(img_queue_recent) + list(img_queue_old)

            if len(queue_list) == 0:
                raise FileNotFoundError("No images found")

            # save queue to db
            for s in queue_list:
                s.queued = True
                s.save()

            result = in_context_class.objects.filter(context=self, queued=True)

        img_in_context = result.order_by('?').first()
        img_in_context.queued = False
        if increment_counter:
            img_in_context.random_usages += 1
            img_in_context.all_usages += 1
        img_in_context.save()

        return img_in_context.image

    # noinspection PyProtectedMember
    def generate(self, template=None, saveme=True):
        if template is None:
            template = self.next_image(MemeTemplate, saveme)
        source_files = {}
        prev_slot_id = None
        source_file = None
        for slot in template.memetemplateslot_set.order_by('slot_order').all():
            if slot.slot_order == prev_slot_id:
                source_files[slot] = source_file
                continue
            # pick source file that hasn't been used
            while True:
                source_file = self.next_image(MemeSourceImage, saveme)
                if source_file not in source_files.values():
                    break
            source_files[slot.slot_order] = source_file.name
            prev_slot_id = slot.slot_order
        print(source_files)
        meem = Meem(template_link=template, context_link=self, source_images=json.dumps(source_files))
        if saveme:
            meem.save()
        return meem

    def __str__(self):
        return self.short_name
    

# noinspection PyTypeChecker
class MemeImage(models.Model):

    class Meta:
        abstract = True

    in_context_class = None

    name = models.CharField(max_length=256, primary_key=True, verbose_name='Unique ID', default=struuid4)
    friendly_name = models.CharField(max_length=64, default='', blank=True, verbose_name='Friendly name')
    contexts = models.ManyToManyField(MemeContext, blank=True, verbose_name='Contexts')
    accepted = models.BooleanField(default=False, verbose_name='Accepted')
    add_date = models.DateTimeField(default=timezone.now, verbose_name='Date added')
    change_date = models.DateTimeField(default=timezone.now, verbose_name='Last changed')

    def clean(self):
        self.change_date = timezone.now()
        self.save()

    # add image to queues of all its contexts (or unqueue it if it's not accepted)
    def reindex(self):
        if self.accepted:
            contexts = self.contexts.all()
            if len(contexts) == 0:
                contexts = MemeContext.objects.all()
            for c in contexts:
                self.in_context_class.objects.get_or_create(context=c, image=self)
        else:
            for im in self.in_context_class.objects.filter(image=self, queued=True):
                im.queued = False
                im.save()

    def __str__(self):
        return self.friendly_name or self.name

    @classmethod
    def by_id(cls, name):
        return cls.objects.get(name=name)


class MemeImageInContext(models.Model):
    class Meta:
        abstract = True
        unique_together = ('image', 'context')
        indexes = [
            models.Index(fields=['context', 'random_usages'])
        ]

    image = None
    context = models.ForeignKey(MemeContext, on_delete=models.CASCADE)
    queued = models.BooleanField(default=False)
    random_usages = models.IntegerField(default=0)

    @classmethod
    def count(cls, context):
        return cls.objects.filter(context=context).count()

    def __str__(self):
        return "{} ({})".format(self.image, self.context)


class MemeSourceImage(MemeImage):

    class Meta:
        verbose_name = "Source image"
        indexes = [
            models.Index(fields=['friendly_name'], name='idx_srcimg_fname'),
            models.Index(fields=['add_date'], name='idx_srcimg_adddate'),
            models.Index(fields=['change_date'], name='idx_srcimg_chdate'),
            models.Index(fields=['meme_count'], name='idx_srcimg_mcount'),
        ]

    image_file = models.ImageField(upload_to=config.MEDIA_SUBDIR + '/sourceimg/', max_length=256)

    def get_image_url(self):
        return self.image_file and self.image_file.url or''

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


class MemeSourceImageInContext(MemeImageInContext):
    image = models.ForeignKey(MemeSourceImage, on_delete=models.CASCADE)


MemeSourceImage.in_context_class = MemeSourceImageInContext


class MemeTemplate(MemeImage):

    class Meta:
        verbose_name = "Template"
        indexes = [
            models.Index(fields=['friendly_name'], name='idx_template_fname'),
            models.Index(fields=['add_date'], name='idx_template_adddate'),
            models.Index(fields=['change_date'], name='idx_template_chdate'),
            models.Index(fields=['meme_count'], name='idx_template_mcount'),
        ]

    bg_image_file = models.ImageField(upload_to=config.MEDIA_SUBDIR + '/templates/', max_length=256, null=True, default=None,
                                      blank=True, verbose_name="Template background")
    image_file = models.ImageField(upload_to=config.MEDIA_SUBDIR + '/templates/', max_length=256, null=True, default=None,
                                   blank=True, verbose_name="Template overlay")
    bg_color = ColorField(default='', blank=True, verbose_name='Background color')

    def clean(self):
        if not self.bg_image_file and not self.image_file:
            raise ValidationError('Please upload a template background and/or overlay image')
        if self.bg_image_file and self.image_file and (self.bg_image_file.width != self.image_file.width or self.bg_image_file.height != self.image_file.height):
            raise ValidationError('The background and overlay images have to have the same dimensions')
        super(MemeTemplate, self).clean()

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


class MemeTemplateInContext(MemeImageInContext):
    image = models.ForeignKey(MemeTemplate, on_delete=models.CASCADE)


MemeTemplate.in_context_class = MemeTemplateInContext


class MemeTemplateSlot(models.Model):

    class Meta:
        verbose_name = "Template slot"
        indexes = [
            models.Index(fields=['template', 'slot_order'], name='idx_template_slot')
        ]

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
        ordering = ['-number']
        indexes = [
            models.Index(fields=['number'], name='idx_meme_number'),
            models.Index(fields=['gen_date'], name='idx_meme_gendate'),
        ]

    number = models.IntegerField(default=next_meme_number, unique=True, verbose_name='Number')
    meme_id = models.CharField(primary_key=True, max_length=36, default=struuid4, verbose_name='ID')
    template_link = models.ForeignKey(MemeTemplate, verbose_name='Template', on_delete=models.SET_NULL, null=True)
    context_link = models.ForeignKey(MemeContext, verbose_name='Context', on_delete=models.SET_DEFAULT, default='default')
    gen_date = models.DateTimeField(default=timezone.now, verbose_name='Date generated')
    source_images = models.TextField(verbose_name='Source images')

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
