# -*- coding: utf-8 -*-
from django.db import migrations

def add_parent_entity_to_existing_apps(apps, schema_editor):
    CorpMembershipApp = apps.get_model('corporate_memberships', 'CorpMembershipApp')
    CorpMembershipAppField = apps.get_model('corporate_memberships', 'CorpMembershipAppField')
    corp_apps = CorpMembershipApp.objects.all()
    for corp_app in corp_apps:
        if not CorpMembershipAppField.objects.filter(corp_app=corp_app, field_name='parent_entity').exists():
            app_field = CorpMembershipAppField(
                         corp_app=corp_app,
                         label="Parent Entity",
                         field_name='parent_entity',
                         display=False,)
            app_field.save()

class Migration(migrations.Migration):

    dependencies = [
        ('corporate_memberships', '0010_auto_20171201_1721'),
    ]

    operations = [
        migrations.RunPython(add_parent_entity_to_existing_apps),
    ]
