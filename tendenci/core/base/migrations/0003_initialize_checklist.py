# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        from django.core.management import call_command
        call_command("loaddata", "completionchecklist.json")


    def backwards(self, orm):
        pass


    models = {
        'base.checklistitem': {
            'Meta': {'ordering': "('position',)", 'object_name': 'ChecklistItem'},
            'done': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'position': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        },
        'base.updatetracker': {
            'Meta': {'object_name': 'UpdateTracker'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_updating': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['base']
    symmetrical = True
