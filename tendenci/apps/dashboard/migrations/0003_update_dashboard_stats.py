# -*- coding: utf-8 -*-
import subprocess
from south.v2 import DataMigration

class Migration(DataMigration):

    depends_on = (
        ('events', '0009_auto__add_field_event_priority__add_field_event_display_event_registra'),
        ('pages', '0001_initial'),
        ('event_logs', '0001_initial'),
        ('forms', '0001_initial'),
        ('corporate_memberships', '0006_auto__add_field_corpmembershipimport_bind_members'),
        ('memberships', '0012_auto__add_membershipdemographic'),
    )

    def forwards(self, orm):
        # skip if this command already run
        if not orm.DashboardStatType.objects.filter(name="events_upcoming").exists():
            # run it in the background because this command is time-consuming
            subprocess.Popen(["python", "manage.py",
                              "update_dashboard_stats"])

    def backwards(self, orm):
        pass

    models = {
        'dashboard.dashboardstat': {
            'Meta': {'ordering': "('-create_dt',)", 'object_name': 'DashboardStat'},
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dashboard.DashboardStatType']"}),
            'value': ('django.db.models.fields.TextField', [], {})
        },
        'dashboard.dashboardstattype': {
            'Meta': {'ordering': "('position',)", 'object_name': 'DashboardStatType'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'displayed': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'position': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['dashboard']
    symmetrical = True
