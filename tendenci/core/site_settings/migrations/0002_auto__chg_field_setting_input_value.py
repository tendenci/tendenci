# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'Setting.input_value'
        db.alter_column('site_settings_setting', 'input_value', self.gf('django.db.models.fields.CharField')(max_length=1000))


    def backwards(self, orm):
        
        # Changing field 'Setting.input_value'
        db.alter_column('site_settings_setting', 'input_value', self.gf('django.db.models.fields.CharField')(max_length=255))


    models = {
        'site_settings.setting': {
            'Meta': {'object_name': 'Setting'},
            'client_editable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'data_type': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'default_value': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'input_type': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'input_value': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'blank': 'True'}),
            'is_secure': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'parent_id': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'scope': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'scope_category': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'store': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'updated_by': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'value': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        }
    }

    complete_apps = ['site_settings']
