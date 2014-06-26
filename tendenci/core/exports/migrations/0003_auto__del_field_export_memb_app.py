# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Export.memb_app'
        db.delete_column('exports_export', 'memb_app_id')


    def backwards(self, orm):
        # Adding field 'Export.memb_app'
        db.add_column('exports_export', 'memb_app',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['memberships.App'], null=True, blank=True),
                      keep_default=False)


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