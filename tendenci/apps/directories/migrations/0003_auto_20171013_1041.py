# -*- coding: utf-8 -*-
from django.db import migrations, models
import tendenci.libs.tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('directories', '0002_auto_20150804_1545'),
    ]

    operations = [
        migrations.AlterField(
            model_name='directory',
            name='body',
            field=tendenci.libs.tinymce.models.HTMLField(verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='directory',
            name='headline',
            field=models.CharField(max_length=200, verbose_name='Name', blank=True),
        ),
    ]
