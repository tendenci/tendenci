# -*- coding: utf-8 -*-
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0001_initial'),
        ('corporate_memberships', '0007_auto_20160927_1706'),
    ]

    operations = [
        migrations.AddField(
            model_name='corpprofile',
            name='logo',
            field=models.ForeignKey(to='files.File', null=True, on_delete=django.db.models.deletion.CASCADE),
        ),
    ]
