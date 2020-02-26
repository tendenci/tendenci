# -*- coding: utf-8 -*-


from django.db import models, migrations
import tendenci.apps.user_groups.utils
import django.db.models.deletion
from django.conf import settings
import tagging.fields


class Migration(migrations.Migration):

    dependencies = [
        ('user_groups', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('entities', '0001_initial'),
        ('files', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Rotator',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Story',
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
                ('position', models.IntegerField(default=0, null=True, verbose_name='Position', blank=True)),
                ('guid', models.CharField(max_length=40)),
                ('title', models.CharField(max_length=200, blank=True)),
                ('content', models.TextField(blank=True)),
                ('syndicate', models.BooleanField(default=False, verbose_name='Include in RSS feed')),
                ('full_story_link', models.CharField(max_length=300, verbose_name='Full Story Link', blank=True)),
                ('link_title', models.CharField(max_length=200, verbose_name='Link Title', blank=True)),
                ('start_dt', models.DateTimeField(null=True, verbose_name='Start Date/Time', blank=True)),
                ('end_dt', models.DateTimeField(null=True, verbose_name='End Date/Time', blank=True)),
                ('expires', models.BooleanField(default=True, verbose_name='Expires')),
                ('tags', tagging.fields.TagField(default='', max_length=255, blank=True)),
                ('rotator_position', models.IntegerField(default=0, verbose_name='Rotator Position', blank=True)),
                ('creator', models.ForeignKey(related_name='stories_story_creator', on_delete=django.db.models.deletion.SET_NULL, default=None, editable=False, to=settings.AUTH_USER_MODEL, null=True)),
                ('entity', models.ForeignKey(related_name='stories_story_entity', on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='entities.Entity', null=True)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, default=tendenci.apps.user_groups.utils.get_default_group, to='user_groups.Group', null=True)),
            ],
            options={
                'ordering': ['position'],
                'verbose_name_plural': 'stories',
            },
        ),
        migrations.CreateModel(
            name='StoryPhoto',
            fields=[
                ('file_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, on_delete=django.db.models.deletion.CASCADE, to='files.File')),
            ],
            bases=('files.file',),
        ),
        migrations.AddField(
            model_name='story',
            name='image',
            field=models.ForeignKey(default=None, to='stories.StoryPhoto', help_text='Photo that represents this story.', null=True, on_delete=django.db.models.deletion.CASCADE),
        ),
        migrations.AddField(
            model_name='story',
            name='owner',
            field=models.ForeignKey(related_name='stories_story_owner', on_delete=django.db.models.deletion.SET_NULL, default=None, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='story',
            name='rotator',
            field=models.ForeignKey(default=None, blank=True, to='stories.Rotator', help_text='The rotator where this story belongs.', null=True, on_delete=django.db.models.deletion.CASCADE),
        ),
    ]
