# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Redirect'
        db.create_table('redirects_redirect', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('from_url', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255, db_index=True)),
            ('to_url', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('http_status', self.gf('django.db.models.fields.SmallIntegerField')(default=301)),
            ('status', self.gf('django.db.models.fields.SmallIntegerField')(default=1)),
            ('uses_regex', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('create_dt', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('update_dt', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('redirects', ['Redirect'])


    def backwards(self, orm):
        
        # Deleting model 'Redirect'
        db.delete_table('redirects_redirect')


    models = {
        'redirects.redirect': {
            'Meta': {'object_name': 'Redirect'},
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'from_url': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'http_status': ('django.db.models.fields.SmallIntegerField', [], {'default': '301'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'}),
            'to_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'uses_regex': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['redirects']
