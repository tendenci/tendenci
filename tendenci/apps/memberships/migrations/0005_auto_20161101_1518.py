# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('memberships', '0004_auto_20160520_1740'),
    ]

    operations = [
        migrations.AddField(
            model_name='membershipapp',
            name='donation_default_amount',
            field=models.DecimalField(default=0, verbose_name='Default Amount', max_digits=15, decimal_places=2, blank=True),
        ),
        migrations.AddField(
            model_name='membershipapp',
            name='donation_enabled',
            field=models.BooleanField(default=False, verbose_name='Enable Donation'),
        ),
        migrations.AddField(
            model_name='membershipapp',
            name='donation_label',
            field=models.CharField(max_length=255, null=True, verbose_name='Label', blank=True),
        ),
    ]
