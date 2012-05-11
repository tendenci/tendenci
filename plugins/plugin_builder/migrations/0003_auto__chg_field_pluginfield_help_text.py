# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'PluginField.help_text'
        db.alter_column('plugin_builder_pluginfield', 'help_text', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))


    def backwards(self, orm):
        
        # Changing field 'PluginField.help_text'
        db.alter_column('plugin_builder_pluginfield', 'help_text', self.gf('django.db.models.fields.TextField')(null=True))


    models = {
        'plugin_builder.plugin': {
            'Meta': {'object_name': 'Plugin'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'plural_caps': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'plural_lower': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'single_caps': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'single_lower': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'plugin_builder.pluginfield': {
            'Meta': {'object_name': 'PluginField'},
            'blank': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'default': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'help_text': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'plugin': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['plugin_builder.Plugin']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['plugin_builder']
