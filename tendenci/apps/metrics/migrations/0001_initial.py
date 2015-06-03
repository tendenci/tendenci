# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Metric',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('users', models.IntegerField(verbose_name='users')),
                ('members', models.IntegerField(verbose_name='members')),
                ('visits', models.IntegerField(verbose_name='visits')),
                ('disk_usage', models.BigIntegerField(verbose_name='disk usage')),
                ('invoices', models.IntegerField(null=True, verbose_name='invoices')),
                ('positive_invoices', models.IntegerField(null=True, verbose_name='invoices with a total that is not 0')),
                ('invoice_totals', models.DecimalField(null=True, verbose_name="sum of invoices' totals", max_digits=12, decimal_places=2)),
                ('create_dt', models.DateTimeField(auto_now_add=True, verbose_name='create date/time')),
            ],
        ),
    ]
