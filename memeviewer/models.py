import json
import operator
import os
import re
import config
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.files import File
from functools import reduce
from django.db import models, transaction
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from colorfield.fields import ColorField
from PIL import Image
from PIL import ImageFilter
from util import struuid4
from util.admin_utils import object_url


def next_meme_number():
    return (Meem.objects.all().aggregate(largest=models.Max('number'))['largest'] or 0) + 1


IMAGE_TYPE_SRCIMG = 0
IMAGE_TYPE_TEMPLATE = 1
IMAGE_TYPES = (
    (0, 'Source image'),
    (1, 'Template')
)

class MemeGeneratorException(Exception):
    pass

class NotEnoughImages(MemeGeneratorException):
    pass


class MemeImagePool(models.Model):
    class Meta:
        verbose_name = 'Image pool'
        indexes = [models.Index(fields=['name'], name='idx_imgpool')]
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class MemeImage(models.Model):

    class Meta:
        abstract = True

    in_context_class = None

    name = models.CharField(max_length=256, primary_key=True, verbose_name='Unique ID', default=struuid4)
    friendly_name = models.CharField(max_length=64, default='', blank=True)
    image_pool = models.ForeignKey(MemeImagePool, on_delete=models.CASCADE)
    accepted = models.NullBooleanField(default=None, blank=True, null=True)
    add_date = models.DateTimeField(default=timezone.now, verbose_name='Date added')
    change_date = models.DateTimeField(default=timezone.now, verbose_name='Last changed')
    random_usages = models.IntegerField(default=0)
    image_type = None

    def clean(self):
        self.change_date = timezone.now()
        self.save()

    @transaction.atomic
    def enqueue(self, queue_id):
        if self.accepted:
            QueuedMemeImage.objects.get_or_create(name=self.name, image_type=self.image_type, queue_id=queue_id)
        else:
            QueuedMemeImage.objects.filter(name=self.name, image_type=self.image_type, queue_id=queue_id).delete()

    def __str__(self):
        return self.friendly_name or self.name

    def inc_counter(self):
        self.random_usages += 1
        self.save()

    @classmethod
    @transaction.atomic
    def next(cls, image_pools, queue_id):
        image_type = cls.image_type

        # read queue from db
        result = QueuedMemeImage.objects.filter(image_type=image_type, queue_id=queue_id)

        # if empty, make new queue
        if result.count() == 0:

            queue_length = config.IMG_QUEUE_LENGTH
            recent_threshold = config.RECENT_THRESHOLD

            img_queue_db = cls.objects.filter(accepted=True).filter(image_pool__in=image_pools).order_by('?')
            img_count = min(queue_length, img_queue_db.count())
            img_queue_recent = img_queue_db.filter(random_usages__lte=recent_threshold)[0:(img_count / 2)]
            img_queue_any = img_queue_db[0:(img_count - img_queue_recent.count())]

            queue_list = list(img_queue_recent) + list(img_queue_any)

            if len(queue_list) == 0:
                raise NotEnoughImages('No images found')

            # save queue to db
            for s in queue_list:
                QueuedMemeImage.objects.create(image_type=image_type, queue_id=queue_id, name=s.name)

            result = QueuedMemeImage.objects.filter(image_type=image_type, queue_id=queue_id)

        queued_image = result.first()
        try:
            image = cls.objects.get(name=queued_image.name)
        except cls.DoesNotExist:
            image = None
        queued_image.delete()
        return image or cls(image_type, image_pools, queue_id)


class QueuedMemeImage(models.Model):
    name = models.CharField(max_length=256)
    image_type = models.IntegerField(choices=IMAGE_TYPES)
    queue_id = models.CharField(max_length=128)


