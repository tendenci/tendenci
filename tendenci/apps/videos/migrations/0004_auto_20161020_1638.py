# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def populate_release_dt(apps, schema_editor):
    Video = apps.get_model("videos", "Video")
    for video in Video.objects.all():
        if not video.release_dt:
            video.release_dt = video.create_dt
            video.save()
    
    

class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0003_video_release_dt'),
    ]

    operations = [
        migrations.RunPython(populate_release_dt),
    ]
