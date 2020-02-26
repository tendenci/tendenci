# -*- coding: utf-8 -*-
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('committees', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='committee',
            name='header_image',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='pages.HeaderImage', null=True),
        ),
        migrations.AlterField(
            model_name='committee',
            name='meta',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='meta.Meta'),
        ),
    ]
