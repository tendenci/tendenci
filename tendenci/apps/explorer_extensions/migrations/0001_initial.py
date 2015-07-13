# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DatabaseDumpFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_dt', models.DateTimeField(auto_now_add=True)),
                ('end_dt', models.DateTimeField(null=True, blank=True)),
                ('dbfile', models.FileField(upload_to=b'dbdump')),
                ('status', models.CharField(default=b'pending', max_length=50, choices=[(b'completed', 'Completed'), (b'pending', 'Pending'), (b'failed', 'Failed'), (b'expired', 'Expired')])),
                ('export_format', models.CharField(default=b'json', max_length=20, choices=[(b'json', b'json'), (b'xml', b'xml')])),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
