# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-08-25 00:09
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('memeviewer', '0011_auto_20170825_0127'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='imageincontext',
            name='context',
        ),
        migrations.RemoveField(
            model_name='meem',
            name='context',
        ),
        migrations.RemoveField(
            model_name='meem',
            name='template',
        ),
    ]