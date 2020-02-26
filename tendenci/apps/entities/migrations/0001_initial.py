# -*- coding: utf-8 -*-


from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Entity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('guid', models.CharField(max_length=40)),
                ('entity_name', models.CharField(max_length=200, verbose_name='Name', blank=True)),
                ('entity_type', models.CharField(max_length=200, verbose_name='Type', blank=True)),
                ('contact_name', models.CharField(max_length=200, verbose_name='Contact Name', blank=True)),
                ('phone', models.CharField(max_length=50, blank=True)),
                ('fax', models.CharField(max_length=50, blank=True)),
                ('email', models.CharField(max_length=120, blank=True)),
                ('website', models.CharField(max_length=300, blank=True)),
                ('summary', models.TextField(blank=True)),
                ('notes', models.TextField(blank=True)),
                ('admin_notes', models.TextField(verbose_name='Admin Notes', blank=True)),
                ('allow_anonymous_view', models.BooleanField(default=True, verbose_name='Public can view')),
                ('allow_user_view', models.BooleanField(default=True, verbose_name='Signed in user can view')),
                ('allow_member_view', models.BooleanField(default=True)),
                ('allow_anonymous_edit', models.BooleanField(default=False)),
                ('allow_user_edit', models.BooleanField(default=False, verbose_name='Signed in user can change')),
                ('allow_member_edit', models.BooleanField(default=False)),
                ('create_dt', models.DateTimeField(auto_now_add=True)),
                ('update_dt', models.DateTimeField(auto_now=True)),
                ('creator_username', models.CharField(max_length=50)),
                ('owner_username', models.CharField(max_length=50)),
                ('status', models.BooleanField(default=True, verbose_name='Active')),
                ('status_detail', models.CharField(default='active', max_length=50)),
                ('creator', models.ForeignKey(related_name='entity_creator', on_delete=django.db.models.deletion.SET_NULL, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('entity_parent', models.ForeignKey(related_name='entity_children', blank=True, to='entities.Entity', null=True, on_delete=django.db.models.deletion.CASCADE)),
                ('owner', models.ForeignKey(related_name='entity_owner', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('entity_name',),
                'verbose_name_plural': 'entities',
            },
        ),
    ]
