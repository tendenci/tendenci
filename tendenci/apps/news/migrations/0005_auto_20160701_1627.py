# -*- coding: utf-8 -*-


from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0004_auto_20160701_1247'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='news',
            name='group',
        ),
    ]
