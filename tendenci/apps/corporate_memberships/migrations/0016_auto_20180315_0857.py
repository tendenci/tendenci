# -*- coding: utf-8 -*-
from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('corporate_memberships', '0015_auto_20180114_1155'),
    ]

    operations = [
        migrations.AlterField(
            model_name='corpmembership',
            name='anonymous_creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='corporate_memberships.Creator', null=True),
        ),
        migrations.AlterField(
            model_name='corpmembership',
            name='approved_denied_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='Approved or Denied User', to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterField(
            model_name='corpmembership',
            name='corporate_membership_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='MembershipType', to='corporate_memberships.CorporateMembershipType', null=True),
        ),
        migrations.AlterField(
            model_name='corpmembership',
            name='invoice',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='invoices.Invoice', null=True),
        ),
        migrations.AlterField(
            model_name='corpmembership',
            name='payment_method',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, default=None, verbose_name='Payment Method', to='payments.PaymentMethod', null=True),
        ),
        migrations.AlterField(
            model_name='corpprofile',
            name='industry',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='industries.Industry', null=True),
        ),
        migrations.AlterField(
            model_name='corpprofile',
            name='logo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='files.File', null=True),
        ),
        migrations.AlterField(
            model_name='corpprofile',
            name='parent_entity',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='entities.Entity', null=True),
        ),
        migrations.AlterField(
            model_name='corpprofile',
            name='region',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='regions.Region', null=True),
        ),
        migrations.AlterField(
            model_name='notice',
            name='corporate_membership_type',
            field=models.ForeignKey(blank=True, help_text="Note that if you don't select a corporate membership type, the notice will go out to all members.", null=True, on_delete=django.db.models.deletion.SET_NULL, to='corporate_memberships.CorporateMembershipType'),
        ),
    ]
