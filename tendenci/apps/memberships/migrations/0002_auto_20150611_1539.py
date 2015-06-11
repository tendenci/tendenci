# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('memberships', '0001_initial'),
        ('regions', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('entities', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='membershipdefault',
            name='region',
            field=models.ForeignKey(blank=True, to='regions.Region', null=True),
        ),
        migrations.AddField(
            model_name='membershipdefault',
            name='user',
            field=models.ForeignKey(editable=False, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='membershipappfield',
            name='content_type',
            field=models.ForeignKey(to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='membershipappfield',
            name='membership_app',
            field=models.ForeignKey(related_name='fields', to='memberships.MembershipApp'),
        ),
        migrations.AddField(
            model_name='membershipapp',
            name='creator',
            field=models.ForeignKey(related_name='memberships_membershipapp_creator', on_delete=django.db.models.deletion.SET_NULL, default=None, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='membershipapp',
            name='entity',
            field=models.ForeignKey(related_name='memberships_membershipapp_entity', on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='entities.Entity', null=True),
        ),
        migrations.AddField(
            model_name='membershipapp',
            name='membership_types',
            field=models.ManyToManyField(to='memberships.MembershipType', verbose_name=b'Membership Types'),
        ),
        migrations.AddField(
            model_name='membershipapp',
            name='owner',
            field=models.ForeignKey(related_name='memberships_membershipapp_owner', on_delete=django.db.models.deletion.SET_NULL, default=None, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='membershipapp',
            name='payment_methods',
            field=models.ManyToManyField(to='payments.PaymentMethod', verbose_name='Payment Methods'),
        ),
    ]
