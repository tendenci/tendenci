# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import tendenci.apps.user_groups.utils


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0003_auto_20160309_2123'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='content_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='contenttypes.ContentType', null=True),
        ),
        migrations.AlterField(
            model_name='file',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, default=tendenci.apps.user_groups.utils.get_default_group, to='user_groups.Group', null=True),
        ),
    ]
