# -*- coding: utf-8 -*-
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
            name='Donation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('guid', models.CharField(max_length=50)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('company', models.CharField(default='', max_length=50, null=True, blank=True)),
                ('address', models.CharField(default='', max_length=100, null=True, blank=True)),
                ('address2', models.CharField(default='', max_length=100, null=True, verbose_name='address line 2', blank=True)),
                ('city', models.CharField(default='', max_length=50, null=True, blank=True)),
                ('state', models.CharField(default='', max_length=50, null=True, blank=True)),
                ('zip_code', models.CharField(default='', max_length=50, null=True, blank=True)),
                ('country', models.CharField(default='', max_length=50, null=True, blank=True)),
                ('email', models.CharField(max_length=50)),
                ('phone', models.CharField(max_length=50)),
                ('referral_source', models.CharField(default='', max_length=200, null=True, verbose_name='referred by', blank=True)),
                ('comments', models.TextField(null=True, blank=True)),
                ('donation_amount', models.DecimalField(max_digits=10, decimal_places=2)),
                ('allocation', models.CharField(default='', max_length=150, null=True, blank=True)),
                ('payment_method', models.CharField(default='cc', max_length=50)),
                ('create_dt', models.DateTimeField(auto_now_add=True)),
                ('creator_username', models.CharField(max_length=50, null=True)),
                ('owner_username', models.CharField(max_length=50, null=True)),
                ('status_detail', models.CharField(default='estimate', max_length=50)),
                ('status', models.NullBooleanField(default=True)),
                ('creator', models.ForeignKey(related_name='donation_creator', to=settings.AUTH_USER_MODEL, null=True, on_delete=django.db.models.deletion.CASCADE)),
                ('invoice', models.ForeignKey(blank=True, to='invoices.Invoice', null=True, on_delete=django.db.models.deletion.CASCADE)),
                ('owner', models.ForeignKey(related_name='donation_owner', to=settings.AUTH_USER_MODEL, null=True, on_delete=django.db.models.deletion.CASCADE)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, on_delete=django.db.models.deletion.CASCADE)),
            ],
            options={'verbose_name': 'Donation', 'verbose_name_plural': 'Donations'},
        ),
    ]
