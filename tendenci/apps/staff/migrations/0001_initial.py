# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings
import tagging.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('entities', '0001_initial'),
        ('files', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Staff',
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
                ('name', models.CharField(max_length=50)),
                ('slug', models.SlugField(max_length=75)),
                ('biography', models.TextField(null=True, blank=True)),
                ('email', models.EmailField(max_length=254, null=True, blank=True)),
                ('phone', models.CharField(max_length=25, null=True, blank=True)),
                ('cv', models.TextField()),
                ('personal_sites', models.TextField(help_text=b'List personal websites followed by a return', verbose_name='Personal Sites', blank=True)),
                ('tags', tagging.fields.TagField(help_text='Tags separated by commas. E.g Tag1, Tag2, Tag3', max_length=255, blank=True)),
                ('creator', models.ForeignKey(related_name='staff_staff_creator', on_delete=django.db.models.deletion.SET_NULL, default=None, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('department', models.ForeignKey(blank=True, to='staff.Department', null=True)),
                ('entity', models.ForeignKey(related_name='staff_staff_entity', on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='entities.Entity', null=True)),
                ('owner', models.ForeignKey(related_name='staff_staff_owner', on_delete=django.db.models.deletion.SET_NULL, default=None, to=settings.AUTH_USER_MODEL, null=True)),
                ('positions', models.ManyToManyField(to='staff.Position', blank=True)),
            ],
            options={
                'get_latest_by': '-position',
                'verbose_name': 'Staff',
                'verbose_name_plural': 'Staff',
                'permissions': (('view_staff', 'Can view staff'),),
            },
        ),
        migrations.CreateModel(
            name='StaffFile',
            fields=[
                ('file_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='files.File')),
                ('position', models.IntegerField(default=0, null=True, verbose_name='Position', blank=True)),
                ('photo_type', models.CharField(max_length=50, choices=[(b'featured', b'Featured'), (b'other', b'Other')])),
                ('staff', models.ForeignKey(to='staff.Staff')),
            ],
            options={
                'ordering': ('position',),
            },
            bases=('files.file', models.Model),
        ),
    ]
