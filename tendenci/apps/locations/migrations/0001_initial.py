# -*- coding: utf-8 -*-


from django.db import models, migrations
import tendenci.apps.base.fields
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('entities', '0001_initial'),
        ('files', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Distance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('zip_code', models.CharField(max_length=7)),
                ('distance', models.PositiveSmallIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Location',
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
                ('status', models.BooleanField(default=True, verbose_name='Active')),
                ('status_detail', models.CharField(default='active', max_length=50)),
                ('guid', models.CharField(max_length=40)),
                ('location_name', models.CharField(max_length=200, verbose_name='Name', blank=True)),
                ('slug', tendenci.apps.base.fields.SlugField(unique=True, max_length=100, verbose_name='URL Path', db_index=True)),
                ('description', models.TextField(blank=True)),
                ('contact', models.CharField(max_length=100, blank=True)),
                ('address', models.CharField(max_length=100, blank=True)),
                ('address2', models.CharField(max_length=100, blank=True)),
                ('city', models.CharField(max_length=100, blank=True)),
                ('state', models.CharField(max_length=50, blank=True)),
                ('zipcode', models.CharField(max_length=50, verbose_name='Zip Code', blank=True)),
                ('country', models.CharField(max_length=100, blank=True)),
                ('phone', models.CharField(max_length=50, blank=True)),
                ('fax', models.CharField(max_length=50, blank=True)),
                ('email', models.CharField(max_length=120, blank=True)),
                ('website', models.CharField(max_length=300, blank=True)),
                ('latitude', models.FloatField(null=True, blank=True)),
                ('longitude', models.FloatField(null=True, blank=True)),
                ('hq', models.BooleanField(default=False, verbose_name='Headquarters')),
                ('creator', models.ForeignKey(related_name='locations_location_creator', on_delete=django.db.models.deletion.SET_NULL, default=None, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('entity', models.ForeignKey(related_name='locations_location_entity', on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='entities.Entity', null=True)),
                ('logo', models.ForeignKey(default=None, to='files.File', help_text='Only jpg, gif, or png images.', null=True, on_delete=django.db.models.deletion.CASCADE)),
                ('owner', models.ForeignKey(related_name='locations_location_owner', on_delete=django.db.models.deletion.SET_NULL, default=None, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
            },
        ),
        migrations.CreateModel(
            name='LocationImport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_dt', models.DateTimeField(auto_now_add=True)),
                ('creator', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.CASCADE)),
            ],
        ),
        migrations.AddField(
            model_name='distance',
            name='location',
            field=models.ForeignKey(to='locations.Location', on_delete=django.db.models.deletion.CASCADE),
        ),
    ]
