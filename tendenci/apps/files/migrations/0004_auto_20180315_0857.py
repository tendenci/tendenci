# -*- coding: utf-8 -*-


from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0003_auto_20160309_2123'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='content_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='contenttypes.ContentType', null=True),
        ),
    ]