class MemeSourceImage(MemeImage):

    class Meta:
        verbose_name = "Source image"
        indexes = [
            models.Index(fields=['friendly_name'], name='idx_srcimg_fname'),
            models.Index(fields=['add_date'], name='idx_srcimg_adddate'),
            models.Index(fields=['change_date'], name='idx_srcimg_chdate'),
            models.Index(fields=['random_usages'], name='idx_srcimg_usages'),
        ]

    image_file = models.ImageField(upload_to='sourceimg/', max_length=256)
    image_type = IMAGE_TYPE_SRCIMG

    @property
    def image_url(self):
        return self.image_file and self.image_file.url or''

    @classmethod
    @transaction.atomic
    def submit(cls, image_pool, filepath, filename=None, friendly_name=None):
        imgid = struuid4()
        saved_filename = imgid + filename
        if friendly_name is None:
            friendly_name = filename and os.path.splitext(filename.replace('_', ' ').rstrip())[0][:32] or ''
        srcimg = MemeSourceImage(image_pool=image_pool, name=imgid, friendly_name=friendly_name)
        srcimg.image_file.save(saved_filename, File(open(filepath, "rb")))
        srcimg.save()
        return srcimg


class MemeTemplate(MemeImage):

    class Meta:
        verbose_name = "Template"
        indexes = [
            models.Index(fields=['friendly_name'], name='idx_template_fname'),
            models.Index(fields=['add_date'], name='idx_template_adddate'),
            models.Index(fields=['change_date'], name='idx_template_chdate'),
            models.Index(fields=['random_usages'], name='idx_template_usages'),
        ]

    bg_image_file = models.ImageField(upload_to='templates/', max_length=256, null=True, default=None,
                                      blank=True, verbose_name="Background")
    image_file = models.ImageField(upload_to='templates/', max_length=256, null=True, default=None,
                                   blank=True, verbose_name="Overlay")
    bg_color = ColorField(default='', blank=True, verbose_name='Background color')
    image_type = IMAGE_TYPE_TEMPLATE

    def clean(self):
        if not self.bg_image_file and not self.image_file:
            raise ValidationError('Please upload a template background and/or overlay image')
        if self.bg_image_file and self.image_file and (self.bg_image_file.width != self.image_file.width or self.bg_image_file.height != self.image_file.height):
            raise ValidationError('The background and overlay images have to have the same dimensions')
        super(MemeTemplate, self).clean()

    @classmethod
    def find(cls, image_pools=None, name=None, allow_disabled=False):
        obj = cls.objects
        if not allow_disabled:
            obj = obj.filter(accepted=True)
        if image_pools is not None:
            obj = obj.filter(image_pool__in=image_pools)
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

    def slot(self, slot_id):
        return MemeTemplateSlot.objects.filter(template=self, slot_order=slot_id)

    @property
    def preview_url(self):
        return self.pk and reverse('memeviewer:template_preview_view', kwargs={'template_name': self.name}) or ''

    @property
    def image_url(self):
        return self.image_file and self.image_file.url or ''

    @property
    def bgimage_url(self):
        return self.bg_image_file and self.bg_image_file.url or ''


