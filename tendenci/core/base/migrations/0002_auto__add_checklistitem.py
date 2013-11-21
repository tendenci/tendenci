# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ChecklistItem'
        db.create_table('base_checklistitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('position', self.gf('django.db.models.fields.IntegerField')(default=0, null=True, blank=True)),
            ('key', self.gf('django.db.models.fields.CharField')(unique=True, max_length=20)),
            ('label', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('done', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('base', ['ChecklistItem'])


    def backwards(self, orm):
        # Deleting model 'ChecklistItem'
        db.delete_table('base_checklistitem')


    models = {
        'base.checklistitem': {
            'Meta': {'ordering': "('position',)", 'object_name': 'ChecklistItem'},
            'done': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'position': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        },
        'base.updatetracker': {
            'Meta': {'object_name': 'UpdateTracker'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_updating': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['base']
