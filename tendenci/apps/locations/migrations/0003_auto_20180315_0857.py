# -*- coding: utf-8 -*-


from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0002_auto_20170328_1659'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='logo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, default=None, to='files.File', help_text='Only jpg, gif, or png images.', null=True),
        ),
    ]
