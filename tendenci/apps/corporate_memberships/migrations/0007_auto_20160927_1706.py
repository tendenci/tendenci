# -*- coding: utf-8 -*-
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('corporate_memberships', '0006_auto_20160211_1542'),
    ]

    operations = [
        migrations.AddField(
            model_name='corpmembership',
            name='renew_from_id',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
