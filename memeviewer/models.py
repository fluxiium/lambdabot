import imghdr
import operator
import os
import re
import uuid

from functools import reduce
from PIL import Image
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from lamdabotweb.settings import MEMES_DIR, WEBSITE_URL, SOURCEIMG_DIR, TEMPLATE_DIR, TEMPLATE_URL, SOURCEIMG_URL, \
    MEMES_URL, IMG_QUEUE_LENGTH, MAX_SRCIMG_SIZE


def struuid4():
    return str(uuid.uuid4())


def next_meme_number():
    return (Meem.objects.all().aggregate(largest=models.Max('number'))['largest'] or 0) + 1


def next_image(context, image_type):
    # read queue from db
    result = ImageInContext.objects.filter(image_type=image_type, context_link=context)
    objects = MemeSourceImage.objects if image_type == ImageInContext.IMAGE_TYPE_SOURCEIMG else MemeTemplate.objects
    imagedir = SOURCEIMG_DIR if image_type == ImageInContext.IMAGE_TYPE_SOURCEIMG else TEMPLATE_DIR

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
    elif not os.path.isfile(os.path.join(imagedir, sourceimg)):
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

    context_id = models.CharField(max_length=32, primary_key=True, verbose_name='ID')
    name = models.CharField(max_length=64, verbose_name='Name')

    @classmethod
    def by_id(cls, name):
        return cls.objects.get(context_id=name)

    @classmethod
    def by_id_or_create(cls, name, friendly_name):
        context = cls.objects.filter(context_id=name).first()
        if context is not None:
            return context
        context = cls.objects.create(context_id=name, name=friendly_name)
        return context

    def get_reset_url(self):
        return reverse('memeviewer:context_reset_view', kwargs={'context': self.context_id})

    def __str__(self):
        return self.name


class MemeSourceImage(models.Model):

    class Meta:
        verbose_name = "Source image"

    name = models.CharField(max_length=256, primary_key=True, verbose_name='File name')
    friendly_name = models.CharField(max_length=64, default='', blank=True, verbose_name='Friendly name')
    contexts = models.ManyToManyField(MemeContext, blank=True, verbose_name='Contexts')
    accepted = models.BooleanField(default=False, verbose_name='Accepted')
    add_date = models.DateTimeField(default=timezone.now, verbose_name='Date added')

    def get_image_url(self):
        return SOURCEIMG_URL + self.name

    def __str__(self):
        return self.friendly_name or self.name

    def contexts_string(self):
        contexts = self.contexts.all()
        if contexts.count() == 0:
            return "*"
        result = ""
        for context in contexts:
            result += context.context_id + " "
        return result.strip()

    @classmethod
    def submit(cls, original_filename, filename=None):
        try:
            image = Image.open(original_filename)
        except OSError:
            return None

        if filename is None:
            filename = "{0}.{1}".format(str(uuid.uuid4()), imghdr.what(original_filename))
        else:
            filename = filename.replace(".", "_{}.".format(str(uuid.uuid4())))

        stat = os.stat(original_filename)
        if stat.st_size > MAX_SRCIMG_SIZE and image.mode == "RGBA":
            image = image.convert('RGB')
            filename += ".jpeg"
            original_filename += ".jpeg"
            image.save(original_filename)
            stat = os.stat(original_filename)

        if stat.st_size > MAX_SRCIMG_SIZE:
            return None

        image.save(os.path.join(SOURCEIMG_DIR, filename))
        srcimg = MemeSourceImage(name=filename)
        srcimg.save()
        return srcimg

    @classmethod
    def count(cls, context):
        return cls.by_context(context).count()

    @classmethod
    def by_context(cls, context):
        return cls.objects.filter(Q(contexts=context) | Q(contexts=None)).filter(accepted=True)


class MemeTemplate(models.Model):

    class Meta:
        verbose_name = "Template"

    name = models.CharField(max_length=64, primary_key=True, verbose_name='File name')
    friendly_name = models.CharField(max_length=64, default='', blank=True, verbose_name='Friendly name')
    contexts = models.ManyToManyField(MemeContext, blank=True, verbose_name='Contexts')
    bg_color = models.CharField(max_length=16, default='', blank=True, verbose_name='Background color')
    bg_img = models.CharField(max_length=64, default='', blank=True, verbose_name='Background image')
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
        return reverse('memeviewer:template_preview_view', kwargs={'template_name': self.name})

    def get_image_url(self):
        return TEMPLATE_URL + self.name

    def get_bgimage_url(self):
        return self.bg_img and (TEMPLATE_URL + self.bg_img) or None

    def contexts_string(self):
        contexts = self.contexts.all()
        if contexts.count() == 0:
            return "*"
        result = ""
        for context in contexts:
            result += "{} ".format(context.context_id)
        return result.strip()

    def __str__(self):
        return self.friendly_name or self.name


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
        if MemeTemplate.count(context) == 0 or MemeSourceImage.count(context) == 0:
            raise FileNotFoundError("Not enough available source images or templates")
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

    def get_sourceimgs(self):
        return MemeSourceImageInSlot.objects.filter(meme=self).order_by('slot__slot_order')

    def get_local_path(self):
        return os.path.join(MEMES_DIR, self.meme_id + '.jpg')

    def get_url(self):
        return MEMES_URL + self.meme_id + '.jpg'

    def get_info_url(self):
        return WEBSITE_URL + 'meme/' + self.meme_id

    def __str__(self):
        return "{0} - #{1}, {2}".format(self.meme_id, self.number, self.gen_date)


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
    image_name = models.CharField(max_length=64, verbose_name='File name')
    context_link = models.ForeignKey(MemeContext, on_delete=models.CASCADE, verbose_name='Context')

    def __str__(self):
        return "{0} - {1} ({2})"\
            .format(self.image_name, self.context_link.context_id, self.IMAGE_TYPE_CHOICES[self.image_type][1])
