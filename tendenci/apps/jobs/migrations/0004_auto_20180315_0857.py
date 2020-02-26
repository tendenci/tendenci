# -*- coding: utf-8 -*-


from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0003_auto_20170910_1702'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='invoice',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='invoices.Invoice', null=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='pricing',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='jobs.JobPricing', null=True),
        ),
    ]
