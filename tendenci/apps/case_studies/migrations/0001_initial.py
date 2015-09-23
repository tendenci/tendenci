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
            name='CaseStudy',
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
                ('client', models.CharField(max_length=75)),
                ('website', models.URLField(max_length=150)),
                ('slug', models.SlugField(max_length=100)),
                ('overview', models.TextField(null=True, blank=True)),
                ('execution', models.TextField(null=True, blank=True)),
                ('results', models.TextField(null=True, blank=True)),
                ('tags', tagging.fields.TagField(help_text='Tags separated by commas. E.g Tag1, Tag2, Tag3', max_length=255, blank=True)),
                ('creator', models.ForeignKey(related_name='case_studies_casestudy_creator', on_delete=django.db.models.deletion.SET_NULL, default=None, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('entity', models.ForeignKey(related_name='case_studies_casestudy_entity', on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='entities.Entity', null=True)),
                ('owner', models.ForeignKey(related_name='case_studies_casestudy_owner', on_delete=django.db.models.deletion.SET_NULL, default=None, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'Case Study',
                'verbose_name_plural': 'Case Studies',
                'permissions': (('view_casestudy', 'Can view case study'),),
            },
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('file_ptr', models.OneToOneField(related_name='case_studies_image_related', primary_key=True, serialize=False, to='files.File')),
                ('file_type', models.CharField(default=b'other', max_length=50, verbose_name='File type', choices=[(b'featured', b'Featured Screenshot'), (b'screenshot', b'Screenshot'), (b'homepage', b'Homepage Image'), (b'other', b'Other')])),
                ('position', models.IntegerField(blank=True)),
                ('case_study', models.ForeignKey(to='case_studies.CaseStudy')),
            ],
            options={
                'ordering': ('position',),
            },
            bases=('files.file',),
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
            ],
            options={
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='Technology',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True)),
            ],
            options={
                'ordering': ['title'],
                'verbose_name': 'Technology',
                'verbose_name_plural': 'Technologies',
            },
        ),
    ]
