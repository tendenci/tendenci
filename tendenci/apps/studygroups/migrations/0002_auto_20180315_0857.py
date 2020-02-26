# -*- coding: utf-8 -*-


from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('studygroups', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studygroup',
            name='header_image',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='pages.HeaderImage', null=True),
        ),
        migrations.AlterField(
            model_name='studygroup',
            name='meta',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='meta.Meta'),
        ),
    ]
