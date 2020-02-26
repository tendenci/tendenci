# -*- coding: utf-8 -*-
from django.db import migrations
from django.core.management import call_command


def update_stats(apps, schema_editor):
    DashboardStatType = apps.get_model("dashboard", "DashboardStatType")
    if not DashboardStatType.objects.filter(name="events_upcoming").exists():
        # Trap errors here. When run with the initial migrations,
        # it could fail if other tables or columns referenced haven't
        # been created yet.
        # In that case, it's okay because this command will run with
        # the scheduled task "run_nightly_commands".
        try:
            call_command('update_dashboard_stats')
        except:
            pass


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        #migrations.RunPython(update_stats),
    ]
