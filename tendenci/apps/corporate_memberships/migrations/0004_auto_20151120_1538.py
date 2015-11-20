# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

def threshold_copyto_cap(apps, schema_editor):
    # copy the value of individual_threshold to membership_cap
    CorporateMembershipType = apps.get_model('corporate_memberships', 'CorporateMembershipType')
    for corp_type in CorporateMembershipType.objects.all():
        if corp_type.apply_threshold:
            corp_type.apply_cap = True
            corp_type.membership_cap = corp_type.individual_threshold
            corp_type.save()

class Migration(migrations.Migration):
    dependencies = [
        ('corporate_memberships', '0003_auto_20151120_1531'),
    ]

    operations = [
        migrations.RunPython(threshold_copyto_cap),
    ]
