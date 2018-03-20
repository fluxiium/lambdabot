import imghdr
import operator
import os
import re
import uuid
from django.contrib.contenttypes.models import ContentType
from django.core.files import File

from functools import reduce
from PIL import Image
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from lamdabotweb.settings import WEBSITE_URL, IMG_QUEUE_LENGTH, MAX_SRCIMG_SIZE, MEDIA_SUBDIR, MEDIA_URL, MEDIA_ROOT


def struuid4():
    return str(uuid.uuid4())


def next_meme_number():
    return (Meem.objects.all().aggregate(largest=models.Max('number'))['largest'] or 0) + 1


def next_image(context, image_type):
    # read queue from db
    result = ImageInContext.objects.filter(image_type=image_type, context_link=context)
    objects = MemeSourceImage.objects if image_type == ImageInContext.IMAGE_TYPE_SOURCEIMG else MemeTemplate.objects

    # if empty, make new queue
    if result.count() == 0:

        queue_length = IMG_QUEUE_LENGTH
        img_queue = objects.filter(accepted=True).filter(Q(contexts=context) | Q(contexts=None))\
            .order_by('?')[0:(min(queue_length, objects.count()))]

        # save queue to db
        for s in img_queue:
            img_in_context = ImageInContext(image_name=s.name, image_type=image_type, context_link=context)
            img_in_context.save()

        result = ImageInContext.objects.filter(image_type=image_type, context_link=context)

    img_in_context = result.first()
    sourceimg = img_in_context.image_name
    img_in_context.delete()

    img_obj = objects.filter(name=sourceimg, accepted=True).filter(Q(contexts=context) | Q(contexts=None)).first()

    if img_obj is None:
        return next_image(context, image_type)
    elif not img_obj.image_file:
        raise FileNotFoundError("Image file not found")
    else:
        return img_obj


def next_template(context):
    return next_image(context, ImageInContext.IMAGE_TYPE_TEMPLATE)


def next_sourceimg(context):
    return next_image(context, ImageInContext.IMAGE_TYPE_SOURCEIMG)


# MODELS --------------------------------------------------------------------------------------------------------

class MemeContext(models.Model):

    class Meta:
        verbose_name = "Context"

    short_name = models.CharField(max_length=32, primary_key=True, verbose_name='ID')
    name = models.CharField(max_length=64, verbose_name='Name')

    @classmethod
    def by_id(cls, name):
        return cls.objects.get(short_name=name)

    @classmethod
    def by_id_or_create(cls, name, friendly_name):
        context = cls.objects.filter(short_name=name).first()
        if context is not None:
            return context
        context = cls.objects.create(short_name=name, name=friendly_name)
        return context

    def get_reset_url(self):
        return reverse('memeviewer:context_reset_view', kwargs={'context': self.short_name})

    def __str__(self):
        return self.short_name


class MemeSourceImage(models.Model):

    class Meta:
        verbose_name = "Source image"

    name = models.CharField(max_length=256, primary_key=True, verbose_name='Unique ID', default=struuid4)
    image_file = models.ImageField(upload_to=MEDIA_SUBDIR + '/sourceimg/', max_length=256)
    friendly_name = models.CharField(max_length=64, default='', blank=True, verbose_name='Friendly name')
    contexts = models.ManyToManyField(MemeContext, blank=True, verbose_name='Contexts')
    accepted = models.BooleanField(default=False, verbose_name='Accepted')
    add_date = models.DateTimeField(default=timezone.now, verbose_name='Date added')

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

    @classmethod
    def submit(cls, filepath, filename=None, friendly_name=None):
        try:
            image = Image.open(filepath)
        except OSError:
            return None

        imgid = struuid4()
        saved_filename = "{0}.{1}".format(imgid, imghdr.what(filepath))

        stat = os.stat(filepath)
        if stat.st_size > MAX_SRCIMG_SIZE and image.mode == "RGBA":
            image = image.convert('RGB')
            saved_filename += ".jpeg"
            filepath += ".jpeg"
            image.save(filepath)
            stat = os.stat(filepath)

        if stat.st_size > MAX_SRCIMG_SIZE:
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

    def get_admin_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return reverse("admin:%s_%s_change" % (content_type.app_label, content_type.model), args=(self.name,))

    def get_memes_admin_url(self):
        content_type = ContentType.objects.get_for_model(Meem)
        content_type2 = ContentType.objects.get_for_model(MemeSourceImageInSlot)
        return reverse("admin:%s_%s_changelist" % (content_type.app_label, content_type.model)) + \
            ("?%s__source_image__name__exact=" % content_type2.model) + self.name


