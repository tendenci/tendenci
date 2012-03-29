# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Metric'
        db.create_table('metrics_metric', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('users', self.gf('django.db.models.fields.IntegerField')()),
            ('members', self.gf('django.db.models.fields.IntegerField')()),
            ('visits', self.gf('django.db.models.fields.IntegerField')()),
            ('disk_usage', self.gf('django.db.models.fields.BigIntegerField')()),
            ('create_dt', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('metrics', ['Metric'])


    def backwards(self, orm):
        
        # Deleting model 'Metric'
        db.delete_table('metrics_metric')


    models = {
        'metrics.metric': {
            'Meta': {'object_name': 'Metric'},
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'disk_usage': ('django.db.models.fields.BigIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'members': ('django.db.models.fields.IntegerField', [], {}),
            'users': ('django.db.models.fields.IntegerField', [], {}),
            'visits': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['metrics']
