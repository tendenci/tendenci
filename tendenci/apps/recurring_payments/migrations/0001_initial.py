# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('payments', '0001_initial'),
        ('invoices', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('customer_profile_id', models.CharField(max_length=100)),
                ('payment_profile_id', models.CharField(unique=True, max_length=100)),
                ('card_type', models.CharField(max_length=50, null=True)),
                ('card_num', models.CharField(max_length=4, null=True)),
                ('expiration_dt', models.DateTimeField(null=True, blank=True)),
                ('create_dt', models.DateTimeField(auto_now_add=True)),
                ('update_dt', models.DateTimeField(auto_now=True)),
                ('creator_username', models.CharField(max_length=50, null=True)),
                ('owner_username', models.CharField(max_length=50, null=True)),
                ('status_detail', models.CharField(default=b'active', max_length=50)),
                ('status', models.BooleanField(default=True)),
                ('creator', models.ForeignKey(related_name='payment_profile_creator', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
                ('owner', models.ForeignKey(related_name='payment_profile_owner', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='PaymentTransaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('payment_profile_id', models.CharField(default=b'', max_length=100)),
                ('trans_type', models.CharField(max_length=50, null=True)),
                ('amount', models.DecimalField(max_digits=15, decimal_places=2)),
                ('result_code', models.CharField(default=b'', max_length=10)),
                ('message_code', models.CharField(default=b'', max_length=20)),
                ('message_text', models.CharField(default=b'', max_length=200)),
                ('create_dt', models.DateTimeField(auto_now_add=True)),
                ('status', models.BooleanField(default=True)),
                ('creator', models.ForeignKey(related_name='payment_transaction_creator', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
                ('payment', models.ForeignKey(to='payments.Payment', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='RecurringPayment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('guid', models.CharField(max_length=50)),
                ('customer_profile_id', models.CharField(default=b'', max_length=100)),
                ('url', models.CharField(default=b'', max_length=100, null=True, verbose_name='Website URL', blank=True)),
                ('description', models.CharField(help_text='Use a short term, example: web hosting', max_length=100, verbose_name='Description')),
                ('object_content_id', models.IntegerField(default=0, null=True, blank=True)),
                ('billing_period', models.CharField(default=b'month', max_length=50, choices=[(b'month', 'Month(s)'), (b'year', 'Year(s)'), (b'week', 'Week(s)'), (b'day', 'Day(s)')])),
                ('billing_frequency', models.IntegerField(default=1)),
                ('billing_start_dt', models.DateTimeField(help_text='The initial start date for the recurring payments.That is, the start date of the first billing cycle.', verbose_name='Initial billing cycle start date')),
                ('num_days', models.IntegerField(default=0)),
                ('due_sore', models.CharField(default=b'start', max_length=20, verbose_name='Billing cycle start or end date', choices=[(b'start', 'start'), (b'end', 'end')])),
                ('payment_amount', models.DecimalField(max_digits=15, decimal_places=2)),
                ('tax_exempt', models.BooleanField(default=True)),
                ('taxable', models.BooleanField(default=False)),
                ('tax_rate', models.DecimalField(default=0, help_text='Example: 0.0825 for 8.25%.', max_digits=7, decimal_places=6, blank=True)),
                ('has_trial_period', models.BooleanField(default=False)),
                ('trial_period_start_dt', models.DateTimeField(null=True, verbose_name='Trial period start date', blank=True)),
                ('trial_period_end_dt', models.DateTimeField(null=True, verbose_name='Trial period end date', blank=True)),
                ('trial_amount', models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True)),
                ('next_billing_dt', models.DateTimeField(null=True, blank=True)),
                ('last_payment_received_dt', models.DateTimeField(null=True, blank=True)),
                ('num_billing_cycle_completed', models.IntegerField(default=0, blank=True)),
                ('num_billing_cycle_failed', models.IntegerField(default=0, blank=True)),
                ('current_balance', models.DecimalField(default=0, max_digits=15, decimal_places=2)),
                ('outstanding_balance', models.DecimalField(default=0, max_digits=15, decimal_places=2)),
                ('create_dt', models.DateTimeField(auto_now_add=True)),
                ('update_dt', models.DateTimeField(auto_now=True)),
                ('creator_username', models.CharField(max_length=50, null=True)),
                ('owner_username', models.CharField(max_length=50, null=True)),
                ('status_detail', models.CharField(default=b'active', max_length=50, choices=[(b'active', 'Active'), (b'inactive', 'Inactive'), (b'disabled', 'Disabled')])),
                ('status', models.BooleanField(default=True)),
                ('creator', models.ForeignKey(related_name='recurring_payment_creator', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
                ('object_content_type', models.ForeignKey(blank=True, to='contenttypes.ContentType', null=True)),
                ('owner', models.ForeignKey(related_name='recurring_payment_owner', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
                ('user', models.ForeignKey(related_name='recurring_payment_user', on_delete=django.db.models.deletion.SET_NULL, verbose_name='Customer', to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='RecurringPaymentInvoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('billing_cycle_start_dt', models.DateTimeField(null=True, verbose_name='Billing cycle start date', blank=True)),
                ('billing_cycle_end_dt', models.DateTimeField(null=True, verbose_name='Billing cycle end date', blank=True)),
                ('last_payment_failed_dt', models.DateTimeField(null=True, verbose_name='Last payment failed date', blank=True)),
                ('billing_dt', models.DateTimeField(null=True, blank=True)),
                ('payment_received_dt', models.DateTimeField(null=True, blank=True)),
                ('create_dt', models.DateTimeField(auto_now_add=True)),
                ('invoice', models.ForeignKey(blank=True, to='invoices.Invoice', null=True)),
                ('recurring_payment', models.ForeignKey(related_name='rp_invoices', to='recurring_payments.RecurringPayment')),
            ],
        ),
        migrations.AddField(
            model_name='paymenttransaction',
            name='recurring_payment',
            field=models.ForeignKey(related_name='transactions', to='recurring_payments.RecurringPayment'),
        ),
        migrations.AddField(
            model_name='paymenttransaction',
            name='recurring_payment_invoice',
            field=models.ForeignKey(related_name='transactions', to='recurring_payments.RecurringPaymentInvoice'),
        ),
    ]
