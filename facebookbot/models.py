from django.db import models

from memeviewer.models import Meem


class FacebookMeem(models.Model):

    class Meta:
        verbose_name = "Facebook meme link"

    meme = models.ForeignKey(Meem, on_delete=models.CASCADE, verbose_name='Meme link')
    post = models.CharField(max_length=40, verbose_name='Post link')

    def __str__(self):
        return "{0} - {1}".format(self.meme.number, self.post)
