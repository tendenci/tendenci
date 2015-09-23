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
            name='Speaker',
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
                ('name', models.CharField(max_length=50)),
                ('slug', models.SlugField(max_length=75)),
                ('company', models.CharField(max_length=150, blank=True)),
                ('position', models.CharField(max_length=150, blank=True)),
                ('biography', models.TextField(null=True, blank=True)),
                ('email', models.EmailField(max_length=254, null=True, blank=True)),
                ('ordering', models.IntegerField(max_length=3, verbose_name='order')),
                ('facebook', models.CharField(max_length=100, blank=True)),
                ('twitter', models.CharField(max_length=100, blank=True)),
                ('linkedin', models.CharField(max_length=100, blank=True)),
                ('get_satisfaction', models.CharField(max_length=100, verbose_name=b'GetSatisfaction', blank=True)),
                ('flickr', models.CharField(max_length=100, blank=True)),
                ('slideshare', models.CharField(max_length=100, blank=True)),
                ('personal_sites', models.TextField(help_text=b'List personal websites followed by a return', verbose_name='Personal Sites', blank=True)),
                ('tags', tagging.fields.TagField(help_text='Tags separated by commas. E.g Tag1, Tag2, Tag3', max_length=255, blank=True)),
                ('creator', models.ForeignKey(related_name='speakers_speaker_creator', on_delete=django.db.models.deletion.SET_NULL, default=None, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('entity', models.ForeignKey(related_name='speakers_speaker_entity', on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='entities.Entity', null=True)),
                ('owner', models.ForeignKey(related_name='speakers_speaker_owner', on_delete=django.db.models.deletion.SET_NULL, default=None, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'get_latest_by': '-start_date',
                'verbose_name': 'speaker',
                'verbose_name_plural': 'speaker',
                'permissions': (('view_speaker', 'Can view speaker'),),
            },
        ),
        migrations.CreateModel(
            name='SpeakerFile',
            fields=[
                ('file_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='files.File')),
                ('photo_type', models.CharField(max_length=50, choices=[(b'professional', b'Professional'), (b'fun', b'Fun')])),
                ('position', models.IntegerField(blank=True)),
                ('speaker', models.ForeignKey(to='speakers.Speaker')),
            ],
            options={
                'ordering': ('position',),
            },
            bases=('files.file',),
        ),
        migrations.CreateModel(
            name='Track',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=50)),
            ],
        ),
        migrations.AddField(
            model_name='speaker',
            name='track',
            field=models.ForeignKey(to='speakers.Track', null=True),
        ),
    ]
