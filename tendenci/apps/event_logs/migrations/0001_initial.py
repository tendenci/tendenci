# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('robots', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('entities', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.IntegerField(null=True)),
                ('source', models.CharField(max_length=50, null=True)),
                ('event_id', models.IntegerField()),
                ('event_name', models.CharField(max_length=50)),
                ('event_type', models.CharField(max_length=50)),
                ('event_data', models.TextField()),
                ('category', models.CharField(max_length=50, null=True)),
                ('session_id', models.CharField(max_length=40, null=True)),
                ('username', models.CharField(max_length=50, null=True)),
                ('email', models.EmailField(max_length=254, null=True)),
                ('user_ip_address', models.GenericIPAddressField(null=True)),
                ('server_ip_address', models.GenericIPAddressField(null=True)),
                ('url', models.URLField(max_length=255, null=True)),
                ('http_referrer', models.URLField(max_length=255, null=True)),
                ('headline', models.CharField(max_length=50, null=True)),
                ('description', models.CharField(max_length=120, null=True)),
                ('http_user_agent', models.TextField(null=True)),
                ('request_method', models.CharField(max_length=10, null=True)),
                ('query_string', models.TextField(null=True)),
                ('create_dt', models.DateTimeField(auto_now_add=True)),
                ('uuid', models.CharField(max_length=40)),
                ('application', models.CharField(max_length=50, db_index=True)),
                ('action', models.CharField(max_length=50, db_index=True)),
                ('model_name', models.CharField(max_length=75)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='contenttypes.ContentType', null=True)),
                ('entity', models.ForeignKey(to='entities.Entity', null=True)),
                ('robot', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='robots.Robot', null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'permissions': (('view_eventlog', 'Can view eventlog'),),
            },
        ),
        migrations.CreateModel(
            name='EventLogBaseColor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('source', models.CharField(max_length=50)),
                ('event_id', models.IntegerField()),
                ('hex_color', models.CharField(max_length=6)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EventLogColor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('event_id', models.IntegerField()),
                ('hex_color', models.CharField(max_length=6)),
                ('rgb_color', models.CommaSeparatedIntegerField(max_length=11)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
