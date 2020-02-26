# -*- coding: utf-8 -*-


from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0006_remove_event_group'),
    ]

    operations = [
        migrations.AlterField(
            model_name='addon',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='user_groups.Group', null=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='image',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='events.EventPhoto', help_text='Photo that represents this event.', null=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='meta',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='meta.Meta'),
        ),
        migrations.AlterField(
            model_name='event',
            name='place',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='events.Place', null=True),
        ),
        migrations.AlterField(
            model_name='registrant',
            name='pricing',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='events.RegConfPricing', null=True),
        ),
        migrations.AlterField(
            model_name='registration',
            name='invoice',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='invoices.Invoice', null=True),
        ),
        migrations.AlterField(
            model_name='registration',
            name='payment_method',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='payments.PaymentMethod', null=True),
        ),
        migrations.AlterField(
            model_name='registration',
            name='reg_conf_price',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='events.RegConfPricing', null=True),
        ),
        migrations.AlterField(
            model_name='registrationconfiguration',
            name='email',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='emails.Email', null=True),
        ),
    ]
