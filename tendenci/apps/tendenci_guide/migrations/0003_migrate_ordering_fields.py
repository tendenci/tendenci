# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        # Migrate data from previous ordering field
        for guide in orm.Guide.objects.all():
            guide.position = guide.ordering
            guide.save()


    def backwards(self, orm):
        # Migrate data from previous ordering field
        for guide in orm.Guide.objects.all():
            guide.ordering = guide.position
            guide.save()


    models = {
        'tendenci_guide.guide': {
            'Meta': {'object_name': 'Guide'},
            'content': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ordering': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'section': ('django.db.models.fields.CharField', [], {'default': "'misc'", 'max_length': '50'}),
            'slug': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['tendenci_guide']
