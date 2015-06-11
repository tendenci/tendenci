# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tendenci.apps.user_groups.utils
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('meta', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('user_groups', '0001_initial'),
        ('entities', '0001_initial'),
        ('photos', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='photoset',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, default=tendenci.apps.user_groups.utils.get_default_group, to='user_groups.Group', null=True),
        ),
        migrations.AddField(
            model_name='photoset',
            name='owner',
            field=models.ForeignKey(related_name='photos_photoset_owner', on_delete=django.db.models.deletion.SET_NULL, default=None, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='image',
            name='creator',
            field=models.ForeignKey(related_name='photos_image_creator', on_delete=django.db.models.deletion.SET_NULL, default=None, editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='image',
            name='effect',
            field=models.ForeignKey(related_name='image_related', verbose_name='effect', blank=True, to='photos.PhotoEffect', null=True),
        ),
        migrations.AddField(
            model_name='image',
            name='entity',
            field=models.ForeignKey(related_name='photos_image_entity', on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='entities.Entity', null=True),
        ),
        migrations.AddField(
            model_name='image',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, default=tendenci.apps.user_groups.utils.get_default_group, blank=True, to='user_groups.Group', null=True),
        ),
        migrations.AddField(
            model_name='image',
            name='license',
            field=models.ForeignKey(blank=True, to='photos.License', null=True),
        ),
        migrations.AddField(
            model_name='image',
            name='member',
            field=models.ForeignKey(related_name='added_photos', on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='image',
            name='meta',
            field=models.OneToOneField(null=True, blank=True, to='meta.Meta'),
        ),
        migrations.AddField(
            model_name='image',
            name='owner',
            field=models.ForeignKey(related_name='photos_image_owner', on_delete=django.db.models.deletion.SET_NULL, default=None, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='image',
            name='photoset',
            field=models.ManyToManyField(to='photos.PhotoSet', verbose_name='photo set', blank=True),
        ),
        migrations.AddField(
            model_name='albumcover',
            name='photo',
            field=models.ForeignKey(to='photos.Image'),
        ),
        migrations.AddField(
            model_name='albumcover',
            name='photoset',
            field=models.OneToOneField(to='photos.PhotoSet'),
        ),
        migrations.AlterUniqueTogether(
            name='pool',
            unique_together=set([('photo', 'content_type', 'object_id')]),
        ),
    ]
