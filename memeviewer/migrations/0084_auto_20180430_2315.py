# Generated by Django 2.0 on 2018-04-30 21:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('memeviewer', '0083_auto_20180430_2036'),
    ]

    operations = [
        migrations.AlterField(
            model_name='memesourceimage',
            name='accepted',
            field=models.NullBooleanField(default=None),
        ),
        migrations.AlterField(
            model_name='memetemplate',
            name='accepted',
            field=models.NullBooleanField(default=None),
        ),
    ]
