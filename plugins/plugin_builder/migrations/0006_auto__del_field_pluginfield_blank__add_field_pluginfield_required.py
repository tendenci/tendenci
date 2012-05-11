# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'PluginField.blank'
        db.delete_column('plugin_builder_pluginfield', 'blank')

        # Adding field 'PluginField.required'
        db.add_column('plugin_builder_pluginfield', 'required', self.gf('django.db.models.fields.BooleanField')(default=True), keep_default=False)


    def backwards(self, orm):
        
        # Adding field 'PluginField.blank'
        db.add_column('plugin_builder_pluginfield', 'blank', self.gf('django.db.models.fields.BooleanField')(default=False), keep_default=False)

        # Deleting field 'PluginField.required'
        db.delete_column('plugin_builder_pluginfield', 'required')


    models = {
        'plugin_builder.plugin': {
            'Meta': {'object_name': 'Plugin'},
            'event_id': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'plural_caps': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'plural_lower': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'single_caps': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'single_lower': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'plugin_builder.pluginfield': {
            'Meta': {'unique_together': "(('plugin', 'name'),)", 'object_name': 'PluginField'},
            'default': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'help_text': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'kwargs': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'plugin': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fields'", 'to': "orm['plugin_builder.Plugin']"}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['plugin_builder']
