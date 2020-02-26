# -*- coding: utf-8 -*-
from django.db import migrations


def parent_entity_assign_default(apps, schema_editor):
    """
    Assign the default entity to the parent_entity field for existing corp profiles.
    """
    CorpProfile = apps.get_model('corporate_memberships', 'CorpProfile')
    Entity = apps.get_model('entities', 'Entity')
    corp_profiles = CorpProfile.objects.all()
    default_entity = Entity.objects.first()
    for corp_profile in corp_profiles:
        if not corp_profile.parent_entity:
            corp_profile.parent_entity = default_entity
            corp_profile.save()

class Migration(migrations.Migration):

    dependencies = [
        ('corporate_memberships', '0012_corpmembershipapp_parent_entities'),
    ]

    operations = [
        migrations.RunPython(parent_entity_assign_default),
    ]
