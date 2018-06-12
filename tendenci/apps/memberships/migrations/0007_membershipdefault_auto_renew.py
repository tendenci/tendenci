# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('memberships', '0006_membershipset_donation_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='membershipdefault',
            name='auto_renew',
            field=models.BooleanField(default=False),
        ),
    ]
