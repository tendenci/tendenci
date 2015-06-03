# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('entities', '0001_initial'),
        ('invoices', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Discount',
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
                ('discount_code', models.CharField(help_text='Discount codes must be unique.', unique=True, max_length=100)),
                ('start_dt', models.DateTimeField(verbose_name='Start Date/Time')),
                ('end_dt', models.DateTimeField(verbose_name='Start Date/Time')),
                ('never_expires', models.BooleanField(default=False, help_text='Check this box to make the discount code never expire.', verbose_name='Never Expires')),
                ('value', models.DecimalField(help_text='Enter discount value as a positive number.', verbose_name='Discount Value', max_digits=10, decimal_places=2)),
                ('cap', models.IntegerField(default=0, help_text='Enter 0 for unlimited discount code uses.', verbose_name='Maximum Uses')),
                ('apps', models.ManyToManyField(help_text='Select the applications that can use this discount.', to='contenttypes.ContentType', verbose_name='Applications')),
                ('creator', models.ForeignKey(related_name='discounts_discount_creator', on_delete=django.db.models.deletion.SET_NULL, default=None, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('entity', models.ForeignKey(related_name='discounts_discount_entity', on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='entities.Entity', null=True)),
                ('owner', models.ForeignKey(related_name='discounts_discount_owner', on_delete=django.db.models.deletion.SET_NULL, default=None, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'permissions': (('view_discount', 'Can view discount'),),
            },
        ),
        migrations.CreateModel(
            name='DiscountUse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_dt', models.DateTimeField(auto_now_add=True)),
                ('discount', models.ForeignKey(to='discounts.Discount')),
                ('invoice', models.ForeignKey(to='invoices.Invoice')),
            ],
        ),
    ]
