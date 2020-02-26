# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('memberships', '0005_auto_20161101_1518'),
    ]

    operations = [
        migrations.AddField(
            model_name='membershipset',
            name='donation_amount',
            field=models.DecimalField(default=0, max_digits=15, decimal_places=2, blank=True),
        ),
    ]
