# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."
        # Note: Don't use "from appname.models import ModelName".
        # Use orm.ModelName to refer to models in this application,
        # and orm['appname.ModelName'] for models in other applications.
        orm.DashboardStatType.objects.exclude(displayed=True).update(displayed=False)

    def backwards(self, orm):
        "Write your backwards methods here."
        pass

    models = {
        u'dashboard.dashboardstat': {
            'Meta': {'ordering': "('-create_dt',)", 'object_name': 'DashboardStat'},
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dashboard.DashboardStatType']"}),
            'value': ('django.db.models.fields.TextField', [], {})
        },
        u'dashboard.dashboardstattype': {
            'Meta': {'ordering': "('position',)", 'object_name': 'DashboardStatType'},
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'displayed': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'position': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['dashboard']
    symmetrical = True
