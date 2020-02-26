# -*- coding: utf-8 -*-


from django.db import migrations, models
import django.db.models.deletion
import tendenci.apps.user_groups.utils


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, default=None, to='user_groups.Group', null=True),
        ),
        migrations.AlterField(
            model_name='page',
            name='header_image',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='pages.HeaderImage', null=True),
        ),
        migrations.AlterField(
            model_name='page',
            name='meta',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='meta.Meta'),
        ),
    ]
