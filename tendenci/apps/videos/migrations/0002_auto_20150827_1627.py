# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='video',
            options={'ordering': ('ordering',), 'verbose_name': 'Videos', 'verbose_name_plural': 'Videos', 'permissions': (('view_video', 'Can view video'),)},
        ),
    ]
