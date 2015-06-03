# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('entities', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Industry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('allow_anonymous_view', models.BooleanField(default=True, verbose_name='Public can view')),
                ('allow_user_view', models.BooleanField(default=True, verbose_name='Signed in user can view')),
                ('allow_member_view', models.BooleanField(default=True)),
                ('allow_user_edit', models.BooleanField(default=False, verbose_name='Signed in user can change')),
                ('allow_member_edit', models.BooleanField(default=False)),
                ('create_dt', models.DateTimeField(auto_now_add=True, verbose_name='Created On')),
                ('update_dt', models.DateTimeField(auto_now=True, verbose_name='Last Updated')),
                ('creator_username', models.CharField(max_length=50)),
                ('owner_username', models.CharField(max_length=50)),
                ('status', models.BooleanField(default=True, verbose_name=b'Active')),
                ('status_detail', models.CharField(default=b'active', max_length=50)),
                ('position', models.IntegerField(default=0, null=True, verbose_name='Position', blank=True)),
                ('guid', models.CharField(max_length=40)),
                ('industry_name', models.CharField(max_length=200, verbose_name='Name')),
                ('industry_code', models.CharField(max_length=200, verbose_name='Industry Code')),
                ('description', models.TextField(default=b'', blank=True)),
                ('creator', models.ForeignKey(related_name='industries_industry_creator', on_delete=django.db.models.deletion.SET_NULL, default=None, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('entity', models.ForeignKey(related_name='industries_industry_entity', on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='entities.Entity', null=True)),
                ('owner', models.ForeignKey(related_name='industries_industry_owner', on_delete=django.db.models.deletion.SET_NULL, default=None, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('position', '-update_dt'),
                'verbose_name': 'Industry',
                'verbose_name_plural': 'Industries',
                'permissions': (('view_industry', 'Can view industry'),),
            },
        ),
    ]
