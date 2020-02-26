# -*- coding: utf-8 -*-
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0009_auto_20180315_0857'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='video',
            options={'ordering': ('position',), 'verbose_name': 'Video', 'verbose_name_plural': 'Videos'},
        ),
    ]
