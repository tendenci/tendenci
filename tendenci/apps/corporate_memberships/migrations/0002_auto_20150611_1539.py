# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('corporate_memberships', '0001_initial'),
        ('memberships', '0001_initial'),
        ('events', '0004_auto_20150611_1539'),
        ('entities', '0001_initial'),
        ('industries', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='indivmembershiprenewentry',
            name='membership',
            field=models.ForeignKey(to='memberships.MembershipDefault'),
        ),
        migrations.AddField(
            model_name='indivemailverification',
            name='corp_profile',
            field=models.ForeignKey(to='corporate_memberships.CorpProfile'),
        ),
        migrations.AddField(
            model_name='indivemailverification',
            name='creator',
            field=models.ForeignKey(related_name='corp_email_veri8n_creator', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='indivemailverification',
            name='updated_by',
            field=models.ForeignKey(related_name='corp_email_veri8n_updator', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='freepassesstat',
            name='corp_membership',
            field=models.ForeignKey(related_name='passes_used', to='corporate_memberships.CorpMembership'),
        ),
        migrations.AddField(
            model_name='freepassesstat',
            name='creator',
            field=models.ForeignKey(related_name='corporate_memberships_freepassesstat_creator', on_delete=django.db.models.deletion.SET_NULL, default=None, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='freepassesstat',
            name='entity',
            field=models.ForeignKey(related_name='corporate_memberships_freepassesstat_entity', on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='entities.Entity', null=True),
        ),
        migrations.AddField(
            model_name='freepassesstat',
            name='event',
            field=models.ForeignKey(related_name='passes_used', to='events.Event'),
        ),
        migrations.AddField(
            model_name='freepassesstat',
            name='owner',
            field=models.ForeignKey(related_name='corporate_memberships_freepassesstat_owner', on_delete=django.db.models.deletion.SET_NULL, default=None, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='freepassesstat',
            name='registrant',
            field=models.ForeignKey(to='events.Registrant', null=True),
        ),
        migrations.AddField(
            model_name='freepassesstat',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='corpprofile',
            name='creator',
            field=models.ForeignKey(related_name='corporate_memberships_corpprofile_creator', on_delete=django.db.models.deletion.SET_NULL, default=None, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='corpprofile',
            name='entity',
            field=models.ForeignKey(related_name='corporate_memberships_corpprofile_entity', on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='entities.Entity', null=True),
        ),
        migrations.AddField(
            model_name='corpprofile',
            name='industry',
            field=models.ForeignKey(blank=True, to='industries.Industry', null=True),
        ),
        migrations.AddField(
            model_name='corpprofile',
            name='owner',
            field=models.ForeignKey(related_name='corporate_memberships_corpprofile_owner', on_delete=django.db.models.deletion.SET_NULL, default=None, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
