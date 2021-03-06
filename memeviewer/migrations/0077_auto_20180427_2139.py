# Generated by Django 2.0 on 2018-04-27 19:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('memeviewer', '0076_auto_20180423_1906'),
    ]

    operations = [
        migrations.CreateModel(
            name='MemeImagePool',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='QueuedMemeImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('image_type', models.IntegerField(choices=[(0, 'Source image'), (1, 'Template')])),
                ('queue_id', models.CharField(max_length=128)),
            ],
        ),
        migrations.RemoveIndex(
            model_name='memesourceimage',
            name='idx_srcimg_mcount',
        ),
        migrations.RemoveIndex(
            model_name='memetemplate',
            name='idx_template_mcount',
        ),
        migrations.RemoveField(
            model_name='memesourceimage',
            name='meme_count',
        ),
        migrations.RemoveField(
            model_name='memetemplate',
            name='meme_count',
        ),
        migrations.AddField(
            model_name='memesourceimage',
            name='random_usages',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='memetemplate',
            name='random_usages',
            field=models.IntegerField(default=0),
        ),
        migrations.AddIndex(
            model_name='memesourceimage',
            index=models.Index(fields=['random_usages'], name='idx_srcimg_usages'),
        ),
        migrations.AddIndex(
            model_name='memetemplate',
            index=models.Index(fields=['random_usages'], name='idx_template_usages'),
        ),
        migrations.DeleteModel(
            name='MemeSourceImageInContext',
        ),
        migrations.DeleteModel(
            name='MemeTemplateInContext',
        ),
        migrations.AddField(
            model_name='memesourceimage',
            name='image_pool',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='memeviewer.MemeImagePool'),
        ),
        migrations.AddField(
            model_name='memetemplate',
            name='image_pool',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='memeviewer.MemeImagePool'),
        ),
    ]
