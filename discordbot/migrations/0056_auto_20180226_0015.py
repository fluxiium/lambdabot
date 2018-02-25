# Generated by Django 2.0 on 2018-02-25 23:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('discordbot', '0055_auto_20180226_0007'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='discordserverperm',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='discordserverperm',
            name='server',
        ),
        migrations.AlterUniqueTogether(
            name='discordserveruserperm',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='discordserveruserperm',
            name='server_user',
        ),
        migrations.DeleteModel(
            name='DiscordServerPerm',
        ),
        migrations.DeleteModel(
            name='DiscordServerUserPerm',
        ),
    ]