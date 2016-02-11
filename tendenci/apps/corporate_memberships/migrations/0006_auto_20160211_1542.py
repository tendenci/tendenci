# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corporate_memberships', '0005_auto_20151120_1552'),
    ]

    operations = [
        migrations.AddField(
            model_name='corporatemembershiptype',
            name='above_cap_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=15, blank=True, help_text='Price for members who join above cap.', null=True, verbose_name='Membership cap'),
        ),
        migrations.AddField(
            model_name='corporatemembershiptype',
            name='allow_above_cap',
            field=models.BooleanField(default=False, help_text='Check this box to allow additional member join above cap.', verbose_name='Allow above cap'),
        ),
    ]
