# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Meta',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200, blank=True)),
                ('keywords', models.TextField(blank=True)),
                ('description', models.TextField(blank=True)),
                ('canonical_url', models.CharField(max_length=500, blank=True)),
                ('update_dt', models.DateTimeField(auto_now=True)),
                ('create_dt', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
