# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recurring_payments', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='recurringpayment',
            name='platform',
            field=models.CharField(default='authorizenet', max_length=50, blank=True),
        ),
    ]
