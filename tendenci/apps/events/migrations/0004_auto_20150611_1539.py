# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0003_auto_20150611_1537'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='end_dt',
            field=models.DateTimeField(default=datetime.datetime(2015, 7, 11, 17, 39, 14, 182580)),
        ),
        migrations.AlterField(
            model_name='event',
            name='start_dt',
            field=models.DateTimeField(default=datetime.datetime(2015, 7, 11, 15, 39, 14, 182544)),
        ),
        migrations.AlterField(
            model_name='recurringevent',
            name='starts_on',
            field=models.DateTimeField(default=datetime.datetime(2015, 7, 11, 15, 39, 14, 181393)),
        ),
    ]
