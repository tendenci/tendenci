# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('corporate_memberships', '0001_initial'),
        ('memberships', '0001_initial'),
        ('events', '0001_initial'),
        ('entities', '0001_initial'),
        ('invoices', '0001_initial'),
        ('industries', '__first__'),
        ('regions', '__first__'),
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
        migrations.AddField(
            model_name='corpprofile',
            name='region',
            field=models.ForeignKey(blank=True, to='regions.Region', null=True),
        ),
        migrations.AddField(
            model_name='corporatemembershiptype',
            name='creator',
            field=models.ForeignKey(related_name='corporate_memberships_corporatemembershiptype_creator', on_delete=django.db.models.deletion.SET_NULL, default=None, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='corporatemembershiptype',
            name='entity',
            field=models.ForeignKey(related_name='corporate_memberships_corporatemembershiptype_entity', on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='entities.Entity', null=True),
        ),
        migrations.AddField(
            model_name='corporatemembershiptype',
            name='membership_type',
            field=models.ForeignKey(help_text='Bind individual memberships to this membership type.', to='memberships.MembershipType'),
        ),
        migrations.AddField(
            model_name='corporatemembershiptype',
            name='owner',
            field=models.ForeignKey(related_name='corporate_memberships_corporatemembershiptype_owner', on_delete=django.db.models.deletion.SET_NULL, default=None, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='corpmembershiprep',
            name='corp_profile',
            field=models.ForeignKey(related_name='reps', to='corporate_memberships.CorpProfile'),
        ),
        migrations.AddField(
            model_name='corpmembershiprep',
            name='user',
            field=models.ForeignKey(verbose_name='Representative', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='corpmembershipimportdata',
            name='mimport',
            field=models.ForeignKey(related_name='corp_membership_import_data', to='corporate_memberships.CorpMembershipImport'),
        ),
        migrations.AddField(
            model_name='corpmembershipimport',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='corpmembershipauthdomain',
            name='corp_profile',
            field=models.ForeignKey(related_name='authorized_domains', to='corporate_memberships.CorpProfile'),
        ),
        migrations.AddField(
            model_name='corpmembershipappfield',
            name='corp_app',
            field=models.ForeignKey(related_name='fields', to='corporate_memberships.CorpMembershipApp'),
        ),
        migrations.AddField(
            model_name='corpmembershipapp',
            name='corp_memb_type',
            field=models.ManyToManyField(to='corporate_memberships.CorporateMembershipType', verbose_name='Corp. Memb. Type'),
        ),
        migrations.AddField(
            model_name='corpmembershipapp',
            name='creator',
            field=models.ForeignKey(related_name='corporate_memberships_corpmembershipapp_creator', on_delete=django.db.models.deletion.SET_NULL, default=None, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='corpmembershipapp',
            name='entity',
            field=models.ForeignKey(related_name='corporate_memberships_corpmembershipapp_entity', on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='entities.Entity', null=True),
        ),
        migrations.AddField(
            model_name='corpmembershipapp',
            name='memb_app',
            field=models.OneToOneField(related_name='corp_app', default=1, to='memberships.MembershipApp', help_text='App for individual memberships.', verbose_name='Membership Application'),
        ),
        migrations.AddField(
            model_name='corpmembershipapp',
            name='owner',
            field=models.ForeignKey(related_name='corporate_memberships_corpmembershipapp_owner', on_delete=django.db.models.deletion.SET_NULL, default=None, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='corpmembershipapp',
            name='payment_methods',
            field=models.ManyToManyField(to='payments.PaymentMethod', verbose_name=b'Payment Methods'),
        ),
        migrations.AddField(
            model_name='corpmembership',
            name='anonymous_creator',
            field=models.ForeignKey(to='corporate_memberships.Creator', null=True),
        ),
        migrations.AddField(
            model_name='corpmembership',
            name='approved_denied_user',
            field=models.ForeignKey(verbose_name='Approved or Denied User', to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='corpmembership',
            name='corp_profile',
            field=models.ForeignKey(related_name='corp_memberships', to='corporate_memberships.CorpProfile'),
        ),
        migrations.AddField(
            model_name='corpmembership',
            name='corporate_membership_type',
            field=models.ForeignKey(verbose_name='MembershipType', to='corporate_memberships.CorporateMembershipType'),
        ),
        migrations.AddField(
            model_name='corpmembership',
            name='creator',
            field=models.ForeignKey(related_name='corporate_memberships_corpmembership_creator', on_delete=django.db.models.deletion.SET_NULL, default=None, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='corpmembership',
            name='entity',
            field=models.ForeignKey(related_name='corporate_memberships_corpmembership_entity', on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='entities.Entity', null=True),
        ),
        migrations.AddField(
            model_name='corpmembership',
            name='invoice',
            field=models.ForeignKey(blank=True, to='invoices.Invoice', null=True),
        ),
        migrations.AddField(
            model_name='corpmembership',
            name='owner',
            field=models.ForeignKey(related_name='corporate_memberships_corpmembership_owner', on_delete=django.db.models.deletion.SET_NULL, default=None, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='corpmembership',
            name='payment_method',
            field=models.ForeignKey(default=None, verbose_name='Payment Method', to='payments.PaymentMethod', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='corpmembershiprep',
            unique_together=set([('corp_profile', 'user')]),
        ),
    ]
