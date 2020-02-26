# -*- coding: utf-8 -*-


from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('entities', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entity',
            name='entity_parent',
            field=models.ForeignKey(related_name='entity_children', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='entities.Entity', null=True),
        ),
    ]
