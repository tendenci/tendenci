# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

def news_group_to_groups(apps, schema_editor):
    """
        Migrate event.group foreignkey relationship to the
        many-to-many relationship in event.groups
    """
    News = apps.get_model('news', 'News')

    for my_news in News.objects.all():
        if my_news.group:
            my_news.groups.add(my_news.group)


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0003_auto_20160701_1246'),
    ]

    operations = [
        migrations.RunPython(news_group_to_groups),
    ]
