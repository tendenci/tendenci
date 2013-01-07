# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Import.failure_reason'
        db.add_column('imports_import', 'failure_reason', self.gf('django.db.models.fields.CharField')(default='', max_length=250, blank=True), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Import.failure_reason'
        db.delete_column('imports_import', 'failure_reason')


    models = {
        'imports.import': {
            'Meta': {'object_name': 'Import'},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_done': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'failure_reason': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250', 'blank': 'True'}),
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
