# -*- coding: utf-8 -*-
from django.db import migrations


def assign_position(apps, schema_editor):
    """
    Assign value from ordering to position
    """
    Video = apps.get_model('videos', 'Video')

    for video in Video.objects.all():
        video.position = video.ordering
        video.save()

class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0006_auto_20170905_1452'),
    ]

    operations = [
        migrations.RunPython(assign_position),
    ]
