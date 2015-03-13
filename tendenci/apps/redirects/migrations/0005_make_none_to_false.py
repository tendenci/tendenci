# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."
        # Note: Don't use "from appname.models import ModelName".
        # Use orm.ModelName to refer to models in this application,
        # and orm['appname.ModelName'] for models in other applications.
        orm.Redirect.objects.exclude(uses_regex=True).update(uses_regex=False)


    def backwards(self, orm):
        "Write your backwards methods here."

    models = {
        u'redirects.redirect': {
            'Meta': {'object_name': 'Redirect'},
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'from_app': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '100', 'blank': 'True'}),
            'from_url': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'blank': 'True'}),
            'http_status': ('django.db.models.fields.SmallIntegerField', [], {'default': '301'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.SmallIntegerField', [], {'default': '1'}),
            'to_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'uses_regex': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['redirects']
    symmetrical = True
