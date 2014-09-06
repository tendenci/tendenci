# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Deleting field 'Guide.ordering'
        db.delete_column('tendenci_guide_guide', 'ordering')


    def backwards(self, orm):
        
        # Adding field 'Guide.ordering'
        db.add_column('tendenci_guide_guide', 'ordering', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True), keep_default=False)


    models = {
        'tendenci_guide.guide': {
            'Meta': {'object_name': 'Guide'},
            'content': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'section': ('django.db.models.fields.CharField', [], {'default': "'misc'", 'max_length': '50'}),
            'slug': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['tendenci_guide']
