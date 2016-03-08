# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import timezones.fields


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0002_auto_20150804_1545'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='country',
            field=models.CharField(max_length=255, verbose_name='country', blank=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='country_2',
            field=models.CharField(max_length=255, verbose_name='country', blank=True),
        ),
    ]
