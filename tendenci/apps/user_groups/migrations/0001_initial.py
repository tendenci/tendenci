# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tendenci.apps.base.fields
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0006_require_contenttypes_0002'),
        ('entities', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
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
                ('name', models.CharField(unique=True, max_length=255, verbose_name='Group Name')),
                ('slug', tendenci.apps.base.fields.SlugField(unique=True, max_length=100, verbose_name='URL Path', db_index=True)),
                ('guid', models.CharField(max_length=40)),
                ('label', models.CharField(max_length=255, verbose_name='Group Label', blank=True)),
                ('dashboard_url', models.CharField(default=b'', help_text='Enable Group Dashboard Redirect in site settings to use this feature.', max_length=255, verbose_name='Dashboard URL', blank=True)),
                ('type', models.CharField(default=b'distribution', max_length=75, blank=True, choices=[(b'distribution', 'Distribution'), (b'security', 'Security'), (b'system_generated', 'System Generated')])),
                ('email_recipient', models.CharField(max_length=255, verbose_name='Recipient Email', blank=True)),
                ('show_as_option', models.BooleanField(default=True, verbose_name='Display Option')),
                ('allow_self_add', models.BooleanField(default=True, verbose_name='Allow Self Add')),
                ('allow_self_remove', models.BooleanField(default=True, verbose_name='Allow Self Remove')),
                ('sync_newsletters', models.BooleanField(default=True, verbose_name='Sync for newsletters')),
                ('description', models.TextField(blank=True)),
                ('auto_respond', models.BooleanField(default=False, verbose_name='Auto Responder')),
                ('auto_respond_priority', models.FloatField(default=0, verbose_name='Priority', blank=True)),
                ('notes', models.TextField(blank=True)),
                ('creator', models.ForeignKey(related_name='user_groups_group_creator', on_delete=django.db.models.deletion.SET_NULL, default=None, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('entity', models.ForeignKey(related_name='user_groups_group_entity', on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='entities.Entity', null=True)),
                ('group', models.OneToOneField(null=True, default=None, to='auth.Group')),
            ],
            options={
                'ordering': ('name',),
                'verbose_name': 'Group',
                'verbose_name_plural': 'Groups',
                'permissions': (('view_group', 'Can view group'),),
            },
        ),
        migrations.CreateModel(
            name='GroupMembership',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('role', models.CharField(default=b'', max_length=255, blank=True)),
                ('sort_order', models.IntegerField(default=0, verbose_name='Sort Order', blank=True)),
                ('creator_id', models.IntegerField(default=0, editable=False)),
                ('creator_username', models.CharField(max_length=50, editable=False)),
                ('owner_id', models.IntegerField(default=0, editable=False)),
                ('owner_username', models.CharField(max_length=50, editable=False)),
                ('status', models.BooleanField(default=True)),
                ('status_detail', models.CharField(default=b'active', max_length=50, choices=[(b'active', b'Active'), (b'inactive', b'Inactive')])),
                ('create_dt', models.DateTimeField(auto_now_add=True)),
                ('update_dt', models.DateTimeField(auto_now=True)),
                ('is_newsletter_subscribed', models.BooleanField(default=True)),
                ('newsletter_key', models.CharField(max_length=50, null=True, blank=True)),
                ('group', models.ForeignKey(to='user_groups.Group')),
                ('member', models.ForeignKey(related_name='group_member', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Group Membership',
                'verbose_name_plural': 'Group Memberships',
            },
        ),
        migrations.AddField(
            model_name='group',
            name='members',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, through='user_groups.GroupMembership'),
        ),
        migrations.AddField(
            model_name='group',
            name='owner',
            field=models.ForeignKey(related_name='user_groups_group_owner', on_delete=django.db.models.deletion.SET_NULL, default=None, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='group',
            name='permissions',
            field=models.ManyToManyField(related_name='group_permissions', to='auth.Permission', blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='groupmembership',
            unique_together=set([('group', 'member')]),
        ),
    ]
