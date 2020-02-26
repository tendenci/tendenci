# -*- coding: utf-8 -*-


from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0005_auto_20160603_1347'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='group',
        ),
    ]
