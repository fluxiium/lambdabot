# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-09-08 12:45
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('memeviewer', '0023_auto_20170908_1433'),
    ]

    database_operations = [
        migrations.AlterModelTable('FacebookMeem', 'facebookbot_facebookmeem'),
        migrations.AlterModelTable('TwitterMeem', 'twitterbot_twittermeem'),
        migrations.AlterModelTable('DiscordMeem', 'discordbot_discordmeem'),
    ]

    state_operations = [
        migrations.DeleteModel('FacebookMeem'),
        migrations.DeleteModel('TwitterMeem'),
        migrations.DeleteModel('DiscordMeem'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=database_operations,
            state_operations=state_operations)
    ]
