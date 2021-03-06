# Generated by Django 2.0 on 2018-04-27 23:32

from django.db import migrations


def do_stuff(apps, schema_editor):
    MemeImagePool = apps.get_model('memeviewer', 'MemeImagePool')
    FacebookMeem = apps.get_model('facebookbot', 'FacebookMeem')
    FacebookPage = apps.get_model('facebookbot', 'FacebookPage')
    halflifepool = MemeImagePool.objects.get(name='halflife')
    mypage = None
    for m in FacebookMeem.objects.all():
        if not mypage:
            mypage = FacebookPage.objects.get_or_create(page_id='486920085001034', name='LambdaBot 3883', token='')[0]
            mypage.image_pools.add(halflifepool)
            mypage.save()
        m.page = mypage
        m.save()


class Migration(migrations.Migration):

    dependencies = [
        ('facebookbot', '0002_auto_20180428_0130'),
    ]

    operations = [
        migrations.RunPython(do_stuff)
    ]
