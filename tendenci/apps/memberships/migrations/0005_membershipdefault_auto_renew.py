# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('memberships', '0004_auto_20160520_1740'),
    ]

    operations = [
        migrations.AddField(
            model_name='membershipdefault',
            name='auto_renew',
            field=models.BooleanField(default=False),
        ),
    ]
