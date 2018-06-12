# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import timezones.fields


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0004_auto_20160701_1247'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='news',
            name='group',
        ),
    ]
