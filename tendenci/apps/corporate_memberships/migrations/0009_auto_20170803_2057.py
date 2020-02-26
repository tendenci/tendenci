# -*- coding: utf-8 -*-
from django.db import migrations


def add_logo_to_existing_apps(apps, schema_editor):
    CorpMembershipApp = apps.get_model('corporate_memberships', 'CorpMembershipApp')
    CorpMembershipAppField = apps.get_model('corporate_memberships', 'CorpMembershipAppField')
    corp_apps = CorpMembershipApp.objects.all()
    for corp_app in corp_apps:
        if not CorpMembershipAppField.objects.filter(corp_app=corp_app, field_name='logo').exists():
            app_field = CorpMembershipAppField(
                         corp_app=corp_app,
                         label="Logo",
                         field_name='logo_file',
                         field_type='FileField',
                         display=False,)
            app_field.save()


class Migration(migrations.Migration):

    dependencies = [
        ('corporate_memberships', '0008_auto_20170803_2038'),
    ]

    operations = [
            migrations.RunPython(add_logo_to_existing_apps),
    ]
