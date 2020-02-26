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
            name='MakePayment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('guid', models.CharField(max_length=50)),
                ('first_name', models.CharField(max_length=100, null=True)),
                ('last_name', models.CharField(max_length=100, null=True)),
                ('company', models.CharField(default='', max_length=50, null=True, blank=True)),
                ('address', models.CharField(default='', max_length=100, null=True, blank=True)),
                ('address2', models.CharField(default='', max_length=100, null=True, verbose_name='address line 2', blank=True)),
                ('city', models.CharField(default='', max_length=50, null=True, blank=True)),
                ('state', models.CharField(default='', max_length=50, null=True, blank=True)),
                ('zip_code', models.CharField(default='', max_length=50, null=True, blank=True)),
                ('country', models.CharField(default='', max_length=50, null=True, blank=True)),
                ('email', models.CharField(default='', max_length=50, null=True)),
                ('phone', models.CharField(default='', max_length=50, null=True, blank=True)),
                ('referral_source', models.CharField(default='', max_length=200, null=True, verbose_name='referred by', blank=True)),
                ('comments', models.TextField(null=True, blank=True)),
                ('payment_amount', models.DecimalField(max_digits=10, decimal_places=2)),
                ('payment_count', models.IntegerField(null=True, blank=True)),
                ('payment_method', models.CharField(default='cc', max_length=50)),
                ('invoice_id', models.IntegerField(null=True, blank=True)),
                ('create_dt', models.DateTimeField(auto_now_add=True)),
                ('creator_username', models.CharField(max_length=50, null=True)),
                ('owner_username', models.CharField(max_length=50, null=True)),
                ('status_detail', models.CharField(default='estimate', max_length=50)),
                ('status', models.BooleanField(default=True)),
                ('creator', models.ForeignKey(related_name='make_payment_creator', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
                ('owner', models.ForeignKey(related_name='make_payment_owner', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'General Payment',
                'verbose_name_plural': 'General Payments',
            },
        ),
    ]