class MemeTemplate(models.Model):

    class Meta:
        verbose_name = "Template"

    name = models.CharField(max_length=64, primary_key=True, verbose_name='Unique ID', default=struuid4)
    bg_image_file = models.ImageField(upload_to=MEDIA_SUBDIR + '/templates/', max_length=256, null=True, default=None, blank=True)
    image_file = models.ImageField(upload_to=MEDIA_SUBDIR + '/templates/', max_length=256, null=True, default=None, blank=True)
    friendly_name = models.CharField(max_length=64, default='', blank=True, verbose_name='Friendly name')
    contexts = models.ManyToManyField(MemeContext, blank=True, verbose_name='Contexts')
    bg_color = models.CharField(max_length=16, default='', blank=True, verbose_name='Background color')
    accepted = models.BooleanField(default=False, verbose_name='Accepted')
    add_date = models.DateTimeField(default=timezone.now, verbose_name='Date added')

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
        found = obj.filter(name__iexact=name).first()
        if found is not None:
            return found
        found = obj.filter(friendly_name__iexact=name).first()
        if found is not None:
            return found
        found = obj.filter(name__istartswith=name).first()
        if found is not None:
            return found
        found = obj.filter(friendly_name__istartswith=name).first()
        if found is not None:
            return found
        found = obj.filter(name__icontains=name).first()
        if found is not None:
            return found
        found = obj.filter(friendly_name__icontains=name).first()
        if found is not None:
            return found
        name_words = re.split(' |\.|/', name)
        found = obj.filter(reduce(operator.and_, (Q(name__icontains=x) for x in name_words))).first()
        if found is not None:
            return found
        found = obj.filter(reduce(operator.and_, (Q(friendly_name__icontains=x) for x in name_words))).first()
        return found

    def possible_combinations(self, context):
        possible = 1
        slots = MemeTemplateSlot.objects.filter(template=self)
        srcimgs = MemeSourceImage.count(context)
        prev_slot_id = None
        for slot in slots:
            if slot.slot_order == prev_slot_id:
                continue
            possible *= srcimgs
            srcimgs -= 1
        return possible

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

    def get_admin_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return reverse("admin:%s_%s_change" % (content_type.app_label, content_type.model), args=(self.name,))

    def get_memes_admin_url(self):
        content_type = ContentType.objects.get_for_model(Meem)
        return reverse("admin:%s_%s_changelist" % (content_type.app_label, content_type.model)) + \
            "?template_link__name__exact=" + self.name


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
    template_link = models.ForeignKey(MemeTemplate, verbose_name='Template', on_delete=models.CASCADE)
    context_link = models.ForeignKey(MemeContext, verbose_name='Context', on_delete=models.CASCADE)
    gen_date = models.DateTimeField(default=timezone.now, verbose_name='Date generated')

    @classmethod
    def create(cls, template, sourceimgs, context):
        meem = cls(template_link=template, context_link=context)
        meem.save()
        for slot, sourceimg in sourceimgs.items():
            MemeSourceImageInSlot(meme=meem, slot=slot, source_image=sourceimg).save()
        return meem

    @classmethod
    def generate(cls, context, template=None):
        if MemeTemplate.count(context) == 0:
            raise FileNotFoundError("Please upload some templates first")
        if MemeSourceImage.count(context) == 0:
            raise FileNotFoundError("Please upload some source images first")
        if template is None:
            template = next_template(context)
        source_files = {}
        prev_slot_id = None
        source_file = None
        for slot in template.memetemplateslot_set.order_by('slot_order').all():
            if slot.slot_order == prev_slot_id:
                source_files[slot] = source_file
                continue
            # pick source file that hasn't been used
            while True:
                source_file = next_sourceimg(context)
                if source_file not in source_files.values():
                    break
            source_files[slot] = source_file
            prev_slot_id = slot.slot_order
        meem = cls.create(template, source_files, context)
        return meem

    @classmethod
    def possible_combinations(cls, context):
        possible = 0
        for template in MemeTemplate.by_context(context):
            possible += template.possible_combinations(context)
        return possible

    def get_sourceimgs_in_slots(self):
        return MemeSourceImageInSlot.objects.filter(meme=self).order_by('slot__slot_order')

    def get_local_path(self):
        return os.path.join(MEDIA_ROOT, MEDIA_SUBDIR, 'memes', self.meme_id + '.jpg')

    def get_url(self):
        return MEDIA_URL + MEDIA_SUBDIR + '/memes/' + self.meme_id + '.jpg'

    def get_info_url(self):
        return WEBSITE_URL + 'meme/' + self.meme_id

    def __str__(self):
        return "{0} - #{1}, {2}".format(self.meme_id, self.number, self.gen_date)

    def get_admin_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return reverse("admin:%s_%s_change" % (content_type.app_label, content_type.model), args=(self.meme_id,))


class MemeSourceImageInSlot(models.Model):

    class Meta:
        verbose_name = "Source image in slot"

    meme = models.ForeignKey(Meem, verbose_name="Meme", on_delete=models.CASCADE)
    slot = models.ForeignKey(MemeTemplateSlot, verbose_name="Template slot", on_delete=models.CASCADE)
    source_image = models.ForeignKey(MemeSourceImage, verbose_name="Source image", on_delete=models.CASCADE)


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
    image_name = models.CharField(max_length=256, verbose_name='Unique ID')
    context_link = models.ForeignKey(MemeContext, on_delete=models.CASCADE, verbose_name='Context')

    def __str__(self):
        return "{0} - {1} ({2})"\
            .format(self.image_name, self.context_link.short_name, self.IMAGE_TYPE_CHOICES[self.image_type][1])
