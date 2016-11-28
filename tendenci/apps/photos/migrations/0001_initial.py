# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import tagging.fields
import tendenci.apps.photos.models
import tendenci.apps.user_groups.utils
from django.conf import settings
import django.db.models.deletion
import tendenci.apps.base.fields


class Migration(migrations.Migration):

    dependencies = [
        ('user_groups', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('meta', '0001_initial'),
        ('entities', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AlbumCover',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('allow_anonymous_view', models.BooleanField(default=True, verbose_name='Public can view')),
                ('allow_user_view', models.BooleanField(default=True, verbose_name='Signed in user can view')),
                ('allow_member_view', models.BooleanField(default=True)),
                ('allow_user_edit', models.BooleanField(default=False, verbose_name='Signed in user can change')),
                ('allow_member_edit', models.BooleanField(default=False)),
                ('create_dt', models.DateTimeField(auto_now_add=True, verbose_name='Created On')),
                ('update_dt', models.DateTimeField(auto_now=True, verbose_name='Last Updated')),
                ('creator_username', models.CharField(max_length=50)),
                ('owner_username', models.CharField(max_length=50)),
                ('status', models.BooleanField(default=True, verbose_name=b'Active')),
                ('status_detail', models.CharField(default=b'active', max_length=50)),
                ('position', models.IntegerField(default=0, null=True, verbose_name='Position', blank=True)),
                ('image', models.ImageField(upload_to=tendenci.apps.photos.models.get_storage_path, verbose_name='image')),
                ('date_taken', models.DateTimeField(verbose_name='date taken', null=True, editable=False, blank=True)),
                ('view_count', models.PositiveIntegerField(default=0, editable=False)),
                ('crop_from', models.CharField(default=b'center', max_length=10, verbose_name='crop from', blank=True, choices=[(b'top', 'Top'), (b'right', 'Right'), (b'bottom', 'Bottom'), (b'left', 'Left'), (b'center', 'Center (Default)')])),
                ('guid', models.CharField(max_length=40, editable=False)),
                ('title', models.CharField(max_length=200, verbose_name='title')),
                ('title_slug', models.SlugField(verbose_name='slug')),
                ('caption', models.TextField(verbose_name='caption', blank=True)),
                ('date_added', models.DateTimeField(auto_now_add=True, verbose_name='date added')),
                ('is_public', models.BooleanField(default=True, help_text='Public photographs will be displayed in the default views.', verbose_name='public')),
                ('safetylevel', models.IntegerField(default=3, verbose_name='safety level', choices=[(1, 'Safe'), (2, 'Not Safe')])),
                ('tags', tagging.fields.TagField(help_text='Comma delimited (eg. mickey, donald, goofy)', max_length=255, blank=True)),
                ('exif_data', tendenci.apps.base.fields.DictField(null=True, verbose_name='exif')),
                ('photographer', models.CharField(max_length=100, null=True, verbose_name='Photographer', blank=True)),
                ('creator', models.ForeignKey(related_name='photos_image_creator', on_delete=django.db.models.deletion.SET_NULL, default=None, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'permissions': (('view_image', 'Can view image'),),
            },
        ),
        migrations.CreateModel(
            name='License',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200, verbose_name='name')),
                ('code', models.CharField(max_length=200, verbose_name='code', blank=True)),
                ('author', models.CharField(max_length=200, verbose_name='author', blank=True)),
                ('deed', models.URLField(verbose_name='license deed', blank=True)),
                ('legal_code', models.URLField(verbose_name='legal code', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='PhotoEffect',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=30, verbose_name='name')),
                ('description', models.TextField(verbose_name='description', blank=True)),
                ('transpose_method', models.CharField(blank=True, max_length=15, verbose_name='rotate or flip', choices=[(b'FLIP_LEFT_RIGHT', 'Flip left to right'), (b'FLIP_TOP_BOTTOM', 'Flip top to bottom'), (b'ROTATE_90', 'Rotate 90 degrees counter-clockwise'), (b'ROTATE_270', 'Rotate 90 degrees clockwise'), (b'ROTATE_180', 'Rotate 180 degrees')])),
                ('color', models.FloatField(default=1.0, help_text='A factor of 0.0 gives a black and white image, a factor of 1.0 gives the original image.', verbose_name='color')),
                ('brightness', models.FloatField(default=1.0, help_text='A factor of 0.0 gives a black image, a factor of 1.0 gives the original image.', verbose_name='brightness')),
                ('contrast', models.FloatField(default=1.0, help_text='A factor of 0.0 gives a solid grey image, a factor of 1.0 gives the original image.', verbose_name='contrast')),
                ('sharpness', models.FloatField(default=1.0, help_text='A factor of 0.0 gives a blurred image, a factor of 1.0 gives the original image.', verbose_name='sharpness')),
                ('filters', models.CharField(help_text='Chain multiple filters using the following pattern "FILTER_ONE->FILTER_TWO->FILTER_THREE". Image filters will be applied in order. The following filters are available: BLUR, CONTOUR, DETAIL, EDGE_ENHANCE, EDGE_ENHANCE_MORE, EMBOSS, FIND_EDGES, SHARPEN, SMOOTH, SMOOTH_MORE.', max_length=200, verbose_name='filters', blank=True)),
                ('reflection_size', models.FloatField(default=0, help_text='The height of the reflection as a percentage of the orignal image. A factor of 0.0 adds no reflection, a factor of 1.0 adds a reflection equal to the height of the orignal image.', verbose_name='size')),
                ('reflection_strength', models.FloatField(default=0.6, help_text='The initial opacity of the reflection gradient.', verbose_name='strength')),
                ('background_color', models.CharField(default=b'#FFFFFF', help_text='The background color of the reflection gradient. Set this to match the background color of your page.', max_length=7, verbose_name='color')),
            ],
            options={
                'verbose_name': 'photo effect',
                'verbose_name_plural': 'photo effects',
            },
        ),
        migrations.CreateModel(
            name='PhotoSet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('allow_anonymous_view', models.BooleanField(default=True, verbose_name='Public can view')),
                ('allow_user_view', models.BooleanField(default=True, verbose_name='Signed in user can view')),
                ('allow_member_view', models.BooleanField(default=True)),
                ('allow_user_edit', models.BooleanField(default=False, verbose_name='Signed in user can change')),
                ('allow_member_edit', models.BooleanField(default=False)),
                ('create_dt', models.DateTimeField(auto_now_add=True, verbose_name='Created On')),
                ('update_dt', models.DateTimeField(auto_now=True, verbose_name='Last Updated')),
                ('creator_username', models.CharField(max_length=50)),
                ('owner_username', models.CharField(max_length=50)),
                ('status', models.BooleanField(default=True, verbose_name=b'Active')),
                ('status_detail', models.CharField(default=b'active', max_length=50)),
                ('position', models.IntegerField(default=0, null=True, verbose_name='Position', blank=True)),
                ('guid', models.CharField(max_length=40)),
                ('name', models.CharField(max_length=200, verbose_name='name')),
                ('description', models.TextField(verbose_name='description', blank=True)),
                ('publish_type', models.IntegerField(default=2, verbose_name='publish_type', choices=[(1, 'Private'), (2, 'Public')])),
                ('tags', tagging.fields.TagField(help_text='Tags are separated by commas, ex: Tag 1, Tag 2, Tag 3', max_length=255, blank=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True)),
                ('creator', models.ForeignKey(related_name='photos_photoset_creator', on_delete=django.db.models.deletion.SET_NULL, default=None, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('entity', models.ForeignKey(related_name='photos_photoset_entity', on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='entities.Entity', null=True)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='user_groups.Group', null=True)),
                ('owner', models.ForeignKey(related_name='photos_photoset_owner', on_delete=django.db.models.deletion.SET_NULL, default=None, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'Photo Album',
                'verbose_name_plural': 'Photo Album',
                'permissions': (('view_photoset', 'Can view photoset'),),
            },
        ),
        migrations.CreateModel(
            name='PhotoSize',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Photo size name should contain only letters, numbers and underscores. Examples: "thumbnail", "display", "small", "main_page_widget".', unique=True, max_length=20, verbose_name='name')),
                ('width', models.PositiveIntegerField(default=0, help_text='If width is set to "0" the image will be scaled to the supplied height.', verbose_name='width')),
                ('height', models.PositiveIntegerField(default=0, help_text='If height is set to "0" the image will be scaled to the supplied width', verbose_name='height')),
                ('quality', models.PositiveIntegerField(default=70, help_text='JPEG image quality.', verbose_name='quality', choices=[(30, 'Very Low'), (40, 'Low'), (50, 'Medium-Low'), (60, 'Medium'), (70, 'Medium-High'), (80, 'High'), (90, 'Very High')])),
                ('upscale', models.BooleanField(default=False, help_text='If selected the image will be scaled up if necessary to fit the supplied dimensions. Cropped sizes will be upscaled regardless of this setting.', verbose_name='upscale images?')),
                ('crop', models.BooleanField(default=False, help_text='If selected the image will be scaled and cropped to fit the supplied dimensions.', verbose_name='crop to fit?')),
                ('pre_cache', models.BooleanField(default=False, help_text='If selected this photo size will be pre-cached as photos are added.', verbose_name='pre-cache?')),
                ('increment_count', models.BooleanField(default=False, help_text='If selected the image\'s "view_count" will be incremented when this photo size is displayed.', verbose_name='increment view count?')),
                ('effect', models.ForeignKey(related_name='photo_sizes', verbose_name='photo effect', blank=True, to='photos.PhotoEffect', null=True)),
            ],
            options={
                'ordering': ['width', 'height'],
                'verbose_name': 'photo size',
                'verbose_name_plural': 'photo sizes',
            },
        ),
        migrations.CreateModel(
            name='Pool',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('created_at', models.DateTimeField(default=datetime.datetime.now, verbose_name='created_at')),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('photo', models.ForeignKey(to='photos.Image')),
            ],
            options={
                'verbose_name': 'pool',
                'verbose_name_plural': 'pools',
                'permissions': (('view_photopool', 'Can view photopool'),),
            },
        ),
        migrations.CreateModel(
            name='Watermark',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=30, verbose_name='name')),
                ('description', models.TextField(verbose_name='description', blank=True)),
                ('image', models.ImageField(upload_to=b'/media//watermarks', verbose_name='image')),
                ('style', models.CharField(default=b'scale', max_length=5, verbose_name='style', choices=[(b'tile', 'Tile'), (b'scale', 'Scale')])),
                ('opacity', models.FloatField(default=1, help_text='The opacity of the overlay.', verbose_name='opacity')),
            ],
            options={
                'verbose_name': 'watermark',
                'verbose_name_plural': 'watermarks',
            },
        ),
        migrations.AddField(
            model_name='photosize',
            name='watermark',
            field=models.ForeignKey(related_name='photo_sizes', verbose_name='watermark image', blank=True, to='photos.Watermark', null=True),
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
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='user_groups.Group', null=True),
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
