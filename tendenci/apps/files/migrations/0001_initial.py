# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tendenci.apps.user_groups.utils
import tendenci.apps.files.models
import django.db.models.deletion
from django.conf import settings
import tagging.fields


class Migration(migrations.Migration):

    dependencies = [
        ('user_groups', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('entities', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MultipleFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='File',
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
                ('file', models.FileField(upload_to=tendenci.apps.files.models.file_directory, max_length=260, verbose_name=b'')),
                ('guid', models.CharField(max_length=40)),
                ('name', models.CharField(max_length=250, blank=True)),
                ('description', models.TextField(blank=True)),
                ('object_id', models.IntegerField(null=True, blank=True)),
                ('is_public', models.BooleanField(default=True)),
                ('tags', tagging.fields.TagField(max_length=255, null=True, blank=True)),
                ('content_type', models.ForeignKey(blank=True, to='contenttypes.ContentType', null=True)),
                ('creator', models.ForeignKey(related_name='files_file_creator', on_delete=django.db.models.deletion.SET_NULL, default=None, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('entity', models.ForeignKey(related_name='files_file_entity', on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='entities.Entity', null=True)),
            ],
            options={
                'permissions': (('view_file', 'Can view file'),),
            },
        ),
        migrations.CreateModel(
            name='FilesCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('parent', models.ForeignKey(to='files.FilesCategory', null=True)),
            ],
            options={
                'ordering': ('name',),
                'verbose_name_plural': 'File Categories',
            },
        ),
        migrations.AddField(
            model_name='file',
            name='file_cat',
            field=models.ForeignKey(related_name='file_cat', on_delete=django.db.models.deletion.SET_NULL, verbose_name='Files Category', to='files.FilesCategory', null=True),
        ),
        migrations.AddField(
            model_name='file',
            name='file_sub_cat',
            field=models.ForeignKey(related_name='file_subcat', on_delete=django.db.models.deletion.SET_NULL, verbose_name='Files Sub Category', to='files.FilesCategory', null=True),
        ),
        migrations.AddField(
            model_name='file',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, default=tendenci.apps.user_groups.utils.get_default_group, to='user_groups.Group', null=True),
        ),
        migrations.AddField(
            model_name='file',
            name='owner',
            field=models.ForeignKey(related_name='files_file_owner', on_delete=django.db.models.deletion.SET_NULL, default=None, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
