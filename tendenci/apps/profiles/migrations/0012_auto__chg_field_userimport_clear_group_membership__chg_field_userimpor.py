# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'UserImport.clear_group_membership'
        db.alter_column(u'profiles_userimport', 'clear_group_membership', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'UserImport.interactive'
        db.alter_column(u'profiles_userimport', 'interactive', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Profile.hide_address'
        db.alter_column(u'profiles_profile', 'hide_address', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Profile.hide_in_search'
        db.alter_column(u'profiles_profile', 'hide_in_search', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Profile.allow_user_view'
        db.alter_column(u'profiles_profile', 'allow_user_view', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Profile.hide_email'
        db.alter_column(u'profiles_profile', 'hide_email', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Profile.first_responder'
        db.alter_column(u'profiles_profile', 'first_responder', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Profile.allow_anonymous_view'
        db.alter_column(u'profiles_profile', 'allow_anonymous_view', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Profile.status'
        db.alter_column(u'profiles_profile', 'status', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Profile.remember_login'
        db.alter_column(u'profiles_profile', 'remember_login', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Profile.agreed_to_tos'
        db.alter_column(u'profiles_profile', 'agreed_to_tos', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Profile.exported'
        db.alter_column(u'profiles_profile', 'exported', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Profile.hide_phone'
        db.alter_column(u'profiles_profile', 'hide_phone', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Profile.allow_user_edit'
        db.alter_column(u'profiles_profile', 'allow_user_edit', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Profile.allow_member_view'
        db.alter_column(u'profiles_profile', 'allow_member_view', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Profile.direct_mail'
        db.alter_column(u'profiles_profile', 'direct_mail', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Profile.allow_member_edit'
        db.alter_column(u'profiles_profile', 'allow_member_edit', self.gf('django.db.models.fields.NullBooleanField')(null=True))

    def backwards(self, orm):

        # Changing field 'UserImport.clear_group_membership'
        db.alter_column(u'profiles_userimport', 'clear_group_membership', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'UserImport.interactive'
        db.alter_column(u'profiles_userimport', 'interactive', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Profile.hide_address'
        db.alter_column(u'profiles_profile', 'hide_address', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Profile.hide_in_search'
        db.alter_column(u'profiles_profile', 'hide_in_search', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Profile.allow_user_view'
        db.alter_column(u'profiles_profile', 'allow_user_view', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Profile.hide_email'
        db.alter_column(u'profiles_profile', 'hide_email', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Profile.first_responder'
        db.alter_column(u'profiles_profile', 'first_responder', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Profile.allow_anonymous_view'
        db.alter_column(u'profiles_profile', 'allow_anonymous_view', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Profile.status'
        db.alter_column(u'profiles_profile', 'status', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Profile.remember_login'
        db.alter_column(u'profiles_profile', 'remember_login', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Profile.agreed_to_tos'
        db.alter_column(u'profiles_profile', 'agreed_to_tos', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Profile.exported'
        db.alter_column(u'profiles_profile', 'exported', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Profile.hide_phone'
        db.alter_column(u'profiles_profile', 'hide_phone', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Profile.allow_user_edit'
        db.alter_column(u'profiles_profile', 'allow_user_edit', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Profile.allow_member_view'
        db.alter_column(u'profiles_profile', 'allow_member_view', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Profile.direct_mail'
        db.alter_column(u'profiles_profile', 'direct_mail', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Profile.allow_member_edit'
        db.alter_column(u'profiles_profile', 'allow_member_edit', self.gf('django.db.models.fields.BooleanField')())

    models = {
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
        },
        u'entities.entity': {
            'Meta': {'ordering': "('entity_name',)", 'object_name': 'Entity'},
            'admin_notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'allow_anonymous_edit': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_anonymous_view': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'allow_member_edit': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_member_view': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_user_edit': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_user_view': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'contact_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'entity_creator'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'entity_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'entity_parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'entity_children'", 'null': 'True', 'to': u"orm['entities.Entity']"}),
            'entity_type': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'entity_owner'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'status': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'summary': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'website': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'})
        },
        u'profiles.profile': {
            'Meta': {'object_name': 'Profile'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'address2': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'address_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'admin_notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'agreed_to_tos': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'allow_anonymous_view': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'allow_member_edit': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_member_view': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_user_edit': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_user_view': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'company': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'county': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'profiles_profile_creator'", 'to': u"orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'department': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'direct_mail': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'display_name': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'dob': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'education': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'email2': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['entities.Entity']", 'null': 'True', 'blank': 'True'}),
            'exported': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'first_responder': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'hide_address': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'hide_email': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'hide_in_search': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'hide_phone': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'historical_member_number': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'home_phone': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'initials': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'language': ('django.db.models.fields.CharField', [], {'default': "'en'", 'max_length': '10'}),
            'mailing_name': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'member_number': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'mobile_phone': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'original_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'profiles_profile_owner'", 'to': u"orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'phone2': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'pl_id': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'position_assignment': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'position_title': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'referral_source': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'remember_login': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'salutation': ('django.db.models.fields.CharField', [], {'max_length': '15', 'blank': 'True'}),
            'sex': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'sf_contact_id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'spouse': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'ssn': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'status': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'student': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'time_zone': ('timezones.fields.TimeZoneField', [], {'default': "'US/Central'", 'max_length': '100'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'url2': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'profile'", 'unique': 'True', 'to': u"orm['auth.User']"}),
            'work_phone': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'})
        },
        u'profiles.userimport': {
            'Meta': {'object_name': 'UserImport'},
            'clear_group_membership': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'complete_dt': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'group_id': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'header_line': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '3000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interactive': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'num_processed': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'override': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'recap_file': ('django.db.models.fields.files.FileField', [], {'max_length': '260', 'null': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'not_started'", 'max_length': '50'}),
            'summary': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '500', 'null': 'True'}),
            'total_rows': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'upload_file': ('django.db.models.fields.files.FileField', [], {'max_length': '260', 'null': 'True'})
        },
        u'profiles.userimportdata': {
            'Meta': {'object_name': 'UserImportData'},
            'action_taken': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'}),
            'error': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '500'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'row_data': ('tendenci.apps.base.fields.DictField', [], {}),
            'row_num': ('django.db.models.fields.IntegerField', [], {}),
            'uimport': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_import_data'", 'to': u"orm['profiles.UserImport']"})
        }
    }

    complete_apps = ['profiles']