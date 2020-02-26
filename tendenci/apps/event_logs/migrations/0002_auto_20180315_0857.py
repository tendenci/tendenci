# -*- coding: utf-8 -*-


from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('event_logs', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventlog',
            name='entity',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='entities.Entity', null=True),
        ),
    ]
