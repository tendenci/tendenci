# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tendenci.apps.imports.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Import',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('app_label', models.CharField(max_length=50)),
                ('model_name', models.CharField(max_length=50)),
                ('status', models.CharField(default=b'pending', max_length=50, verbose_name='status', choices=[(b'pending', 'Pending'), (b'processing', 'Processing'), (b'completed', 'Completed'), (b'failed', 'Failed')])),
                ('failure_reason', models.CharField(default=b'', max_length=250, blank=True)),
                ('file', models.FileField(upload_to=tendenci.apps.imports.models.file_directory, max_length=260, verbose_name=b'')),
                ('total_created', models.IntegerField(default=0)),
                ('total_updated', models.IntegerField(default=0)),
                ('total_invalid', models.IntegerField(default=0)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_done', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
