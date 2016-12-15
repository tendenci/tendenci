# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import timezones.fields


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0005_auto_20160330_1428'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='direct_mail',
            field=models.BooleanField(default=True, verbose_name='direct mail'),
        ),
    ]
