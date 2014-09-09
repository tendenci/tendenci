# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'AcctTran.status'
        db.alter_column(u'accountings_accttran', 'status', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'AcctTran.creator'
        db.alter_column(u'accountings_accttran', 'creator_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.SET_NULL, to=orm['auth.User']))

        # Changing field 'AcctTran.owner'
        db.alter_column(u'accountings_accttran', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.SET_NULL, to=orm['auth.User']))

        # Changing field 'AcctTran.cleared'
        db.alter_column(u'accountings_accttran', 'cleared', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'AcctEntry.status'
        db.alter_column(u'accountings_acctentry', 'status', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'AcctEntry.creator'
        db.alter_column(u'accountings_acctentry', 'creator_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.SET_NULL, to=orm['auth.User']))

        # Changing field 'AcctEntry.exported'
        db.alter_column(u'accountings_acctentry', 'exported', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'AcctEntry.owner'
        db.alter_column(u'accountings_acctentry', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.SET_NULL, to=orm['auth.User']))

    def backwards(self, orm):

        # Changing field 'AcctTran.status'
        db.alter_column(u'accountings_accttran', 'status', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'AcctTran.creator'
        db.alter_column(u'accountings_accttran', 'creator_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['auth.User']))

        # Changing field 'AcctTran.owner'
        db.alter_column(u'accountings_accttran', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['auth.User']))

        # Changing field 'AcctTran.cleared'
        db.alter_column(u'accountings_accttran', 'cleared', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'AcctEntry.status'
        db.alter_column(u'accountings_acctentry', 'status', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'AcctEntry.creator'
        db.alter_column(u'accountings_acctentry', 'creator_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['auth.User']))

        # Changing field 'AcctEntry.exported'
        db.alter_column(u'accountings_acctentry', 'exported', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'AcctEntry.owner'
        db.alter_column(u'accountings_acctentry', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['auth.User']))

    models = {
        u'accountings.acct': {
            'Meta': {'object_name': 'Acct'},
            'account_number': ('django.db.models.fields.IntegerField', [], {'unique': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '5'})
        },
        u'accountings.acctentry': {
            'Meta': {'object_name': 'AcctEntry'},
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'accentry_creator'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50'}),
            'entry_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'exported': ('django.db.models.fields.NullBooleanField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'accentry_owner'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50'}),
            'source': ('django.db.models.fields.TextField', [], {}),
            'status': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'accountings.accttran': {
            'Meta': {'object_name': 'AcctTran'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'accts'", 'null': 'True', 'to': u"orm['accountings.Acct']"}),
            'acct_entry': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'trans'", 'to': u"orm['accountings.AcctEntry']"}),
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'cleared': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'accttran_creator'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'accttran_owner'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'status': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['accountings']