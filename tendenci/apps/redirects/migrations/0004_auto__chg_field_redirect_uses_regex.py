# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Redirect.uses_regex'
        db.alter_column(u'redirects_redirect', 'uses_regex', self.gf('django.db.models.fields.NullBooleanField')(null=True))

    def backwards(self, orm):

        # Changing field 'Redirect.uses_regex'
        db.alter_column(u'redirects_redirect', 'uses_regex', self.gf('django.db.models.fields.BooleanField')())

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