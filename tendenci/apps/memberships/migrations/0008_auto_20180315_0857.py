# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('memberships', '0007_membershipdefault_auto_renew'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membershipdefault',
            name='action_taken_user',
            field=models.ForeignKey(related_name='action_taken_set', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='membershipdefault',
            name='application_abandoned_user',
            field=models.ForeignKey(related_name='application_abandond_set', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='membershipdefault',
            name='application_approved_denied_user',
            field=models.ForeignKey(related_name='application_approved_denied_set', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='membershipdefault',
            name='application_approved_user',
            field=models.ForeignKey(related_name='application_approved_set', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='membershipdefault',
            name='application_complete_user',
            field=models.ForeignKey(related_name='application_complete_set', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='membershipdefault',
            name='directory',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='directories.Directory', null=True),
        ),
        migrations.AlterField(
            model_name='membershipdefault',
            name='industry',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='industries.Industry', null=True),
        ),
        migrations.AlterField(
            model_name='membershipdefault',
            name='payment_method',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='payments.PaymentMethod', null=True),
        ),
        migrations.AlterField(
            model_name='membershipdefault',
            name='region',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='regions.Region', null=True),
        ),
        migrations.AlterField(
            model_name='notice',
            name='notice_type',
            field=models.CharField(max_length=20, verbose_name='For Notice Type', choices=[(b'join', 'Join Date'), (b'renewal', 'Renewal Date'), (b'expiration', 'Expiration Date'), (b'approve', 'Join Approval Date'), (b'disapprove', 'Join Disapproval Date'), (b'approve_renewal', 'Renewal Approval Date'), (b'disapprove_renewal', 'Renewal Disapproval Date')]),
        ),
    ]
