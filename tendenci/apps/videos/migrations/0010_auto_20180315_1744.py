# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0009_auto_20180315_0857'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='video',
            options={'ordering': ('position',), 'verbose_name': 'Video', 'verbose_name_plural': 'Videos', 'permissions': (('view_video', 'Can view video'),)},
        ),
    ]
