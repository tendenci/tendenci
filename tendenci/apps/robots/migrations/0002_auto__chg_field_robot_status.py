# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Robot.status'
        db.alter_column(u'robots_robot', 'status', self.gf('django.db.models.fields.NullBooleanField')(null=True))

    def backwards(self, orm):

        # Changing field 'Robot.status'
        db.alter_column(u'robots_robot', 'status', self.gf('django.db.models.fields.BooleanField')())

    models = {
        u'robots.robot': {
            'Meta': {'object_name': 'Robot'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'status': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['robots']