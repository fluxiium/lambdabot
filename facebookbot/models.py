from django.db import models, transaction

from memeviewer.models import Meem, MemeImagePool


class FacebookPage(models.Model):
    class Meta:
        indexes = [models.Index(fields=['name'], name='idx_fbpage_name')]

    page_id = models.CharField(max_length=32, primary_key=True)
    name = models.CharField(max_length=64, blank=True, default='')
    token = models.TextField()
    image_pools = models.ManyToManyField(MemeImagePool)

    @transaction.atomic
    def generate_meme(self):
        meme = Meem.generate(self.image_pools, 'fb-' + self.page_id)
        fb_meme = FacebookMeem.objects.create(meme=meme, page=self)
        return fb_meme

    def __str__(self):
        return self.name


class FacebookMeem(models.Model):
    meme = models.ForeignKey(Meem, on_delete=models.CASCADE)
    page = models.ForeignKey(FacebookPage, null=True, default=None, on_delete=models.SET_NULL)
    post = models.CharField(max_length=40, blank=True, default='')

    def __str__(self):
        return "{0} - {1}".format(self.meme.number, self.post)
