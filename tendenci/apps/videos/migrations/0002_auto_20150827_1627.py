# -*- coding: utf-8 -*-
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='video',
            options={'ordering': ('ordering',), 'verbose_name': 'Videos', 'verbose_name_plural': 'Videos'},
        ),
    ]
