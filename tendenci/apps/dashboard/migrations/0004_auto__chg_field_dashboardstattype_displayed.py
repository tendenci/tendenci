# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'DashboardStatType.displayed'
        db.alter_column(u'dashboard_dashboardstattype', 'displayed', self.gf('django.db.models.fields.NullBooleanField')(null=True))

    def backwards(self, orm):

        # Changing field 'DashboardStatType.displayed'
        db.alter_column(u'dashboard_dashboardstattype', 'displayed', self.gf('django.db.models.fields.BooleanField')())

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