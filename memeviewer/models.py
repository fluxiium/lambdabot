import json
import os
import uuid

from django.db import models
from django.utils import timezone

from lamdabotweb.settings import MEMES_DIR, STATIC_URL
from memeviewer.context import next_template, MEME_TEMPLATES, next_sourceimg


class Meem(models.Model):
    number = models.AutoField(primary_key=True)
    meme_id = models.CharField(max_length=36)
    template = models.CharField(max_length=64)
    sourceimgs = models.TextField()
    context = models.CharField(max_length=32)
    gen_date = models.DateTimeField(default=timezone.now)

    @classmethod
    def create(cls, template, sourceimgs, context):
        return cls(template=template, sourceimgs=json.dumps(sourceimgs), context=context, meme_id=str(uuid.uuid4()))

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
        meem.save()
        return meem

    def get_sourceimgs(self):
        return json.loads(self.sourceimgs)

    def get_local_path(self):
        return os.path.join(MEMES_DIR, self.meme_id + '.jpg')

    def get_url(self):
        return STATIC_URL + 'lambdabot/resources/memes/' + self.meme_id + '.jpg'

    def __str__(self):
        return "{0} - #{1}, {2}".format(self.meme_id, self.number, self.gen_date)
