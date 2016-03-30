# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tendenci.libs.tinymce.models
import django.db.models.deletion
from django.conf import settings
import tagging.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('entities', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=200)),
                ('slug', models.SlugField(unique=True)),
            ],
            options={
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='OembedlyCache',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.CharField(max_length=800)),
                ('width', models.IntegerField(db_index=True)),
                ('height', models.IntegerField(db_index=True)),
                ('code', models.TextField()),
                ('thumbnail', models.CharField(max_length=800)),
            ],
        ),
        migrations.CreateModel(
            name='Video',
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
                ('title', models.CharField(max_length=200)),
                ('slug', models.SlugField(unique=True, max_length=200)),
                ('image', models.ImageField(upload_to=b'uploads/videos/%y/%m', blank=True)),
                ('video_url', models.CharField(help_text=b'Youtube, Vimeo, etc..', max_length=500)),
                ('description', tendenci.libs.tinymce.models.HTMLField()),
                ('tags', tagging.fields.TagField(help_text=b'Tag 1, Tag 2, ...', max_length=255, blank=True)),
                ('ordering', models.IntegerField(null=True, blank=True)),
                ('category', models.ForeignKey(to='videos.Category')),
                ('creator', models.ForeignKey(related_name='videos_video_creator', on_delete=django.db.models.deletion.SET_NULL, default=None, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('entity', models.ForeignKey(related_name='videos_video_entity', on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='entities.Entity', null=True)),
                ('owner', models.ForeignKey(related_name='videos_video_owner', on_delete=django.db.models.deletion.SET_NULL, default=None, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('ordering',),
                'verbose_name': 'Video',
                'verbose_name_plural': 'Videos',
                'permissions': (('view_video', 'Can view video'),),
            },
        ),
        migrations.CreateModel(
            name='VideoType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=200)),
                ('slug', models.SlugField(unique=True)),
            ],
            options={
                'verbose_name_plural': 'Video Types',
            },
        ),
        migrations.AddField(
            model_name='video',
            name='video_type',
            field=models.ForeignKey(blank=True, to='videos.VideoType', null=True),
        ),
    ]
