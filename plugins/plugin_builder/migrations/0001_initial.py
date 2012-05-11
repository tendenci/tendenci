# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Plugin'
        db.create_table('plugin_builder_plugin', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('single_caps', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('single_lower', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('plural_caps', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('plural_lower', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('plugin_builder', ['Plugin'])

        # Adding model 'PluginField'
        db.create_table('plugin_builder_pluginfield', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('default', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('blank', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('help_text', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('plugin_builder', ['PluginField'])


    def backwards(self, orm):
        
        # Deleting model 'Plugin'
        db.delete_table('plugin_builder_plugin')

        # Deleting model 'PluginField'
        db.delete_table('plugin_builder_pluginfield')


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
            'help_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['plugin_builder']
