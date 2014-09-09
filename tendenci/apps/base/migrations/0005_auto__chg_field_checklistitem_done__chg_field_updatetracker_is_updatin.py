# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'ChecklistItem.done'
        db.alter_column(u'base_checklistitem', 'done', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'UpdateTracker.is_updating'
        db.alter_column(u'base_updatetracker', 'is_updating', self.gf('django.db.models.fields.NullBooleanField')(null=True))

    def backwards(self, orm):

        # Changing field 'ChecklistItem.done'
        db.alter_column(u'base_checklistitem', 'done', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'UpdateTracker.is_updating'
        db.alter_column(u'base_updatetracker', 'is_updating', self.gf('django.db.models.fields.BooleanField')())

    models = {
        u'base.checklistitem': {
            'Meta': {'ordering': "('position',)", 'object_name': 'ChecklistItem'},
            'done': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'position': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'})
        },
        u'base.updatetracker': {
            'Meta': {'object_name': 'UpdateTracker'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_updating': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['base']