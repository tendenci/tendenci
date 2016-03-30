# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tendenci.apps.user_groups.utils
import tendenci.apps.base.fields
import django.db.models.deletion
import tendenci.libs.tinymce.models
from django.conf import settings
import tagging.fields


class Migration(migrations.Migration):

    dependencies = [
        ('user_groups', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('meta', '0001_initial'),
        ('entities', '0001_initial'),
        ('invoices', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Job',
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
                ('list_type', models.CharField(max_length=50)),
                ('code', models.CharField(max_length=50, blank=True)),
                ('location', models.CharField(max_length=500, null=True, blank=True)),
                ('skills', models.TextField(blank=True)),
                ('experience', models.TextField(blank=True)),
                ('education', models.TextField(blank=True)),
                ('level', models.CharField(max_length=50, blank=True)),
                ('period', models.CharField(max_length=50, blank=True)),
                ('is_agency', models.BooleanField(default=False)),
                ('contact_method', models.TextField(blank=True)),
                ('position_reports_to', models.CharField(max_length=200, blank=True)),
                ('salary_from', models.CharField(max_length=50, blank=True)),
                ('salary_to', models.CharField(max_length=50, blank=True)),
                ('computer_skills', models.TextField(blank=True)),
                ('requested_duration', models.IntegerField()),
                ('activation_dt', models.DateTimeField(null=True, blank=True)),
                ('post_dt', models.DateTimeField(null=True, blank=True)),
                ('expiration_dt', models.DateTimeField(null=True, blank=True)),
                ('start_dt', models.DateTimeField(null=True, blank=True)),
                ('job_url', models.CharField(max_length=300, blank=True)),
                ('syndicate', models.BooleanField(default=True, verbose_name='Include in RSS feed')),
                ('design_notes', models.TextField(blank=True)),
                ('contact_company', models.CharField(max_length=300, blank=True)),
                ('contact_name', models.CharField(max_length=150, blank=True)),
                ('contact_address', models.CharField(max_length=50, blank=True)),
                ('contact_address2', models.CharField(max_length=50, blank=True)),
                ('contact_city', models.CharField(max_length=50, blank=True)),
                ('contact_state', models.CharField(max_length=50, blank=True)),
                ('contact_zip_code', models.CharField(max_length=50, blank=True)),
                ('contact_country', models.CharField(max_length=50, blank=True)),
                ('contact_phone', models.CharField(max_length=50, blank=True)),
                ('contact_fax', models.CharField(max_length=50, blank=True)),
                ('contact_email', models.CharField(max_length=300, blank=True)),
                ('contact_website', models.CharField(max_length=300, blank=True)),
                ('tags', tagging.fields.TagField(max_length=255, blank=True)),
                ('payment_method', models.CharField(default=b'', max_length=50, blank=True)),
                ('member_price', models.DecimalField(null=True, max_digits=20, decimal_places=2, blank=True)),
                ('member_count', models.IntegerField(null=True, blank=True)),
                ('non_member_price', models.DecimalField(null=True, max_digits=20, decimal_places=2, blank=True)),
                ('non_member_count', models.IntegerField(null=True, blank=True)),
                ('creator', models.ForeignKey(related_name='jobs_job_creator', on_delete=django.db.models.deletion.SET_NULL, default=None, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('entity', models.ForeignKey(related_name='jobs_job_entity', on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='entities.Entity', null=True)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, default=tendenci.apps.user_groups.utils.get_default_group, to='user_groups.Group', null=True)),
                ('invoice', models.ForeignKey(blank=True, to='invoices.Invoice', null=True)),
                ('meta', models.OneToOneField(null=True, to='meta.Meta')),
                ('owner', models.ForeignKey(related_name='jobs_job_owner', on_delete=django.db.models.deletion.SET_NULL, default=None, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'Job',
                'verbose_name_plural': 'Jobs',
                'permissions': (('view_job', 'Can view job'),),
            },
        ),
        migrations.CreateModel(
            name='JobPricing',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=40, null=True, blank=True)),
                ('guid', models.CharField(max_length=40)),
                ('duration', models.IntegerField(blank=True)),
                ('regular_price', models.DecimalField(default=0, max_digits=15, decimal_places=2, blank=True)),
                ('premium_price', models.DecimalField(default=0, max_digits=15, decimal_places=2, blank=True)),
                ('regular_price_member', models.DecimalField(default=0, max_digits=15, decimal_places=2, blank=True)),
                ('premium_price_member', models.DecimalField(default=0, max_digits=15, decimal_places=2, blank=True)),
                ('show_member_pricing', models.BooleanField(default=False)),
                ('include_tax', models.BooleanField(default=False)),
                ('tax_rate', models.DecimalField(default=0, help_text='Example: 0.0825 for 8.25%.', max_digits=5, decimal_places=4, blank=True)),
                ('create_dt', models.DateTimeField(auto_now_add=True)),
                ('update_dt', models.DateTimeField(auto_now=True)),
                ('creator_username', models.CharField(max_length=50, null=True)),
                ('owner_username', models.CharField(max_length=50, null=True)),
                ('status', models.BooleanField(default=True)),
                ('creator', models.ForeignKey(related_name='job_pricing_creator', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
                ('owner', models.ForeignKey(related_name='job_pricing_owner', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'Job Pricing',
                'verbose_name_plural': 'Job Pricings',
                'permissions': (('view_jobpricing', 'Can view job pricing'),),
            },
        ),
        migrations.AddField(
            model_name='job',
            name='pricing',
            field=models.ForeignKey(to='jobs.JobPricing', null=True),
        ),
    ]
