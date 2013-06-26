# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'DashboardStatType'
        db.create_table('dashboard_dashboardstattype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('position', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('displayed', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('dashboard', ['DashboardStatType'])

        # Deleting column 'DashboardStat.key'.
        db.delete_column('dashboard_dashboardstat', 'key')

        # Adding field 'DashboardStat.key'.
        db.add_column('dashboard_dashboardstat', 'key', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dashboard.DashboardStatType']))


    def backwards(self, orm):
        
        # Deleting model 'DashboardStatType'
        db.delete_table('dashboard_dashboardstattype')

        # Deleting column 'DashboardStat.key'.
        db.delete_column('dashboard_dashboardstat', 'key_id')

        # Adding field 'DashboardStat.key'.
        db.add_column('dashboard_dashboardstat', 'key', self.gf('django.db.models.fields.CharField')(max_length=255))


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
            'description': ('django.db.models.fields.TextField', [], {}),
            'displayed': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'position': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['dashboard']
