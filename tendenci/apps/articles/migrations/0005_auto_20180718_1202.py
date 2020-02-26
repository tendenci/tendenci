# -*- coding: utf-8 -*-
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0001_initial'),
        ('articles', '0004_auto_20180315_1839'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='thumbnail',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='files.File', help_text='The thumbnail image can be used on your homepage or sidebar if it is setup in your theme. The thumbnail image will not display on the news page.', null=True),
        ),
    ]
