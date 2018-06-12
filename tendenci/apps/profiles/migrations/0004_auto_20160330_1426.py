# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import timezones.fields


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0003_auto_20160308_1106'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='allow_anonymous_view',
            field=models.NullBooleanField(default=False, verbose_name='Public can view'),
        ),
    ]
