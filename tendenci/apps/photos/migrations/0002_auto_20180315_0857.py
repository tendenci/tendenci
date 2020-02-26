# -*- coding: utf-8 -*-


from django.db import migrations, models
import tendenci.apps.user_groups.utils
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('photos', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='effect',
            field=models.ForeignKey(related_name='image_related', on_delete=django.db.models.deletion.SET_NULL, verbose_name='effect', blank=True, to='photos.PhotoEffect', null=True),
        ),
        migrations.AlterField(
            model_name='image',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='user_groups.Group', null=True),
        ),
        migrations.AlterField(
            model_name='image',
            name='license',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='photos.License', null=True),
        ),
        migrations.AlterField(
            model_name='image',
            name='meta',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True, to='meta.Meta'),
        ),
        migrations.AlterField(
            model_name='photoset',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, default=None, to='user_groups.Group', null=True),
        ),
    ]
