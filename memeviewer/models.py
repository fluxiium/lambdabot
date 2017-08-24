import json
import os
import uuid

from django.db import models
from django.utils import timezone

from lamdabotweb.settings import MEMES_DIR, STATIC_URL
from memeviewer.context import next_template, MEME_TEMPLATES, next_sourceimg


def struuid4():
    return str(uuid.uuid4())


def next_meme_number():
    return (Meem.objects.all().aggregate(largest=models.Max('number'))['largest'] or 0) + 1


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

    def __str__(self):
        return "{0} - #{1}, {2}".format(self.meme_id, self.number, self.gen_date)


class FacebookMeem(models.Model):
    meme = models.ForeignKey(Meem, on_delete=models.CASCADE)
    url = models.CharField(max_length=256)


class TwitterMeem(models.Model):
    meme = models.ForeignKey(Meem, on_delete=models.CASCADE)
    url = models.CharField(max_length=256)


class DiscordMeem(models.Model):
    meme = models.ForeignKey(Meem, on_delete=models.CASCADE)
    server = models.CharField(max_length=64)
