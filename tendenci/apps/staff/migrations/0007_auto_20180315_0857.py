# -*- coding: utf-8 -*-


from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0006_auto_20180126_1732'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staff',
            name='department',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='staff.Department', null=True),
        ),
    ]
