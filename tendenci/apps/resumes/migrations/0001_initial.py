# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import tendenci.libs.tinymce.models
import tendenci.apps.resumes.models
from django.conf import settings
import tagging.fields
import tendenci.apps.base.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('meta', '0001_initial'),
        ('entities', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Resume',
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
                ('title', models.CharField(max_length=250)),
                ('slug', tendenci.apps.base.fields.SlugField(unique=True, max_length=100, verbose_name='URL Path', db_index=True)),
                ('description', tendenci.libs.tinymce.models.HTMLField()),
                ('location', models.CharField(max_length=500, blank=True)),
                ('skills', models.TextField(blank=True)),
                ('experience', models.TextField(blank=True)),
                ('awards', models.TextField(verbose_name='Awards and Certifications', blank=True)),
                ('education', models.TextField(blank=True)),
                ('is_agency', models.BooleanField(default=False)),
                ('list_type', models.CharField(default=b'regular', max_length=50)),
                ('requested_duration', models.IntegerField(default=30)),
                ('activation_dt', models.DateTimeField(null=True, blank=True)),
                ('expiration_dt', models.DateTimeField(null=True, blank=True)),
                ('resume_url', models.CharField(max_length=300, blank=True)),
                ('resume_file', models.FileField(default=b'', upload_to=tendenci.apps.resumes.models.file_directory, max_length=260, verbose_name='Upload your resume here', blank=True)),
                ('syndicate', models.BooleanField(default=False, verbose_name='Include in RSS feed')),
                ('contact_name', models.CharField(max_length=150, blank=True)),
                ('contact_address', models.CharField(max_length=50, blank=True)),
                ('contact_address2', models.CharField(max_length=50, blank=True)),
                ('contact_city', models.CharField(max_length=50, blank=True)),
                ('contact_state', models.CharField(max_length=50, blank=True)),
                ('contact_zip_code', models.CharField(max_length=50, blank=True)),
                ('contact_country', models.CharField(max_length=50, blank=True)),
                ('contact_phone', models.CharField(max_length=50, blank=True)),
                ('contact_phone2', models.CharField(max_length=50, blank=True)),
                ('contact_fax', models.CharField(max_length=50, blank=True)),
                ('contact_email', models.CharField(max_length=300, blank=True)),
                ('contact_website', models.CharField(max_length=300, blank=True)),
                ('tags', tagging.fields.TagField(max_length=255, blank=True)),
                ('creator', models.ForeignKey(related_name='resumes_resume_creator', on_delete=django.db.models.deletion.SET_NULL, default=None, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('entity', models.ForeignKey(related_name='resumes_resume_entity', on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='entities.Entity', null=True)),
                ('meta', models.OneToOneField(null=True, to='meta.Meta')),
                ('owner', models.ForeignKey(related_name='resumes_resume_owner', on_delete=django.db.models.deletion.SET_NULL, default=None, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'permissions': (('view_resume', 'Can view resume'),),
            },
        ),
    ]
