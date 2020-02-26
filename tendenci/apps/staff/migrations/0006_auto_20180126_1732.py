# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0005_auto_20180126_1719'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staff',
            name='slug',
            field=models.SlugField(unique=True, max_length=75),
        ),
    ]
