# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Import'
        db.create_table('imports_import', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('app_label', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('model_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('status', self.gf('django.db.models.fields.CharField')(default='pending', max_length=50)),
            ('file', self.gf('django.db.models.fields.files.FileField')(max_length=260)),
            ('total_created', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('total_updated', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('total_invalid', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_done', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('imports', ['Import'])


    def backwards(self, orm):
        
        # Deleting model 'Import'
        db.delete_table('imports_import')


    models = {
        'imports.import': {
            'Meta': {'object_name': 'Import'},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_done': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '260'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'pending'", 'max_length': '50'}),
            'total_created': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'total_invalid': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'total_updated': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['imports']
