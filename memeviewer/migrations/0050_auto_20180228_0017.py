# Generated by Django 2.0 on 2018-02-27 23:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('memeviewer', '0049_auto_20180227_2217'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imageincontext',
            name='image_name',
            field=models.CharField(max_length=256, verbose_name='Unique ID'),
        ),
        migrations.AlterField(
            model_name='memetemplate',
            name='bg_image_file',
            field=models.ImageField(blank=True, default='', max_length=256, upload_to='lambdabot/templates/'),
        ),
    ]