# Generated by Django 2.0 on 2018-03-22 23:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('discordbot', '0060_auto_20180303_0301'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='discordserver',
            name='submit_limit_count',
        ),
        migrations.RemoveField(
            model_name='discordserver',
            name='submit_limit_time',
        ),
        migrations.RemoveField(
            model_name='discordserveruser',
            name='submit_limit_count',
        ),
        migrations.RemoveField(
            model_name='discordserveruser',
            name='submit_limit_time',
        ),
    ]
