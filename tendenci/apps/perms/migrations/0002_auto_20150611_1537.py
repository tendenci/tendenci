# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('user_groups', '0001_initial'),
        ('perms', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='objectpermission',
            name='group',
            field=models.ForeignKey(to='user_groups.Group', null=True),
        ),
        migrations.AddField(
            model_name='objectpermission',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
