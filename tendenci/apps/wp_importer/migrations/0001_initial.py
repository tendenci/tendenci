# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('files', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssociatedFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('post_id', models.IntegerField()),
                ('file', models.ForeignKey(to='files.File')),
            ],
        ),
        migrations.CreateModel(
            name='BlogImport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('blog_import_date', models.DateTimeField(auto_now_add=True)),
                ('blog', models.FileField(upload_to=b'blogimport')),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
