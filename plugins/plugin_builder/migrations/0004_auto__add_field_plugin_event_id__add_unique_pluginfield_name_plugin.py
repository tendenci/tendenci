# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Plugin.event_id'
        db.add_column('plugin_builder_plugin', 'event_id', self.gf('django.db.models.fields.IntegerField')(default=0), keep_default=False)

        # Adding unique constraint on 'PluginField', fields ['name', 'plugin']
        db.create_unique('plugin_builder_pluginfield', ['name', 'plugin_id'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'PluginField', fields ['name', 'plugin']
        db.delete_unique('plugin_builder_pluginfield', ['name', 'plugin_id'])

        # Deleting field 'Plugin.event_id'
        db.delete_column('plugin_builder_plugin', 'event_id')


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
            'blank': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'default': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'help_text': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'plugin': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fields'", 'to': "orm['plugin_builder.Plugin']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['plugin_builder']
