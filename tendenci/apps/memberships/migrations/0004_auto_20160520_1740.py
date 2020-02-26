# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('memberships', '0003_auto_20160217_1217'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membershipapp',
            name='use_for_corp',
            field=models.BooleanField(default=False, verbose_name='Use for Corporate Individuals'),
        ),
    ]
