# -*- coding: utf-8 -*-
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0002_auto_20150827_1627'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='release_dt',
            field=models.DateTimeField(null=True, verbose_name='Release Date'),
        ),
    ]
