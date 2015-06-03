# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ThemeFileVersion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file_name', models.CharField(max_length=200)),
                ('content', models.TextField(max_length=150000, blank=True)),
                ('relative_file_path', models.CharField(max_length=500, blank=True)),
                ('create_dt', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'theme archive',
                'verbose_name_plural': 'theme archives',
                'permissions': (('view_themefileversion', 'Can view theme version'),),
            },
        ),
    ]
