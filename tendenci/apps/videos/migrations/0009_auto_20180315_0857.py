# -*- coding: utf-8 -*-
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0008_auto_20170905_1509'),
    ]

    operations = [
        migrations.AlterField(
            model_name='video',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='videos.Category', null=True),
        ),
        migrations.AlterField(
            model_name='video',
            name='slug',
            field=models.SlugField(unique=True, max_length=200, verbose_name='URL Path'),
        ),
        migrations.AlterField(
            model_name='video',
            name='video_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='videos.VideoType', null=True),
        ),
    ]
