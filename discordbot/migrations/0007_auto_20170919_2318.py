# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-09-19 21:18
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('discordbot', '0006_auto_20170919_2310'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='discordserveruser',
            unique_together=set([('user', 'server')]),
        ),
    ]
