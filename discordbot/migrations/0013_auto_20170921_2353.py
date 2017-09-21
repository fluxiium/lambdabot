# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-09-21 21:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('discordbot', '0012_murphyrequest_channel_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='murphyrequest',
            name='processed',
        ),
        migrations.AddField(
            model_name='murphyrequest',
            name='answer_date',
            field=models.DateTimeField(default=None, null=True, verbose_name='Date answered'),
        ),
        migrations.AddField(
            model_name='murphyrequest',
            name='process_date',
            field=models.DateTimeField(default=None, null=True, verbose_name='Process start'),
        ),
    ]