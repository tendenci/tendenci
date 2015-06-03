# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Setting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('label', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('data_type', models.CharField(max_length=10, choices=[(b'string', 'string'), (b'boolean', 'boolean'), (b'integer', 'int'), (b'file', 'file')])),
                ('value', models.TextField(blank=True)),
                ('default_value', models.TextField(blank=True)),
                ('input_type', models.CharField(max_length=25, choices=[(b'text', 'Text'), (b'textarea', 'Textarea'), (b'select', 'Select'), (b'file', 'File')])),
                ('input_value', models.CharField(max_length=1000, blank=True)),
                ('client_editable', models.BooleanField(default=True)),
                ('store', models.BooleanField(default=True)),
                ('update_dt', models.DateTimeField(auto_now=True, null=True)),
                ('updated_by', models.CharField(max_length=50, blank=True)),
                ('scope', models.CharField(max_length=50)),
                ('scope_category', models.CharField(max_length=50)),
                ('parent_id', models.IntegerField(default=0, blank=True)),
                ('is_secure', models.BooleanField(default=False)),
            ],
        ),
    ]
