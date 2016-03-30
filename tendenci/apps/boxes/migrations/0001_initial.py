# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tendenci.apps.user_groups.utils
import tendenci.libs.tinymce.models
import django.db.models.deletion
from django.conf import settings
import tagging.fields


class Migration(migrations.Migration):

    dependencies = [
        ('user_groups', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('entities', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Box',
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
                ('title', models.CharField(max_length=500, blank=True)),
                ('content', tendenci.libs.tinymce.models.HTMLField()),
                ('tags', tagging.fields.TagField(max_length=255, blank=True)),
                ('creator', models.ForeignKey(related_name='boxes_box_creator', on_delete=django.db.models.deletion.SET_NULL, default=None, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('entity', models.ForeignKey(related_name='boxes_box_entity', on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='entities.Entity', null=True)),
                ('group', models.ForeignKey(default=tendenci.apps.user_groups.utils.get_default_group, to='user_groups.Group', null=True)),
                ('owner', models.ForeignKey(related_name='boxes_box_owner', on_delete=django.db.models.deletion.SET_NULL, default=None, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['position'],
                'verbose_name_plural': 'Boxes',
                'permissions': (('view_box', 'Can view box'),),
            },
        ),
    ]
