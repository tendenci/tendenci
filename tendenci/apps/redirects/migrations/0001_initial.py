# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Redirect',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('from_app', models.CharField(db_index=True, max_length=100, verbose_name='From App', blank=True)),
                ('from_url', models.CharField(db_index=True, max_length=255, verbose_name='From URL', blank=True)),
                ('to_url', models.CharField(help_text='You may reference any named regex pattern in From URL with (name). e.g. (?P<slug>[\\w\\-\\/]+) can be mapped to (slug).', max_length=255, verbose_name='To URL', db_index=True)),
                ('http_status', models.SmallIntegerField(default=301, verbose_name='HTTP Status', choices=[(301, '301 - Permanent Redirect'), (302, '302 - Temporary Redirect')])),
                ('status', models.SmallIntegerField(default=1, choices=[(1, 'Active'), (0, 'Inactive')])),
                ('uses_regex', models.BooleanField(default=False, help_text='Check if the From URL uses a regular expression.', verbose_name='Uses Regular Expression')),
                ('create_dt', models.DateTimeField(auto_now_add=True)),
                ('update_dt', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
