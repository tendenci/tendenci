# -*- coding: utf-8 -*-


from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('forms', '0003_auto_20170324_1204'),
    ]

    operations = [
        migrations.AlterField(
            model_name='field',
            name='field_function',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='Special Functionality', choices=[('GroupSubscription', 'Subscribe to Group'), ('GroupSubscriptionAuto', 'Subscribe to Group (Auto)'), ('EmailFirstName', 'First Name'), ('EmailLastName', 'Last Name'), ('EmailFullName', 'Full Name'), ('EmailPhoneNumber', 'Phone Number'), ('Recipients', 'Email to Recipients')]),
        ),
        migrations.AlterField(
            model_name='formentry',
            name='payment_method',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='payments.PaymentMethod', null=True),
        ),
        migrations.AlterField(
            model_name='formentry',
            name='pricing',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='forms.Pricing', null=True),
        ),
    ]
