# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stripe', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stripeaccount',
            name='livemode_access_token',
        ),
        migrations.RemoveField(
            model_name='stripeaccount',
            name='livemode_stripe_publishable_key',
        ),
        migrations.RemoveField(
            model_name='stripeaccount',
            name='refresh_token',
        ),
        migrations.RemoveField(
            model_name='stripeaccount',
            name='testmode_access_token',
        ),
        migrations.RemoveField(
            model_name='stripeaccount',
            name='testmode_stripe_publishable_key',
        ),
        migrations.RemoveField(
            model_name='stripeaccount',
            name='token_type',
        ),
    ]
