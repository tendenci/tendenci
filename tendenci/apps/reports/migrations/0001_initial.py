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
            name='Report',
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
                ('type', models.CharField(max_length=100)),
                ('config', models.TextField(blank=True)),
                ('creator', models.ForeignKey(related_name='reports_report_creator', on_delete=django.db.models.deletion.SET_NULL, default=None, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('entity', models.ForeignKey(related_name='reports_report_entity', on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='entities.Entity', null=True)),
                ('owner', models.ForeignKey(related_name='reports_report_owner', on_delete=django.db.models.deletion.SET_NULL, default=None, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'Report',
                'verbose_name_plural': 'Reports',
            },
        ),
        migrations.CreateModel(
            name='Run',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_dt', models.DateTimeField(auto_now_add=True)),
                ('start_dt', models.DateTimeField(null=True)),
                ('complete_dt', models.DateTimeField(null=True)),
                ('range_start_dt', models.DateTimeField(null=True)),
                ('range_end_dt', models.DateTimeField(null=True)),
                ('creator_username', models.CharField(default=b'', max_length=200, blank=True)),
                ('status', models.CharField(default=b'unstarted', max_length=20, choices=[(b'unstarted', b'Unstarted'), (b'running', b'Running'), (b'complete', b'Complete'), (b'error', b'Error')])),
                ('output', models.TextField(blank=True)),
                ('output_type', models.CharField(default=b'html', max_length=20, choices=[(b'html', b'HTML'), (b'html-extended', b'HTML Extended'), (b'html-summary', b'HTML Summary')])),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
                ('report', models.ForeignKey(to='reports.Report')),
            ],
            options={
                'verbose_name': 'Run',
                'verbose_name_plural': 'Runs',
            },
        ),
    ]
