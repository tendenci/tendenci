# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Robot',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150)),
                ('url', models.URLField()),
                ('version', models.CharField(max_length=50)),
                ('status', models.BooleanField(default=True)),
                ('status_detail', models.CharField(default=b'active', max_length=50, choices=[(b'active', 'Active'), (b'inactive', 'Inactive')])),
            ],
        ),
    ]
