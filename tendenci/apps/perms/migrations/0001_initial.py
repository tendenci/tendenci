# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('user_groups', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ObjectPermission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('codename', models.CharField(max_length=255)),
                ('object_id', models.IntegerField()),
                ('create_dt', models.DateTimeField(auto_now_add=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('group', models.ForeignKey(to='user_groups.Group', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
    ]