class MemeTemplateSlot(models.Model):

    class Meta:
        verbose_name = "Template slot"
        indexes = [
            models.Index(fields=['template', 'slot_order'], name='idx_template_slot')
        ]

    template = models.ForeignKey(MemeTemplate, on_delete=models.CASCADE)
    slot_order = models.IntegerField(verbose_name='Slot group', choices=tuple(zip(
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


# noinspection PyProtectedMember
class Meem(models.Model):

    class Meta:
        verbose_name = "Meme"
        ordering = ['-number']
        indexes = [
            models.Index(fields=['number'], name='idx_meme_number'),
            models.Index(fields=['gen_date'], name='idx_meme_gendate'),
        ]

    number = models.IntegerField(default=next_meme_number, unique=True)
    meme_id = models.CharField(primary_key=True, max_length=36, default=struuid4, verbose_name='ID')
    template_link = models.ForeignKey(MemeTemplate, verbose_name='Template', on_delete=models.SET_NULL, null=True)
    gen_date = models.DateTimeField(default=timezone.now, verbose_name='Date generated')
    source_images = models.TextField()

    @classmethod
    @transaction.atomic
    def generate(cls, image_pools, queue_id, template=None, saveme=True):
        if template is None:
            templ = MemeTemplate.next(image_pools, queue_id)
        else:
            templ = template
        source_files = {}
        prev_slot_id = None
        source_file = None
        for slot in templ.memetemplateslot_set.order_by('slot_order').all():
            if slot.slot_order == prev_slot_id:
                source_files[slot.slot_order] = source_file.name
                continue
            # pick source file that hasn't been used
            attempts = 0
            while True:
                source_file = MemeSourceImage.next(image_pools, queue_id)
                if source_file.name not in source_files.values():
                    break
                else:
                    attempts += 1
                if attempts > 5:
                    raise NotEnoughImages('Not enough source images for template ' + templ.name)
            source_files[slot.slot_order] = source_file.name
            if saveme:
                source_file.inc_counter()
            prev_slot_id = slot.slot_order
        meem = Meem(template_link=templ, source_images=json.dumps(source_files))
        if saveme:
            if template is None:
                templ.inc_counter()
            meem.save()
        return meem

    @property
    def sourceimgs_in_slots(self):
        rawimgs = json.loads(self.source_images)
        imgs = {}
        for slot in self.template_link.memetemplateslot_set.all():
            imgs[slot] = MemeSourceImage.objects.get(name=rawimgs[str(slot.slot_order)])
        return imgs

    @property
    def sourceimgs(self):
        return list(map(lambda x: MemeSourceImage.objects.get(name=x[1]), json.loads(self.source_images).items()))

    @property
    def local_path(self):
        return os.path.join(config.MEDIA_ROOT, 'memes', self.meme_id + '.jpg')

    @property
    def url(self):
        return config.MEDIA_URL + 'memes/' + self.meme_id + '.jpg'

    @property
    def info_url(self):
        return config.WEBSITE_URL + 'meme/' + self.meme_id

    @property
    def admin_link(self):
        return object_url(Meem, self.meme_id, 'Admin')

    def __str__(self):
        return str(self.number)

    def make_img(self, saveme=True):
        if os.path.isfile(self.local_path):
            return Image.open(self.local_path)

        foreground, background = None, None

        if self.template_link.image_file:
            foreground = Image.open(self.template_link.image_file).convert("RGBA")

        if self.template_link.bg_image_file:
            background = Image.open(self.template_link.bg_image_file).convert('RGBA')

        if not foreground and not background:
            raise AttributeError("Template has no background or overlay file")

        background_color = Image.new('RGBA', (foreground or background).size, self.template_link.bg_color or '#000000')

        if background is None:
            background = background_color

        for slot, sourceimg in self.sourceimgs_in_slots.items():

            source_image_original = Image.open(sourceimg.image_file).convert("RGBA")

            # resize, crop, and rotate source image
            source_image = source_image_original.copy()

            if slot.cover:
                resize_ratio = max(slot.w / source_image.size[0], slot.h / source_image.size[1])
            else:
                resize_ratio = min(slot.w / source_image.size[0], slot.h / source_image.size[1])

            source_image = source_image.resize(
                [int(source_image.size[0] * resize_ratio), int(source_image.size[1] * resize_ratio)], Image.ANTIALIAS)

            if slot.cover:
                source_image = source_image.crop((
                    (source_image.size[0] - slot.w) / 2,
                    (source_image.size[1] - slot.h) / 2,
                    (source_image.size[0] + slot.w) / 2,
                    (source_image.size[1] + slot.h) / 2,
                ))

            if slot.rotate != 0:
                source_image = source_image.rotate(slot.rotate, resample=Image.BICUBIC, expand=True)

            # get info for pasting
            source_alpha = source_image.copy()
            paste_pos = (
                int(slot.x + (slot.w - source_image.size[0]) / 2),
                int(slot.y + (slot.h - source_image.size[1]) / 2),
            )

            # apply effects
            if slot.blur:
                source_image = source_image.filter(ImageFilter.GaussianBlur(3))

            if slot.grayscale:
                source_image = source_image.convert('LA')

            background.paste(source_image, paste_pos, source_alpha)

        if foreground:
            meme_image = Image.alpha_composite(background_color, Image.alpha_composite(background, foreground))
        else:
            meme_image = Image.alpha_composite(background_color, background)

        meme_image = meme_image.convert('RGB')
        if saveme:
            meme_image.save(self.local_path)
        return meme_image
