# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models
from django.db.utils import DatabaseError


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'UpdateTracker'
        try:
            db.create_table('base_updatetracker', (
                ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
                ('is_updating', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ))
            db.send_create_signal('base', ['UpdateTracker'])
        except DatabaseError:
            print "Database table already exists. Marking migration as complete."


    def backwards(self, orm):
        # Deleting model 'UpdateTracker'
        db.delete_table('base_updatetracker')


    models = {
        'base.updatetracker': {
            'Meta': {'object_name': 'UpdateTracker'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_updating': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['base']