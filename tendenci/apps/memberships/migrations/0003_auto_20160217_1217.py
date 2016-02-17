# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('memberships', '0002_auto_20150804_1545'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membershiptype',
            name='admin_only',
            field=models.BooleanField(default=False, verbose_name='Admin Only'),
        ),
    ]
