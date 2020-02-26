# -*- coding: utf-8 -*-
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0005_auto_20170608_1523'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='videotype',
            options={'ordering': ('name',), 'verbose_name_plural': 'Video Types'},
        ),
        migrations.AddField(
            model_name='video',
            name='position',
            field=models.IntegerField(default=0, null=True, verbose_name='Position', blank=True),
        ),
    ]
