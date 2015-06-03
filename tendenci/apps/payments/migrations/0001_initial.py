# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('invoices', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('guid', models.CharField(max_length=50)),
                ('payment_attempted', models.BooleanField(default=True)),
                ('response_code', models.CharField(default=b'', max_length=2)),
                ('response_subcode', models.CharField(default=b'', max_length=10)),
                ('response_reason_code', models.CharField(default=b'', max_length=15)),
                ('response_reason_text', models.TextField(default=b'')),
                ('response_page', models.CharField(max_length=200)),
                ('trans_id', models.CharField(default=b'', max_length=100)),
                ('trans_string', models.CharField(max_length=100)),
                ('card_type', models.CharField(default=b'', max_length=50, null=True)),
                ('account_number', models.CharField(default=b'', max_length=4, null=True)),
                ('po_num', models.CharField(max_length=50, blank=True)),
                ('auth_code', models.CharField(max_length=10)),
                ('avs_code', models.CharField(max_length=10)),
                ('amount', models.DecimalField(max_digits=15, decimal_places=2)),
                ('invoice_num', models.CharField(max_length=20, blank=True)),
                ('description', models.CharField(max_length=1600)),
                ('first_name', models.CharField(default=b'', max_length=100, null=True, blank=True)),
                ('last_name', models.CharField(default=b'', max_length=100, null=True, blank=True)),
                ('company', models.CharField(default=b'', max_length=100, null=True, blank=True)),
                ('address', models.CharField(default=b'', max_length=250, null=True, blank=True)),
                ('address2', models.CharField(default=b'', max_length=100, null=True, blank=True)),
                ('city', models.CharField(default=b'', max_length=50, null=True, blank=True)),
                ('state', models.CharField(default=b'', max_length=50, null=True, blank=True)),
                ('zip', models.CharField(default=b'', max_length=20, null=True, blank=True)),
                ('country', models.CharField(default=b'', max_length=60, null=True, blank=True)),
                ('phone', models.CharField(default=b'', max_length=50, null=True, blank=True)),
                ('fax', models.CharField(default=b'', max_length=50, null=True, blank=True)),
                ('email', models.CharField(default=b'', max_length=255, null=True, blank=True)),
                ('ship_to_first_name', models.CharField(default=b'', max_length=100, null=True)),
                ('ship_to_last_name', models.CharField(default=b'', max_length=100, null=True)),
                ('ship_to_company', models.CharField(default=b'', max_length=100, null=True)),
                ('ship_to_address', models.CharField(default=b'', max_length=250, null=True)),
                ('ship_to_city', models.CharField(default=b'', max_length=50, null=True)),
                ('ship_to_state', models.CharField(default=b'', max_length=50, null=True)),
                ('ship_to_zip', models.CharField(default=b'', max_length=20, null=True)),
                ('ship_to_country', models.CharField(default=b'', max_length=60, null=True)),
                ('method', models.CharField(max_length=50)),
                ('freight', models.CharField(max_length=16, blank=True)),
                ('tax_exempt', models.CharField(max_length=16, blank=True)),
                ('md5_hash', models.CharField(max_length=255)),
                ('payment_type', models.CharField(max_length=20)),
                ('cust_id', models.CharField(default=0, max_length=20)),
                ('tax', models.CharField(max_length=16, blank=True)),
                ('duty', models.CharField(max_length=16, blank=True)),
                ('verified', models.BooleanField(default=False)),
                ('submit_dt', models.DateTimeField(null=True, blank=True)),
                ('create_dt', models.DateTimeField(auto_now_add=True)),
                ('update_dt', models.DateTimeField(auto_now=True)),
                ('creator_username', models.CharField(max_length=50, null=True)),
                ('owner_username', models.CharField(max_length=50, null=True)),
                ('status_detail', models.CharField(default=b'', max_length=50)),
                ('status', models.BooleanField(default=True)),
                ('creator', models.ForeignKey(related_name='payment_creator', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
                ('invoice', models.ForeignKey(to='invoices.Invoice')),
                ('owner', models.ForeignKey(related_name='payment_owner', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('human_name', models.CharField(max_length=200)),
                ('machine_name', models.CharField(max_length=200)),
                ('is_online', models.BooleanField(default=False)),
                ('admin_only', models.BooleanField(default=False, help_text='if checked, it will only show for administrators')),
            ],
        ),
    ]
