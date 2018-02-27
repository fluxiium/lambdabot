# Generated by Django 2.0 on 2018-02-27 21:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('memeviewer', '0047_auto_20180227_2150'),
    ]

    operations = [
        migrations.AlterField(
            model_name='memesourceimage',
            name='image_file',
            field=models.ImageField(blank=True, default=None, max_length=256, null=True, upload_to='lambdabot/sourceimg/'),
        ),
        migrations.AlterField(
            model_name='memetemplate',
            name='bg_image_file',
            field=models.ImageField(blank=True, default=None, max_length=256, null=True, upload_to='lambdabot/templates/'),
        ),
        migrations.AlterField(
            model_name='memetemplate',
            name='image_file',
            field=models.ImageField(blank=True, default=None, max_length=256, null=True, upload_to='lambdabot/templates/'),
        ),
    ]
