# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tendenci.apps.user_groups.utils
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0001_initial'),
        ('jobs', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('user_groups', '0001_initial'),
        ('invoices', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, default=tendenci.apps.user_groups.utils.get_default_group, to='user_groups.Group', null=True),
        ),
        migrations.AddField(
            model_name='job',
            name='invoice',
            field=models.ForeignKey(blank=True, to='invoices.Invoice', null=True),
        ),
        migrations.AddField(
            model_name='job',
            name='meta',
            field=models.OneToOneField(null=True, to='meta.Meta'),
        ),
        migrations.AddField(
            model_name='job',
            name='owner',
            field=models.ForeignKey(related_name='jobs_job_owner', on_delete=django.db.models.deletion.SET_NULL, default=None, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='job',
            name='pricing',
            field=models.ForeignKey(to='jobs.JobPricing', null=True),
        ),
    ]
