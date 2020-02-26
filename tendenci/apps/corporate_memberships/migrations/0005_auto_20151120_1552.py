# -*- coding: utf-8 -*-
from django.db import migrations


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
