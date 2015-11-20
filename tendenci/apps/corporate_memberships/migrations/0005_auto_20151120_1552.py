# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corporate_memberships', '0004_auto_20151120_1538'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='corporatemembershiptype',
            name='apply_threshold',
        ),
        migrations.RemoveField(
            model_name='corporatemembershiptype',
            name='individual_threshold',
        ),
        migrations.RemoveField(
            model_name='corporatemembershiptype',
            name='individual_threshold_price',
        ),
    ]
