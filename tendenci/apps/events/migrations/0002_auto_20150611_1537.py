# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('events', '0001_initial'),
        ('invoices', '0001_initial'),
        ('emails', '__first__'),
        ('files', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventPhoto',
            fields=[
                ('file_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='files.File')),
            ],
            options={
                'abstract': False,
            },
            bases=('files.file',),
        ),
        migrations.CreateModel(
            name='Organizer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, blank=True)),
                ('description', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='PaymentMethod',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, blank=True)),
                ('description', models.TextField(blank=True)),
                ('address', models.CharField(max_length=150, blank=True)),
                ('city', models.CharField(max_length=150, blank=True)),
                ('state', models.CharField(max_length=150, blank=True)),
                ('zip', models.CharField(max_length=150, blank=True)),
                ('country', models.CharField(max_length=150, blank=True)),
                ('url', models.URLField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='RecurringEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('repeat_type', models.IntegerField(verbose_name='Repeats', choices=[(1, 'Day(s)'), (2, 'Week(s)'), (3, 'Month(s)'), (4, 'Year(s)')])),
                ('frequency', models.IntegerField(verbose_name='Repeats every')),
                ('starts_on', models.DateTimeField(default=datetime.datetime(2015, 7, 11, 15, 37, 20, 952743))),
                ('ends_on', models.DateTimeField()),
            ],
            options={
                'verbose_name': 'Recurring Event',
                'verbose_name_plural': 'Recurring Events',
            },
        ),
        migrations.CreateModel(
            name='RegAddon',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.DecimalField(default=0, verbose_name='Amount', max_digits=21, decimal_places=2)),
                ('create_dt', models.DateTimeField(auto_now_add=True)),
                ('update_dt', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='RegAddonOption',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='RegConfPricing',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('position', models.IntegerField(default=0, null=True, verbose_name='Position', blank=True)),
                ('title', models.CharField(max_length=500, verbose_name='Pricing display name', blank=True)),
                ('description', models.TextField(verbose_name='Pricing description', blank=True)),
                ('quantity', models.IntegerField(default=1, help_text=b'Total people included in each registration for this pricing group. Ex: Table or Team.', verbose_name='Number of attendees', blank=True)),
                ('price', models.DecimalField(default=0, verbose_name='Price', max_digits=21, decimal_places=2)),
                ('include_tax', models.BooleanField(default=False)),
                ('tax_rate', models.DecimalField(default=0, help_text='Example: 0.0825 for 8.25%.', max_digits=5, decimal_places=4, blank=True)),
                ('payment_required', models.BooleanField(default=False, help_text='A payment required before registration is accepted.')),
                ('start_dt', models.DateTimeField(verbose_name='Start Date')),
                ('end_dt', models.DateTimeField(verbose_name='End Date')),
                ('allow_anonymous', models.BooleanField(default=False, verbose_name='Public can use this pricing')),
                ('allow_user', models.BooleanField(default=False, verbose_name='Signed in user can use this pricing')),
                ('allow_member', models.BooleanField(default=False, verbose_name='All members can use this pricing')),
                ('status', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ('position',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Registrant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('amount', models.DecimalField(default=0, verbose_name='Amount', max_digits=21, decimal_places=2, blank=True)),
                ('name', models.CharField(max_length=100)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('mail_name', models.CharField(max_length=100, blank=True)),
                ('address', models.CharField(max_length=200, blank=True)),
                ('city', models.CharField(max_length=100, blank=True)),
                ('state', models.CharField(max_length=100, blank=True)),
                ('zip', models.CharField(max_length=50, blank=True)),
                ('country', models.CharField(max_length=100, blank=True)),
                ('phone', models.CharField(max_length=50, blank=True)),
                ('email', models.CharField(max_length=100)),
                ('groups', models.CharField(max_length=100)),
                ('position_title', models.CharField(max_length=100, blank=True)),
                ('company_name', models.CharField(max_length=100, blank=True)),
                ('meal_option', models.CharField(default=b'', max_length=200, blank=True)),
                ('comments', models.TextField(default=b'', blank=True)),
                ('is_primary', models.BooleanField(default=False, verbose_name='Is primary registrant')),
                ('override', models.BooleanField(default=False, verbose_name='Admin Price Override?')),
                ('override_price', models.DecimalField(default=0, verbose_name='Override Price', max_digits=21, decimal_places=2, blank=True)),
                ('discount_amount', models.DecimalField(default=0, verbose_name='Discount Amount', max_digits=10, decimal_places=2)),
                ('cancel_dt', models.DateTimeField(null=True, editable=False)),
                ('memberid', models.CharField(max_length=50, null=True, verbose_name='Member ID', blank=True)),
                ('use_free_pass', models.BooleanField(default=False)),
                ('checked_in', models.BooleanField(default=False, verbose_name='Is Checked In?')),
                ('checked_in_dt', models.DateTimeField(null=True)),
                ('reminder', models.BooleanField(default=False, verbose_name='Receive event reminders')),
                ('create_dt', models.DateTimeField(auto_now_add=True)),
                ('update_dt', models.DateTimeField(auto_now=True)),
                ('custom_reg_form_entry', models.ForeignKey(related_name='registrants', to='events.CustomRegFormEntry', null=True)),
                ('pricing', models.ForeignKey(to='events.RegConfPricing', null=True)),
            ],
            options={
                'permissions': (('view_registrant', 'Can view registrant'),),
            },
        ),
        migrations.CreateModel(
            name='Registration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('guid', models.TextField(max_length=40, editable=False)),
                ('note', models.TextField(blank=True)),
                ('reminder', models.BooleanField(default=False)),
                ('amount_paid', models.DecimalField(verbose_name='Amount Paid', max_digits=21, decimal_places=2)),
                ('is_table', models.BooleanField(default=False, verbose_name='Is table registration')),
                ('quantity', models.IntegerField(default=1, verbose_name='Number of registrants for a table')),
                ('override_table', models.BooleanField(default=False, verbose_name='Admin Price Override?')),
                ('override_price_table', models.DecimalField(default=0, verbose_name='Override Price', max_digits=21, decimal_places=2, blank=True)),
                ('canceled', models.BooleanField(default=False, verbose_name='Canceled')),
                ('create_dt', models.DateTimeField(auto_now_add=True)),
                ('update_dt', models.DateTimeField(auto_now=True)),
                ('addons_added', models.TextField(null=True, blank=True)),
                ('creator', models.ForeignKey(related_name='created_registrations', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
                ('event', models.ForeignKey(to='events.Event')),
                ('invoice', models.ForeignKey(blank=True, to='invoices.Invoice', null=True)),
                ('owner', models.ForeignKey(related_name='owned_registrations', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
                ('payment_method', models.ForeignKey(to='payments.PaymentMethod', null=True)),
                ('reg_conf_price', models.ForeignKey(to='events.RegConfPricing', null=True)),
            ],
            options={
                'permissions': (('view_registration', 'Can view registration'),),
            },
        ),
        migrations.CreateModel(
            name='RegistrationConfiguration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('payment_required', models.BooleanField(default=True, help_text='A payment required before registration is accepted.')),
                ('limit', models.IntegerField(default=0, verbose_name='Registration Limit')),
                ('enabled', models.BooleanField(default=False, verbose_name='Enable Registration')),
                ('require_guests_info', models.BooleanField(default=False, help_text='If checked, the required fields in registration form are also required for guests.  ', verbose_name='Require Guests Info')),
                ('is_guest_price', models.BooleanField(default=False, verbose_name='Guests Pay Registrant Price')),
                ('discount_eligible', models.BooleanField(default=True)),
                ('allow_free_pass', models.BooleanField(default=False)),
                ('display_registration_stats', models.BooleanField(default=False, help_text=b'Display the number of spots registered and the number of spots left to the public.', verbose_name='Publicly Show Registration Stats')),
                ('use_custom_reg_form', models.BooleanField(default=False, verbose_name='Use Custom Registration Form')),
                ('bind_reg_form_to_conf_only', models.BooleanField(default=True, verbose_name=' ', choices=[(True, 'Use one form for all pricings'), (False, 'Use separate form for each pricing')])),
                ('send_reminder', models.BooleanField(default=False, verbose_name='Send Email Reminder to attendees')),
                ('reminder_days', models.CharField(help_text='Comma delimited. Ex: 7,1', max_length=20, null=True, verbose_name='Specify when (? days before the event starts) the reminder should be sent ', blank=True)),
                ('registration_email_type', models.CharField(default=b'default', max_length=20, verbose_name='Registration Email', choices=[(b'default', 'Default Email Only'), (b'custom', 'Custom Email Only'), (b'both', 'Default and Custom Email')])),
                ('registration_email_text', models.TextField(verbose_name='Registration Email Text', blank=True)),
                ('create_dt', models.DateTimeField(auto_now_add=True)),
                ('update_dt', models.DateTimeField(auto_now=True)),
                ('email', models.ForeignKey(to='emails.Email', null=True)),
                ('payment_method', models.ManyToManyField(to='payments.PaymentMethod')),
                ('reg_form', models.ForeignKey(related_name='regconfs', blank=True, to='events.CustomRegForm', help_text="You'll have the chance to edit the selected form", null=True, verbose_name='Custom Registration Form')),
            ],
        ),
        migrations.CreateModel(
            name='Speaker',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='Speaker Name', blank=True)),
                ('description', models.TextField(blank=True)),
                ('featured', models.BooleanField(default=False, help_text='All speakers marked as featured will be displayed when viewing the event.')),
                ('event', models.ManyToManyField(to='events.Event', blank=True)),
                ('user', models.OneToOneField(null=True, blank=True, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Sponsor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('event', models.ManyToManyField(to='events.Event')),
            ],
        ),
        migrations.CreateModel(
            name='Type',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('slug', models.SlugField(editable=False)),
            ],
        ),
        migrations.CreateModel(
            name='TypeColorSet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fg_color', models.CharField(max_length=20)),
                ('bg_color', models.CharField(max_length=20)),
                ('border_color', models.CharField(max_length=20)),
            ],
        ),
        migrations.AddField(
            model_name='type',
            name='color_set',
            field=models.ForeignKey(to='events.TypeColorSet'),
        ),
        migrations.AddField(
            model_name='registrant',
            name='registration',
            field=models.ForeignKey(to='events.Registration'),
        ),
        migrations.AddField(
            model_name='registrant',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
