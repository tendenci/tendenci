# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Report404'
        db.create_table('handler404_report404', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('count', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('handler404', ['Report404'])


    def backwards(self, orm):
        
        # Deleting model 'Report404'
        db.delete_table('handler404_report404')


    models = {
        'handler404.report404': {
            'Meta': {'object_name': 'Report404'},
            'count': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['handler404']
