# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-08-25 00:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('memeviewer', '0012_auto_20170825_0209'),
    ]

    operations = [
        migrations.AddField(
            model_name='imageincontext',
            name='context',
            field=models.CharField(default='', max_length=32),
            preserve_default=False,
        ),
    ]
