# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.core.management import call_command


def update_stats(apps, schema_editor):
    DashboardStatType = apps.get_model("dashboard", "DashboardStatType")
    if not DashboardStatType.objects.filter(name="events_upcoming").exists():
        call_command('update_dashboard_stats')


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(update_stats),
    ]
