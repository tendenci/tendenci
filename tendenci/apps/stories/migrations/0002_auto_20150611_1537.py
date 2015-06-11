# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tendenci.apps.user_groups.utils
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('stories', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('user_groups', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='story',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, default=tendenci.apps.user_groups.utils.get_default_group, to='user_groups.Group', null=True),
        ),
        migrations.AddField(
            model_name='story',
            name='image',
            field=models.ForeignKey(default=None, to='stories.StoryPhoto', help_text='Photo that represents this story.', null=True),
        ),
        migrations.AddField(
            model_name='story',
            name='owner',
            field=models.ForeignKey(related_name='stories_story_owner', on_delete=django.db.models.deletion.SET_NULL, default=None, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='story',
            name='rotator',
            field=models.ForeignKey(default=None, blank=True, to='stories.Rotator', help_text='The rotator where this story belongs.', null=True),
        ),
    ]
