# -*- coding: utf-8 -*-


from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('entities', '0002_auto_20180315_0857'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='StripeAccount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('allow_anonymous_view', models.BooleanField(default=True, verbose_name='Public can view')),
                ('allow_user_view', models.BooleanField(default=True, verbose_name='Signed in user can view')),
                ('allow_member_view', models.BooleanField(default=True)),
                ('allow_user_edit', models.BooleanField(default=False, verbose_name='Signed in user can change')),
                ('allow_member_edit', models.BooleanField(default=False)),
                ('create_dt', models.DateTimeField(auto_now_add=True, verbose_name='Created On')),
                ('update_dt', models.DateTimeField(auto_now=True, verbose_name='Last Updated')),
                ('creator_username', models.CharField(max_length=50)),
                ('owner_username', models.CharField(max_length=50)),
                ('status', models.BooleanField(default=True, verbose_name=b'Active')),
                ('status_detail', models.CharField(default=b'active', max_length=50)),
                ('account_name', models.CharField(default=b'', max_length=250)),
                ('email', models.CharField(default=b'', max_length=200)),
                ('default_currency', models.CharField(default=b'usd', max_length=5)),
                ('country', models.CharField(default=b'US', max_length=5)),
                ('stripe_user_id', models.CharField(unique=True, max_length=200, verbose_name='Stripe user id')),
                ('scope', models.CharField(max_length=20)),
                ('token_type', models.CharField(max_length=20)),
                ('refresh_token', models.CharField(max_length=200)),
                ('livemode_access_token', models.CharField(max_length=200)),
                ('testmode_access_token', models.CharField(max_length=200)),
                ('livemode_stripe_publishable_key', models.CharField(max_length=200)),
                ('testmode_stripe_publishable_key', models.CharField(max_length=200)),
                ('creator', models.ForeignKey(related_name='stripe_stripeaccount_creator', on_delete=django.db.models.deletion.SET_NULL, default=None, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('entity', models.ForeignKey(related_name='stripe_stripeaccount_entity', on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='entities.Entity', null=True)),
                ('owner', models.ForeignKey(related_name='stripe_stripeaccount_owner', on_delete=django.db.models.deletion.SET_NULL, default=None, to=settings.AUTH_USER_MODEL, null=True)),
                ('user', models.ForeignKey(related_name='stripe_accounts', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
