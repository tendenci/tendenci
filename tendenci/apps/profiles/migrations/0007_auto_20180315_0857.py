# -*- coding: utf-8 -*-


from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0006_auto_20161025_1814'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='entity',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='entities.Entity', null=True),
        ),
    ]
