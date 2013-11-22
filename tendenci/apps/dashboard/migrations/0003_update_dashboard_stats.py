# -*- coding: utf-8 -*-
import subprocess
from south.v2 import DataMigration

class Migration(DataMigration):

    depends_on = (
        ('events', '0021_auto__add_recurringevent__add_field_event_is_recurring_event__add_fiel'),
        ('pages', '0001_initial'),
        ('event_logs', '0001_initial'),
        ('forms', '0010_convert_email_fields'),
        ('corporate_memberships', '0023_setup_corp_reps_group'),
        ('memberships', '0029_auto__add_field_membershipdefault_referer_url'),
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
