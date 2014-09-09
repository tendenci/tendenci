# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Setting.client_editable'
        db.alter_column(u'site_settings_setting', 'client_editable', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Setting.is_secure'
        db.alter_column(u'site_settings_setting', 'is_secure', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Setting.store'
        db.alter_column(u'site_settings_setting', 'store', self.gf('django.db.models.fields.NullBooleanField')(null=True))

    def backwards(self, orm):

        # Changing field 'Setting.client_editable'
        db.alter_column(u'site_settings_setting', 'client_editable', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Setting.is_secure'
        db.alter_column(u'site_settings_setting', 'is_secure', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Setting.store'
        db.alter_column(u'site_settings_setting', 'store', self.gf('django.db.models.fields.BooleanField')())

    models = {
        u'site_settings.setting': {
            'Meta': {'object_name': 'Setting'},
            'client_editable': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'data_type': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'default_value': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'input_type': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'input_value': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'blank': 'True'}),
            'is_secure': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'parent_id': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'scope': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'scope_category': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'store': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'}),
            'updated_by': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'value': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        }
    }

    complete_apps = ['site_settings']