# -*- coding: utf-8 -*-


from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recurring_payments', '0002_recurringpayment_platform'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recurringpayment',
            name='object_content_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='contenttypes.ContentType', null=True),
        ),
    ]
