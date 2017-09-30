# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-09-24 01:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('discordbot', '0018_murphyrequest_related_request'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProcessedMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('msg_id', models.CharField(max_length=32, verbose_name='Message ID')),
                ('process_date', models.DateTimeField(verbose_name='Date processed')),
            ],
            options={
                'verbose_name': 'Processed message',
            },
        ),
    ]