# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'PluginApp.is_enabled'
        db.alter_column(u'pluginmanager_pluginapp', 'is_enabled', self.gf('django.db.models.fields.NullBooleanField')(null=True))

    def backwards(self, orm):

        # Changing field 'PluginApp.is_enabled'
        db.alter_column(u'pluginmanager_pluginapp', 'is_enabled', self.gf('django.db.models.fields.BooleanField')())

    models = {
        u'pluginmanager.pluginapp': {
            'Meta': {'object_name': 'PluginApp'},
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_enabled': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'package': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['pluginmanager']