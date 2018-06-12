# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import timezones.fields
import tendenci.apps.user_groups.utils


class Migration(migrations.Migration):

    dependencies = [
        ('user_groups', '0001_initial'),
        ('news', '0002_auto_20150804_1545'),
    ]

    operations = [
        migrations.AddField(
            model_name='news',
            name='groups',
            field=models.ManyToManyField(default=tendenci.apps.user_groups.utils.get_default_group, related_name='group_news', to='user_groups.Group'),
        ),
    ]
