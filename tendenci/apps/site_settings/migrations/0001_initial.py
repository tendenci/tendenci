# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Setting'
        db.create_table('site_settings_setting', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('data_type', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('value', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('default_value', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('input_type', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('input_value', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('client_editable', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('store', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('update_dt', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('updated_by', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('scope', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('scope_category', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('parent_id', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
            ('is_secure', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('site_settings', ['Setting'])


    def backwards(self, orm):
        
        # Deleting model 'Setting'
        db.delete_table('site_settings_setting')


    models = {
        'site_settings.setting': {
            'Meta': {'object_name': 'Setting'},
            'client_editable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'data_type': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'default_value': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'input_type': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'input_value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
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
