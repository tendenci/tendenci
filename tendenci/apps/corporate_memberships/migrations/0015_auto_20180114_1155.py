# -*- coding: utf-8 -*-
from django.db import migrations

def add_reps_groups(apps, schema_editor):
    from tendenci.apps.corporate_memberships.models import CorpMembershipApp, CorpMembershipRep
#     CorpMembershipApp = apps.get_model('corporate_memberships', 'CorpMembershipApp')
#     CorpMembershipRep = apps.get_model('corporate_memberships', 'CorpMembershipRep')
    current_app = CorpMembershipApp.objects.current_app()
    if current_app:
        if not current_app.dues_reps_group or not current_app.member_reps_group:
            current_app.save()
        # add dues reps to the dues_reps_group and member reps to member_reps_group
        for rep in CorpMembershipRep.objects.filter():
            rep.sync_reps_groups()


class Migration(migrations.Migration):

    dependencies = [
        ('corporate_memberships', '0014_auto_20180114_1144'),
    ]

    operations = [
        migrations.RunPython(add_reps_groups),
    ]
