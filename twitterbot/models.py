import twitter
from django.db import models, transaction
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from memeviewer.models import Meem, MemeImagePool, QueuedMemeImage


class TwitterPage(models.Model):
    class Meta:
        indexes = [models.Index(fields=['name'], name='idx_twtp_name')]

    name = models.CharField(max_length=64, blank=True, default='')
    handle = models.CharField(max_length=64, blank=True, default='')
    consumer_key = models.CharField(max_length=64)
    consumer_secret = models.CharField(max_length=64)
    token_key = models.CharField(max_length=64)
    token_secret = models.CharField(max_length=64)
    image_pools = models.ManyToManyField(MemeImagePool)
    enabled = models.BooleanField(default=True)

    @transaction.atomic
    def generate_meme(self):
        api = twitter.Api(consumer_key=self.consumer_key,
                          consumer_secret=self.consumer_secret,
                          access_token_key=self.token_key,
                          access_token_secret=self.token_secret)
        meme = Meem.generate(self.image_pools.all(), 'twt-' + str(self.pk))
        meme.make_img()
        status = api.PostUpdate(
            meme.info_url,
            media=open(meme.local_path, 'rb')
        )
        self.name = status.user.name
        self.handle = status.user.screen_name
        self.save()
        print("post added!")
        print(status)
        return TwitterMeem.objects.create(meme=meme, page=self, post=status.id)

    def __str__(self):
        return f'{self.name or "?"} (@{self.handle or "?"})'


@receiver(m2m_changed, sender=TwitterPage.image_pools.through)
def pools_changed(sender, instance, **_):
    if isinstance(instance, TwitterPage):
        QueuedMemeImage.objects.filter(queue_id='twt-' + str(instance.id)).delete()


class TwitterMeem(models.Model):

    class Meta:
        verbose_name = "Twitter meme link"

    meme = models.OneToOneField(Meem, on_delete=models.CASCADE)
    page = models.ForeignKey(TwitterPage, null=True, default=None, on_delete=models.SET_NULL)
    post = models.CharField(max_length=40, blank=True, default='')

    def __str__(self):
        return f"{self.meme.number} - {self.page}"
