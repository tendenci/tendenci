# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Export'
        db.create_table('exports_export', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('app_label', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('model_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('status', self.gf('django.db.models.fields.CharField')(default='pending', max_length=50)),
            ('result', self.gf('picklefield.fields.PickledObjectField')(default=None, null=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_done', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('exports', ['Export'])


    def backwards(self, orm):
        
        # Deleting model 'Export'
        db.delete_table('exports_export')


    models = {
        'exports.export': {
            'Meta': {'object_name': 'Export'},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_done': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'result': ('picklefield.fields.PickledObjectField', [], {'default': 'None', 'null': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'pending'", 'max_length': '50'})
        }
    }

    complete_apps = ['exports']
