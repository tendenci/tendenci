# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tendenci.apps.base.fields
import django.db.models.deletion
import tendenci.libs.tinymce.models
from django.conf import settings
import tagging.fields


class Migration(migrations.Migration):

    dependencies = [
        ('user_groups', '0001_initial'),
        ('pages', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('meta', '0001_initial'),
        ('entities', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Officer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('phone', models.CharField(max_length=50, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200, verbose_name='title')),
                ('group', models.ForeignKey(to='user_groups.Group', help_text=b'Group with associated permissions for this officer position.', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='StudyGroup',
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
                ('title', models.CharField(max_length=500, blank=True)),
                ('slug', tendenci.apps.base.fields.SlugField(max_length=100, verbose_name='URL Path', db_index=True)),
                ('content', tendenci.libs.tinymce.models.HTMLField()),
                ('view_contact_form', models.BooleanField(default=False)),
                ('design_notes', models.TextField(verbose_name='Design Notes', blank=True)),
                ('syndicate', models.BooleanField(default=False, verbose_name='Include in RSS feed')),
                ('template', models.CharField(max_length=50, verbose_name='Template', blank=True)),
                ('tags', tagging.fields.TagField(max_length=255, blank=True)),
                ('mission', tendenci.libs.tinymce.models.HTMLField(null=True, blank=True)),
                ('notes', tendenci.libs.tinymce.models.HTMLField(null=True, blank=True)),
                ('contact_name', models.CharField(max_length=200, null=True, blank=True)),
                ('contact_email', models.CharField(max_length=200, null=True, blank=True)),
                ('join_link', models.CharField(max_length=200, null=True, blank=True)),
                ('creator', models.ForeignKey(related_name='studygroups_studygroup_creator', on_delete=django.db.models.deletion.SET_NULL, default=None, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('entity', models.ForeignKey(related_name='studygroups_studygroup_entity', on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='entities.Entity', null=True)),
                ('group', models.ForeignKey(to='user_groups.Group')),
                ('header_image', models.ForeignKey(to='pages.HeaderImage', null=True)),
                ('meta', models.OneToOneField(null=True, to='meta.Meta')),
                ('owner', models.ForeignKey(related_name='studygroups_studygroup_owner', on_delete=django.db.models.deletion.SET_NULL, default=None, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'permissions': (('view_studygroup', 'Can view studygroup'),),
            },
        ),
        migrations.AddField(
            model_name='officer',
            name='position',
            field=models.ForeignKey(to='studygroups.Position'),
        ),
        migrations.AddField(
            model_name='officer',
            name='study_group',
            field=models.ForeignKey(to='studygroups.StudyGroup'),
        ),
        migrations.AddField(
            model_name='officer',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
