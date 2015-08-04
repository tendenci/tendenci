# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tendenci.apps.corporate_memberships.models


class Migration(migrations.Migration):

    dependencies = [
        ('corporate_memberships', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='corpmembershipimport',
            name='upload_file',
            field=models.FileField(upload_to=tendenci.apps.corporate_memberships.models.get_import_file_path, max_length=260, verbose_name='Upload File'),
        ),
    ]
