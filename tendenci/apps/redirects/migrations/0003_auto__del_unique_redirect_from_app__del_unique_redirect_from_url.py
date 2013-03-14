# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):

        # Removing unique constraint on 'Redirect', fields ['from_url']
        try:
            db.delete_unique('redirects_redirect', ['from_url'])
        except ValueError, e:
            pass

    def backwards(self, orm):

        # Adding unique constraint on 'Redirect', fields ['from_url']
        db.create_unique('redirects_redirect', ['from_url'])


    models = {
        'redirects.redirect': {
            'Meta': {'object_name': 'Redirect'},
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'from_app': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'blank': 'True'}),
            'from_url': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'blank': 'True'}),
            'http_status': ('django.db.models.fields.SmallIntegerField', [], {'default': '301'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'}),
            'to_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'uses_regex': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['redirects']
