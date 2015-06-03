# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Guide',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('position', models.IntegerField(default=0, null=True, verbose_name='Position', blank=True)),
                ('title', models.CharField(max_length=100)),
                ('slug', models.CharField(unique=True, max_length=100)),
                ('content', models.TextField(blank=True)),
                ('section', models.CharField(default=b'misc', max_length=50, choices=[(b'Events', 'Events'), (b'Getting Started', 'Getting Started'), (b'Miscellaneous', 'Miscellaneous')])),
            ],
            options={
                'permissions': (('view_guide', 'Can view guide'),),
            },
        ),
    ]
