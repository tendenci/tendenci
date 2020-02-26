# -*- coding: utf-8 -*-


from django.db import migrations


def event_group_to_groups(apps, schema_editor):
    """
        Migrate event.group foreignkey relationship to the
        many-to-many relationship in event.groups
    """
    Event = apps.get_model('events', 'Event')

    for event in Event.objects.all():
        if event.group:
            event.groups.add(event.group)


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0004_auto_20160603_1347'),
    ]

    operations = [
        migrations.RunPython(event_group_to_groups),
    ]
