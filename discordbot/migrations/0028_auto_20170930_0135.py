# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-09-29 23:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('discordbot', '0027_auto_20170930_0113'),
    ]

    operations = [
        migrations.AlterField(
            model_name='discordcommand',
            name='help',
            field=models.TextField(blank=True, default='', verbose_name='Help string'),
        ),
        migrations.AlterField(
            model_name='discordcommand',
            name='help_params',
            field=models.CharField(blank=True, default='', max_length=256, verbose_name='Parameters'),
        ),
        migrations.AlterField(
            model_name='discordcommand',
            name='message',
            field=models.TextField(blank=True, default='', verbose_name='Text message'),
        ),
        migrations.AlterField(
            model_name='discordserver',
            name='name',
            field=models.CharField(blank=True, default='', max_length=64, verbose_name='Server name'),
        ),
        migrations.AlterField(
            model_name='discordserveruser',
            name='meme_limit_count',
            field=models.IntegerField(blank=True, default=None, null=True, verbose_name='Meme limit'),
        ),
        migrations.AlterField(
            model_name='discordserveruser',
            name='meme_limit_time',
            field=models.IntegerField(blank=True, default=None, null=True, verbose_name='Meme limit timeout'),
        ),
        migrations.AlterField(
            model_name='discordserveruser',
            name='nickname',
            field=models.CharField(blank=True, default='', max_length=64, verbose_name='Nickname'),
        ),
        migrations.AlterField(
            model_name='murphyfacepic',
            name='face_pic',
            field=models.CharField(blank=True, default='', max_length=256, verbose_name='Face pic'),
        ),
        migrations.AlterField(
            model_name='murphyrequest',
            name='face_pic',
            field=models.CharField(blank=True, default='', max_length=256, verbose_name='Face pic'),
        ),
        migrations.AlterField(
            model_name='murphyrequest',
            name='question',
            field=models.CharField(blank=True, default='', max_length=256, verbose_name='Question'),
        ),
    ]
