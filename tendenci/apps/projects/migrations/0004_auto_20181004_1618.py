# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0003_auto_20181004_1616'),
    ]

    operations = [
        migrations.AlterField(
            model_name='documents',
            name='doc_type',
            field=models.ForeignKey(blank=True, to='projects.DocumentType', null=True),
        ),
    ]
