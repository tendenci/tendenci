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
            name='Career',
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
                ('guid', models.CharField(max_length=40)),
                ('company', models.CharField(max_length=150, verbose_name='Company')),
                ('company_description', models.TextField(default=b'', verbose_name='Company Description', blank=True)),
                ('position_title', models.CharField(max_length=150, verbose_name='Position Title')),
                ('position_description', models.TextField(default=b'', verbose_name='Position Description', blank=True)),
                ('position_type', models.CharField(default=b'full time', max_length=50, verbose_name='Position Type', choices=[(b'full time', 'Full Time'), (b'part time', 'Part Time'), (b'permanent', 'Permanent'), (b'contract', 'Contract')])),
                ('start_dt', models.DateTimeField(null=True, verbose_name='Start Date/Time', blank=True)),
                ('end_dt', models.DateTimeField(null=True, verbose_name='End Date/Time', blank=True)),
                ('experience', models.TextField(default=b'', verbose_name='Experience', blank=True)),
                ('creator', models.ForeignKey(related_name='careers_career_creator', on_delete=django.db.models.deletion.SET_NULL, default=None, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('entity', models.ForeignKey(related_name='careers_career_entity', on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='entities.Entity', null=True)),
                ('owner', models.ForeignKey(related_name='careers_career_owner', on_delete=django.db.models.deletion.SET_NULL, default=None, to=settings.AUTH_USER_MODEL, null=True)),
                ('user', models.ForeignKey(related_name='careers', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Career',
                'verbose_name_plural': 'Careers',
                'permissions': (('view_career', 'Can view career'),),
            },
        ),
    ]
