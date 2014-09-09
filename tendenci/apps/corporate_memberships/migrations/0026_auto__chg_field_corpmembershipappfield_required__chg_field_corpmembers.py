# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'CorpMembershipAppField.required'
        db.alter_column(u'corporate_memberships_corpmembershipappfield', 'required', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'CorpMembershipAppField.admin_only'
        db.alter_column(u'corporate_memberships_corpmembershipappfield', 'admin_only', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'CorpMembershipAppField.display'
        db.alter_column(u'corporate_memberships_corpmembershipappfield', 'display', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'CorpMembership.allow_user_view'
        db.alter_column(u'corporate_memberships_corpmembership', 'allow_user_view', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'CorpMembership.status'
        db.alter_column(u'corporate_memberships_corpmembership', 'status', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'CorpMembership.approved'
        db.alter_column(u'corporate_memberships_corpmembership', 'approved', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'CorpMembership.allow_user_edit'
        db.alter_column(u'corporate_memberships_corpmembership', 'allow_user_edit', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'CorpMembership.renewal'
        db.alter_column(u'corporate_memberships_corpmembership', 'renewal', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'CorpMembership.allow_member_view'
        db.alter_column(u'corporate_memberships_corpmembership', 'allow_member_view', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'CorpMembership.allow_member_edit'
        db.alter_column(u'corporate_memberships_corpmembership', 'allow_member_edit', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'CorpMembership.allow_anonymous_view'
        db.alter_column(u'corporate_memberships_corpmembership', 'allow_anonymous_view', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'CorpMembershipRep.is_member_rep'
        db.alter_column(u'corporate_memberships_corpmembershiprep', 'is_member_rep', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'CorpMembershipRep.is_dues_rep'
        db.alter_column(u'corporate_memberships_corpmembershiprep', 'is_dues_rep', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'CorpMembershipApp.allow_user_view'
        db.alter_column(u'corporate_memberships_corpmembershipapp', 'allow_user_view', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'CorpMembershipApp.include_tax'
        db.alter_column(u'corporate_memberships_corpmembershipapp', 'include_tax', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'CorpMembershipApp.allow_anonymous_view'
        db.alter_column(u'corporate_memberships_corpmembershipapp', 'allow_anonymous_view', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'CorpMembershipApp.status'
        db.alter_column(u'corporate_memberships_corpmembershipapp', 'status', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'CorpMembershipApp.allow_user_edit'
        db.alter_column(u'corporate_memberships_corpmembershipapp', 'allow_user_edit', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'CorpMembershipApp.allow_member_view'
        db.alter_column(u'corporate_memberships_corpmembershipapp', 'allow_member_view', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'CorpMembershipApp.allow_member_edit'
        db.alter_column(u'corporate_memberships_corpmembershipapp', 'allow_member_edit', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'NoticeLogRecord.action_taken'
        db.alter_column(u'corporate_memberships_noticelogrecord', 'action_taken', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'FreePassesStat.status'
        db.alter_column(u'corporate_memberships_freepassesstat', 'status', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'FreePassesStat.allow_anonymous_view'
        db.alter_column(u'corporate_memberships_freepassesstat', 'allow_anonymous_view', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'FreePassesStat.allow_user_edit'
        db.alter_column(u'corporate_memberships_freepassesstat', 'allow_user_edit', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'FreePassesStat.allow_user_view'
        db.alter_column(u'corporate_memberships_freepassesstat', 'allow_user_view', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'FreePassesStat.allow_member_view'
        db.alter_column(u'corporate_memberships_freepassesstat', 'allow_member_view', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'FreePassesStat.allow_member_edit'
        db.alter_column(u'corporate_memberships_freepassesstat', 'allow_member_edit', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'IndivEmailVerification.verified'
        db.alter_column(u'corporate_memberships_indivemailverification', 'verified', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'CorporateMembershipType.status'
        db.alter_column(u'corporate_memberships_corporatemembershiptype', 'status', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'CorporateMembershipType.allow_user_view'
        db.alter_column(u'corporate_memberships_corporatemembershiptype', 'allow_user_view', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'CorporateMembershipType.allow_anonymous_view'
        db.alter_column(u'corporate_memberships_corporatemembershiptype', 'allow_anonymous_view', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'CorporateMembershipType.admin_only'
        db.alter_column(u'corporate_memberships_corporatemembershiptype', 'admin_only', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'CorporateMembershipType.apply_threshold'
        db.alter_column(u'corporate_memberships_corporatemembershiptype', 'apply_threshold', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'CorporateMembershipType.allow_user_edit'
        db.alter_column(u'corporate_memberships_corporatemembershiptype', 'allow_user_edit', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'CorporateMembershipType.allow_member_view'
        db.alter_column(u'corporate_memberships_corporatemembershiptype', 'allow_member_view', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'CorporateMembershipType.allow_member_edit'
        db.alter_column(u'corporate_memberships_corporatemembershiptype', 'allow_member_edit', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'CorpMembershipImport.bind_members'
        db.alter_column(u'corporate_memberships_corpmembershipimport', 'bind_members', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'CorpProfile.status'
        db.alter_column(u'corporate_memberships_corpprofile', 'status', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'CorpProfile.allow_user_view'
        db.alter_column(u'corporate_memberships_corpprofile', 'allow_user_view', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'CorpProfile.allow_anonymous_view'
        db.alter_column(u'corporate_memberships_corpprofile', 'allow_anonymous_view', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'CorpProfile.tax_exempt'
        db.alter_column(u'corporate_memberships_corpprofile', 'tax_exempt', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'CorpProfile.allow_user_edit'
        db.alter_column(u'corporate_memberships_corpprofile', 'allow_user_edit', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'CorpProfile.allow_member_view'
        db.alter_column(u'corporate_memberships_corpprofile', 'allow_member_view', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'CorpProfile.allow_member_edit'
        db.alter_column(u'corporate_memberships_corpprofile', 'allow_member_edit', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Notice.status'
        db.alter_column(u'corporate_memberships_notice', 'status', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Notice.system_generated'
        db.alter_column(u'corporate_memberships_notice', 'system_generated', self.gf('django.db.models.fields.NullBooleanField')(null=True))

    def backwards(self, orm):

        # Changing field 'CorpMembershipAppField.required'
        db.alter_column(u'corporate_memberships_corpmembershipappfield', 'required', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'CorpMembershipAppField.admin_only'
        db.alter_column(u'corporate_memberships_corpmembershipappfield', 'admin_only', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'CorpMembershipAppField.display'
        db.alter_column(u'corporate_memberships_corpmembershipappfield', 'display', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'CorpMembership.allow_user_view'
        db.alter_column(u'corporate_memberships_corpmembership', 'allow_user_view', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'CorpMembership.status'
        db.alter_column(u'corporate_memberships_corpmembership', 'status', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'CorpMembership.approved'
        db.alter_column(u'corporate_memberships_corpmembership', 'approved', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'CorpMembership.allow_user_edit'
        db.alter_column(u'corporate_memberships_corpmembership', 'allow_user_edit', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'CorpMembership.renewal'
        db.alter_column(u'corporate_memberships_corpmembership', 'renewal', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'CorpMembership.allow_member_view'
        db.alter_column(u'corporate_memberships_corpmembership', 'allow_member_view', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'CorpMembership.allow_member_edit'
        db.alter_column(u'corporate_memberships_corpmembership', 'allow_member_edit', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'CorpMembership.allow_anonymous_view'
        db.alter_column(u'corporate_memberships_corpmembership', 'allow_anonymous_view', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'CorpMembershipRep.is_member_rep'
        db.alter_column(u'corporate_memberships_corpmembershiprep', 'is_member_rep', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'CorpMembershipRep.is_dues_rep'
        db.alter_column(u'corporate_memberships_corpmembershiprep', 'is_dues_rep', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'CorpMembershipApp.allow_user_view'
        db.alter_column(u'corporate_memberships_corpmembershipapp', 'allow_user_view', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'CorpMembershipApp.include_tax'
        db.alter_column(u'corporate_memberships_corpmembershipapp', 'include_tax', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'CorpMembershipApp.allow_anonymous_view'
        db.alter_column(u'corporate_memberships_corpmembershipapp', 'allow_anonymous_view', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'CorpMembershipApp.status'
        db.alter_column(u'corporate_memberships_corpmembershipapp', 'status', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'CorpMembershipApp.allow_user_edit'
        db.alter_column(u'corporate_memberships_corpmembershipapp', 'allow_user_edit', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'CorpMembershipApp.allow_member_view'
        db.alter_column(u'corporate_memberships_corpmembershipapp', 'allow_member_view', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'CorpMembershipApp.allow_member_edit'
        db.alter_column(u'corporate_memberships_corpmembershipapp', 'allow_member_edit', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'NoticeLogRecord.action_taken'
        db.alter_column(u'corporate_memberships_noticelogrecord', 'action_taken', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'FreePassesStat.status'
        db.alter_column(u'corporate_memberships_freepassesstat', 'status', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'FreePassesStat.allow_anonymous_view'
        db.alter_column(u'corporate_memberships_freepassesstat', 'allow_anonymous_view', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'FreePassesStat.allow_user_edit'
        db.alter_column(u'corporate_memberships_freepassesstat', 'allow_user_edit', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'FreePassesStat.allow_user_view'
        db.alter_column(u'corporate_memberships_freepassesstat', 'allow_user_view', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'FreePassesStat.allow_member_view'
        db.alter_column(u'corporate_memberships_freepassesstat', 'allow_member_view', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'FreePassesStat.allow_member_edit'
        db.alter_column(u'corporate_memberships_freepassesstat', 'allow_member_edit', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'IndivEmailVerification.verified'
        db.alter_column(u'corporate_memberships_indivemailverification', 'verified', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'CorporateMembershipType.status'
        db.alter_column(u'corporate_memberships_corporatemembershiptype', 'status', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'CorporateMembershipType.allow_user_view'
        db.alter_column(u'corporate_memberships_corporatemembershiptype', 'allow_user_view', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'CorporateMembershipType.allow_anonymous_view'
        db.alter_column(u'corporate_memberships_corporatemembershiptype', 'allow_anonymous_view', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'CorporateMembershipType.admin_only'
        db.alter_column(u'corporate_memberships_corporatemembershiptype', 'admin_only', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'CorporateMembershipType.apply_threshold'
        db.alter_column(u'corporate_memberships_corporatemembershiptype', 'apply_threshold', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'CorporateMembershipType.allow_user_edit'
        db.alter_column(u'corporate_memberships_corporatemembershiptype', 'allow_user_edit', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'CorporateMembershipType.allow_member_view'
        db.alter_column(u'corporate_memberships_corporatemembershiptype', 'allow_member_view', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'CorporateMembershipType.allow_member_edit'
        db.alter_column(u'corporate_memberships_corporatemembershiptype', 'allow_member_edit', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'CorpMembershipImport.bind_members'
        db.alter_column(u'corporate_memberships_corpmembershipimport', 'bind_members', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'CorpProfile.status'
        db.alter_column(u'corporate_memberships_corpprofile', 'status', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'CorpProfile.allow_user_view'
        db.alter_column(u'corporate_memberships_corpprofile', 'allow_user_view', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'CorpProfile.allow_anonymous_view'
        db.alter_column(u'corporate_memberships_corpprofile', 'allow_anonymous_view', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'CorpProfile.tax_exempt'
        db.alter_column(u'corporate_memberships_corpprofile', 'tax_exempt', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'CorpProfile.allow_user_edit'
        db.alter_column(u'corporate_memberships_corpprofile', 'allow_user_edit', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'CorpProfile.allow_member_view'
        db.alter_column(u'corporate_memberships_corpprofile', 'allow_member_view', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'CorpProfile.allow_member_edit'
        db.alter_column(u'corporate_memberships_corpprofile', 'allow_member_edit', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Notice.status'
        db.alter_column(u'corporate_memberships_notice', 'status', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Notice.system_generated'
        db.alter_column(u'corporate_memberships_notice', 'system_generated', self.gf('django.db.models.fields.BooleanField')())

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
        u'corporate_memberships.corpmembership': {
            'Meta': {'object_name': 'CorpMembership'},
            'admin_notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'allow_anonymous_view': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'allow_member_edit': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_member_view': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_user_edit': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_user_view': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'anonymous_creator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['corporate_memberships.Creator']", 'null': 'True'}),
            'approved': ('django.db.models.fields.NullBooleanField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'approved_denied_dt': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'approved_denied_user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True'}),
            'corp_profile': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'corp_memberships'", 'to': u"orm['corporate_memberships.CorpProfile']"}),
            'corporate_membership_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['corporate_memberships.CorporateMembershipType']"}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "u'corporate_memberships_corpmembership_creator'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'corporate_memberships_corpmembership_entity'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': u"orm['entities.Entity']", 'blank': 'True', 'null': 'True'}),
            'expiration_dt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['invoices.Invoice']", 'null': 'True', 'blank': 'True'}),
            'join_dt': ('django.db.models.fields.DateTimeField', [], {}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "u'corporate_memberships_corpmembership_owner'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'payment_method': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['payments.PaymentMethod']", 'null': 'True'}),
            'renew_dt': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'renewal': ('django.db.models.fields.NullBooleanField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'total_passes_allowed': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'blank': 'True'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'corporate_memberships.corpmembershipapp': {
            'Meta': {'ordering': "('name',)", 'object_name': 'CorpMembershipApp'},
            'allow_anonymous_view': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'allow_member_edit': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_member_view': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_user_edit': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_user_view': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'authentication_method': ('django.db.models.fields.CharField', [], {'default': "'admin'", 'max_length': '50'}),
            'confirmation_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'corp_memb_type': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['corporate_memberships.CorporateMembershipType']", 'symmetrical': 'False'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "u'corporate_memberships_corpmembershipapp_creator'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'description': ('tinymce.models.HTMLField', [], {'null': 'True', 'blank': 'True'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'corporate_memberships_corpmembershipapp_entity'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': u"orm['entities.Entity']", 'blank': 'True', 'null': 'True'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'include_tax': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'memb_app': ('django.db.models.fields.related.OneToOneField', [], {'default': '1', 'related_name': "'corp_app'", 'unique': 'True', 'to': u"orm['memberships.MembershipApp']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '155'}),
            'notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "u'corporate_memberships_corpmembershipapp_owner'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'payment_methods': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['payments.PaymentMethod']", 'symmetrical': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '155'}),
            'status': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'tax_rate': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '5', 'decimal_places': '4', 'blank': 'True'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'corporate_memberships.corpmembershipappfield': {
            'Meta': {'ordering': "('position',)", 'object_name': 'CorpMembershipAppField'},
            'admin_only': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'choices': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'corp_app': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fields'", 'to': u"orm['corporate_memberships.CorpMembershipApp']"}),
            'css_class': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50', 'blank': 'True'}),
            'default_value': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'display': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'field_layout': ('django.db.models.fields.CharField', [], {'default': "'1'", 'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'field_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '30', 'blank': 'True'}),
            'field_type': ('django.db.models.fields.CharField', [], {'default': "'CharField'", 'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'help_text': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '2000', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '2000'}),
            'position': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'required': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'size': ('django.db.models.fields.CharField', [], {'default': "'m'", 'max_length': '1', 'null': 'True', 'blank': 'True'})
        },
        u'corporate_memberships.corpmembershipauthdomain': {
            'Meta': {'object_name': 'CorpMembershipAuthDomain'},
            'corp_profile': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'authorized_domains'", 'to': u"orm['corporate_memberships.CorpProfile']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'corporate_memberships.corpmembershipimport': {
            'Meta': {'object_name': 'CorpMembershipImport'},
            'bind_members': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'complete_dt': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'default': "'name'", 'max_length': '50'}),
            'num_processed': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'override': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'not_started'", 'max_length': '50'}),
            'summary': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '500', 'null': 'True'}),
            'total_rows': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'upload_file': ('django.db.models.fields.files.FileField', [], {'max_length': '260'})
        },
        u'corporate_memberships.corpmembershipimportdata': {
            'Meta': {'object_name': 'CorpMembershipImportData'},
            'action_taken': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mimport': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'corp_membership_import_data'", 'to': u"orm['corporate_memberships.CorpMembershipImport']"}),
            'row_data': ('tendenci.apps.base.fields.DictField', [], {}),
            'row_num': ('django.db.models.fields.IntegerField', [], {})
        },
        u'corporate_memberships.corpmembershiprep': {
            'Meta': {'unique_together': "(('corp_profile', 'user'),)", 'object_name': 'CorpMembershipRep'},
            'corp_profile': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reps'", 'to': u"orm['corporate_memberships.CorpProfile']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_dues_rep': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'is_member_rep': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'corporate_memberships.corporatemembershiptype': {
            'Meta': {'ordering': "('position',)", 'object_name': 'CorporateMembershipType'},
            'admin_only': ('django.db.models.fields.NullBooleanField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'allow_anonymous_view': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'allow_member_edit': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_member_view': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_user_edit': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_user_view': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'apply_threshold': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "u'corporate_memberships_corporatemembershiptype_creator'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'corporate_memberships_corporatemembershiptype_entity'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': u"orm['entities.Entity']", 'blank': 'True', 'null': 'True'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'individual_threshold': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'individual_threshold_price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '15', 'decimal_places': '2', 'blank': 'True'}),
            'membership_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['memberships.MembershipType']"}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'number_passes': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "u'corporate_memberships_corporatemembershiptype_owner'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'position': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '2', 'blank': 'True'}),
            'renewal_price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '15', 'decimal_places': '2', 'blank': 'True'}),
            'status': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'corporate_memberships.corpprofile': {
            'Meta': {'object_name': 'CorpProfile'},
            'address': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '150', 'blank': 'True'}),
            'address2': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'allow_anonymous_view': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'allow_member_edit': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_member_view': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_user_edit': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_user_view': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'annual_ad_expenditure': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '75', 'blank': 'True'}),
            'annual_revenue': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '75', 'blank': 'True'}),
            'chapter': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '150', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50', 'blank': 'True'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "u'corporate_memberships_corpprofile_creator'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'corporate_memberships_corpprofile_entity'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': u"orm['entities.Entity']", 'blank': 'True', 'null': 'True'}),
            'expectations': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'industry': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['industries.Industry']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '250'}),
            'notes': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'number_employees': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "u'corporate_memberships_corpprofile_owner'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'phone': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50', 'blank': 'True'}),
            'referral_source': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '150', 'blank': 'True'}),
            'referral_source_member_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50', 'blank': 'True'}),
            'referral_source_member_number': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50', 'blank': 'True'}),
            'referral_source_other': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '150', 'blank': 'True'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['regions.Region']", 'null': 'True', 'blank': 'True'}),
            'secret_code': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50', 'blank': 'True'}),
            'status': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'tax_exempt': ('django.db.models.fields.NullBooleanField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'ud1': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'ud2': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'ud3': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'ud4': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'ud5': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'ud6': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'ud7': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'ud8': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'zip': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50', 'blank': 'True'})
        },
        u'corporate_memberships.creator': {
            'Meta': {'object_name': 'Creator'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'hash': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '32'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'})
        },
        u'corporate_memberships.freepassesstat': {
            'Meta': {'object_name': 'FreePassesStat'},
            'allow_anonymous_view': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'allow_member_edit': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_member_view': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_user_edit': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_user_view': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'corp_membership': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'passes_used'", 'to': u"orm['corporate_memberships.CorpMembership']"}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "u'corporate_memberships_freepassesstat_creator'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'corporate_memberships_freepassesstat_entity'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': u"orm['entities.Entity']", 'blank': 'True', 'null': 'True'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'passes_used'", 'to': u"orm['events.Event']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "u'corporate_memberships_freepassesstat_owner'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'registrant': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.Registrant']", 'null': 'True'}),
            'status': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True'})
        },
        u'corporate_memberships.indivemailverification': {
            'Meta': {'object_name': 'IndivEmailVerification'},
            'corp_profile': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['corporate_memberships.CorpProfile']"}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'corp_email_veri8n_creator'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'updated_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'corp_email_veri8n_updator'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'verified': ('django.db.models.fields.NullBooleanField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'verified_dt': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'verified_email': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'corporate_memberships.indivmembershiprenewentry': {
            'Meta': {'object_name': 'IndivMembershipRenewEntry'},
            'corp_membership': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['corporate_memberships.CorpMembership']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'membership': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['memberships.MembershipDefault']"}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'pending'", 'max_length': '50'})
        },
        u'corporate_memberships.notice': {
            'Meta': {'object_name': 'Notice'},
            'content_type': ('django.db.models.fields.CharField', [], {'default': "'html'", 'max_length': '10'}),
            'corporate_membership_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['corporate_memberships.CorporateMembershipType']", 'null': 'True', 'blank': 'True'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'corporate_membership_notice_creator'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'email_content': ('tinymce.models.HTMLField', [], {}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notice_name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'notice_time': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'notice_type': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'num_days': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'corporate_membership_notice_owner'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'sender': ('django.db.models.fields.EmailField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'sender_display': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'system_generated': ('django.db.models.fields.NullBooleanField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'corporate_memberships.noticelog': {
            'Meta': {'object_name': 'NoticeLog'},
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notice': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'logs'", 'to': u"orm['corporate_memberships.Notice']"}),
            'notice_sent_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'num_sent': ('django.db.models.fields.IntegerField', [], {})
        },
        u'corporate_memberships.noticelogrecord': {
            'Meta': {'object_name': 'NoticeLogRecord'},
            'action_taken': ('django.db.models.fields.NullBooleanField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'action_taken_dt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'corp_membership': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'log_records'", 'to': u"orm['corporate_memberships.CorpMembership']"}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notice_log': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'log_records'", 'to': u"orm['corporate_memberships.NoticeLog']"})
        },
        u'directories.directory': {
            'Meta': {'object_name': 'Directory'},
            'activation_dt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'address': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'address2': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'admin_notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'allow_anonymous_view': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'allow_member_edit': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_member_view': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_user_edit': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_user_view': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'body': ('tinymce.models.HTMLField', [], {}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "u'directories_directory_creator'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'design_notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'email2': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'enclosure_length': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'enclosure_type': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'enclosure_url': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'directories_directory_entity'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': u"orm['entities.Entity']", 'blank': 'True', 'null': 'True'}),
            'expiration_dt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'headline': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['invoices.Invoice']", 'null': 'True', 'blank': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'list_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'logo_file': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['files.File']", 'null': 'True'}),
            'meta': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['meta.Meta']", 'unique': 'True', 'null': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "u'directories_directory_owner'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'payment_method': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'phone2': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'pricing': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['directories.DirectoryPricing']", 'null': 'True'}),
            'renewal_notice_sent': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'requested_duration': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'slug': ('tendenci.apps.base.fields.SlugField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'status': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'summary': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'syndicate': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'tags': ('tagging.fields.TagField', [], {}),
            'timezone': ('timezones.fields.TimeZoneField', [], {'default': "'US/Central'", 'max_length': '100'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'website': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'})
        },
        u'directories.directorypricing': {
            'Meta': {'object_name': 'DirectoryPricing'},
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'directory_pricing_creator'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'duration': ('django.db.models.fields.IntegerField', [], {'blank': 'True'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'directory_pricing_owner'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'premium_price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '2', 'blank': 'True'}),
            'premium_price_member': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '2', 'blank': 'True'}),
            'regular_price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '2', 'blank': 'True'}),
            'regular_price_member': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '2', 'blank': 'True'}),
            'show_member_pricing': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'emails.email': {
            'Meta': {'object_name': 'Email'},
            'allow_anonymous_view': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'allow_member_edit': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_member_view': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_user_edit': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_user_view': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'attachments': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '500', 'blank': 'True'}),
            'body': ('tinymce.models.HTMLField', [], {}),
            'content_type': ('django.db.models.fields.CharField', [], {'default': "'text/html'", 'max_length': '255'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "u'emails_email_creator'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'emails_email_entity'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': u"orm['entities.Entity']", 'blank': 'True', 'null': 'True'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "u'emails_email_owner'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'recipient': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'recipient_bcc': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'recipient_cc': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'recipient_cc_display': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'recipient_dispaly': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'reply_to': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'sender': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'sender_display': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'status': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
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
        u'events.customregform': {
            'Meta': {'object_name': 'CustomRegForm'},
            'address': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'comments': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'company_name': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'custom_reg_creator'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'email': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'mail_name': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'meal_option': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'notes': ('django.db.models.fields.TextField', [], {'max_length': '2000', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'custom_reg_owner'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'phone': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'position_title': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'zip': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'})
        },
        u'events.customregformentry': {
            'Meta': {'object_name': 'CustomRegFormEntry'},
            'entry_time': ('django.db.models.fields.DateTimeField', [], {}),
            'form': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'entries'", 'to': u"orm['events.CustomRegForm']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'events.event': {
            'Meta': {'object_name': 'Event'},
            'all_day': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_anonymous_view': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'allow_member_edit': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_member_view': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_user_edit': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_user_view': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "u'events_event_creator'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'display_event_registrants': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'display_registrants_to': ('django.db.models.fields.CharField', [], {'default': "'admin'", 'max_length': '6'}),
            'enable_private_slug': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'end_dt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 10, 9, 0, 0)'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'events_event_entity'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': u"orm['entities.Entity']", 'blank': 'True', 'null': 'True'}),
            'external_url': ('django.db.models.fields.URLField', [], {'default': "u''", 'max_length': '200', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['user_groups.Group']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.EventPhoto']", 'null': 'True', 'blank': 'True'}),
            'is_recurring_event': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'mark_registration_ended': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'meta': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['meta.Meta']", 'unique': 'True', 'null': 'True'}),
            'on_weekend': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "u'events_event_owner'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'place': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.Place']", 'null': 'True'}),
            'priority': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'private_slug': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '500', 'blank': 'True'}),
            'recurring_event': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.RecurringEvent']", 'null': 'True'}),
            'registration_configuration': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['events.RegistrationConfiguration']", 'unique': 'True', 'null': 'True'}),
            'start_dt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 10, 9, 0, 0)'}),
            'status': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'tags': ('tagging.fields.TagField', [], {}),
            'timezone': ('timezones.fields.TimeZoneField', [], {'default': "'US/Central'", 'max_length': '100'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.Type']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'events.eventphoto': {
            'Meta': {'object_name': 'EventPhoto', '_ormbases': [u'files.File']},
            u'file_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['files.File']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'events.place': {
            'Meta': {'object_name': 'Place'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'})
        },
        u'events.recurringevent': {
            'Meta': {'object_name': 'RecurringEvent'},
            'ends_on': ('django.db.models.fields.DateTimeField', [], {}),
            'frequency': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'repeat_type': ('django.db.models.fields.IntegerField', [], {}),
            'starts_on': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 10, 9, 0, 0)'})
        },
        u'events.regconfpricing': {
            'Meta': {'ordering': "('position',)", 'object_name': 'RegConfPricing'},
            'allow_anonymous': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_member': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_user': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'end_dt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 10, 9, 0, 0)'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['user_groups.Group']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'include_tax': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'payment_required': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '21', 'decimal_places': '2'}),
            'quantity': ('django.db.models.fields.IntegerField', [], {'default': '1', 'blank': 'True'}),
            'reg_conf': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.RegistrationConfiguration']", 'null': 'True', 'blank': 'True'}),
            'reg_form': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'regconfpricings'", 'null': 'True', 'to': u"orm['events.CustomRegForm']"}),
            'start_dt': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 9, 9, 0, 0)'}),
            'status': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'tax_rate': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '5', 'decimal_places': '4', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'})
        },
        u'events.registrant': {
            'Meta': {'object_name': 'Registrant'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '21', 'decimal_places': '2', 'blank': 'True'}),
            'cancel_dt': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'checked_in': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'checked_in_dt': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'comments': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'company_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'custom_reg_form_entry': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'registrants'", 'null': 'True', 'to': u"orm['events.CustomRegFormEntry']"}),
            'discount_amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '2'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'groups': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_primary': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'mail_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'meal_option': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'memberid': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'override': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'override_price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '21', 'decimal_places': '2', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'position_title': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'pricing': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.RegConfPricing']", 'null': 'True'}),
            'registration': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.Registration']"}),
            'reminder': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'use_free_pass': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'on_delete': 'models.SET_NULL', 'blank': 'True'}),
            'zip': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'})
        },
        u'events.registration': {
            'Meta': {'object_name': 'Registration'},
            'addons_added': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'amount_paid': ('django.db.models.fields.DecimalField', [], {'max_digits': '21', 'decimal_places': '2'}),
            'canceled': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'created_registrations'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.Event']"}),
            'guid': ('django.db.models.fields.TextField', [], {'max_length': '40'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['invoices.Invoice']", 'null': 'True', 'blank': 'True'}),
            'is_table': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'override_price_table': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '21', 'decimal_places': '2', 'blank': 'True'}),
            'override_table': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'owned_registrations'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'payment_method': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['payments.PaymentMethod']", 'null': 'True'}),
            'quantity': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'reg_conf_price': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.RegConfPricing']", 'null': 'True'}),
            'reminder': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'events.registrationconfiguration': {
            'Meta': {'object_name': 'RegistrationConfiguration'},
            'allow_free_pass': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'bind_reg_form_to_conf_only': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'discount_eligible': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'display_registration_stats': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['emails.Email']", 'null': 'True'}),
            'enabled': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_guest_price': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'limit': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'payment_method': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['payments.PaymentMethod']", 'symmetrical': 'False'}),
            'payment_required': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'reg_form': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'regconfs'", 'null': 'True', 'to': u"orm['events.CustomRegForm']"}),
            'registration_email_text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'registration_email_type': ('django.db.models.fields.CharField', [], {'default': "'default'", 'max_length': '20'}),
            'reminder_days': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'require_guests_info': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'send_reminder': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'use_custom_reg_form': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'})
        },
        u'events.type': {
            'Meta': {'object_name': 'Type'},
            'color_set': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['events.TypeColorSet']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'})
        },
        u'events.typecolorset': {
            'Meta': {'object_name': 'TypeColorSet'},
            'bg_color': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'border_color': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'fg_color': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'files.file': {
            'Meta': {'object_name': 'File'},
            'allow_anonymous_view': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'allow_member_edit': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_member_view': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_user_edit': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_user_view': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "u'files_file_creator'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'files_file_entity'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': u"orm['entities.Entity']", 'blank': 'True', 'null': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '260'}),
            'file_cat': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'file_cat'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['files.FilesCategory']"}),
            'file_sub_cat': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'file_subcat'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['files.FilesCategory']"}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['user_groups.Group']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_public': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "u'files_file_owner'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'status': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'tags': ('tagging.fields.TagField', [], {'null': 'True'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'files.filescategory': {
            'Meta': {'ordering': "('name',)", 'object_name': 'FilesCategory'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['files.FilesCategory']", 'null': 'True'})
        },
        u'industries.industry': {
            'Meta': {'ordering': "('position', '-update_dt')", 'object_name': 'Industry'},
            'allow_anonymous_view': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'allow_member_edit': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_member_view': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_user_edit': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_user_view': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "u'industries_industry_creator'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'industries_industry_entity'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': u"orm['entities.Entity']", 'blank': 'True', 'null': 'True'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'industry_code': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'industry_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "u'industries_industry_owner'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'position': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'invoices.invoice': {
            'Meta': {'object_name': 'Invoice'},
            'admin_notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'arrival_date_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'balance': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '2', 'blank': 'True'}),
            'bill_to': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'bill_to_address': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'bill_to_city': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'bill_to_company': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'bill_to_country': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'bill_to_email': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'bill_to_fax': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'bill_to_first_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'bill_to_last_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'bill_to_phone': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'bill_to_state': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'bill_to_zip_code': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'box_and_packing': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '6', 'decimal_places': '2'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invoice_creator'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'disclaimer': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'discount_amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '2'}),
            'discount_code': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'due_date': ('django.db.models.fields.DateTimeField', [], {}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invoices'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': u"orm['entities.Entity']", 'blank': 'True', 'null': 'True'}),
            'fob': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'gift': ('django.db.models.fields.NullBooleanField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'greeting': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instructions': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'is_void': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'object_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'other': ('django.db.models.fields.CharField', [], {'max_length': '120', 'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invoice_owner'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'payments_credits': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '2', 'blank': 'True'}),
            'po': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'project': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'receipt': ('django.db.models.fields.NullBooleanField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'ship_date': ('django.db.models.fields.DateTimeField', [], {}),
            'ship_to': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'ship_to_address': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'ship_to_address_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'ship_to_city': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'ship_to_company': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'ship_to_country': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'ship_to_email': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'ship_to_fax': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'ship_to_first_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'ship_to_last_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'ship_to_phone': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'ship_to_state': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'ship_to_zip_code': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'ship_via': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'shipping': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '6', 'decimal_places': '2'}),
            'shipping_surcharge': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '6', 'decimal_places': '2'}),
            'status': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'estimate'", 'max_length': '50'}),
            'subtotal': ('django.db.models.fields.DecimalField', [], {'max_digits': '15', 'decimal_places': '2', 'blank': 'True'}),
            'tax': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '6', 'decimal_places': '4'}),
            'tax_exempt': ('django.db.models.fields.NullBooleanField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'tax_exemptid': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'tax_rate': ('django.db.models.fields.FloatField', [], {'default': '0', 'blank': 'True'}),
            'taxable': ('django.db.models.fields.NullBooleanField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'tender_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'terms': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'total': ('django.db.models.fields.DecimalField', [], {'max_digits': '15', 'decimal_places': '2', 'blank': 'True'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'variance': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '10', 'decimal_places': '4'}),
            'variance_notes': ('django.db.models.fields.TextField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'})
        },
        u'memberships.membershipapp': {
            'Meta': {'object_name': 'MembershipApp'},
            'allow_anonymous_view': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'allow_member_edit': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_member_view': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_multiple_membership': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'allow_user_edit': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_user_view': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'confirmation_text': ('tinymce.models.HTMLField', [], {}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "u'memberships_membershipapp_creator'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'discount_eligible': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'memberships_membershipapp_entity'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': u"orm['entities.Entity']", 'blank': 'True', 'null': 'True'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'include_tax': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'membership_types': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['memberships.MembershipType']", 'symmetrical': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '155'}),
            'notes': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "u'memberships_membershipapp_owner'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'payment_methods': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['payments.PaymentMethod']", 'symmetrical': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '200'}),
            'status': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'tax_rate': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '5', 'decimal_places': '4', 'blank': 'True'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'use_captcha': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'use_for_corp': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'})
        },
        u'memberships.membershipdefault': {
            'Meta': {'object_name': 'MembershipDefault'},
            'action_taken': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'action_taken_dt': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True'}),
            'action_taken_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'action_taken_set'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'admin_notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'affiliation_member_number': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'allow_anonymous_view': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'allow_member_edit': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_member_view': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_user_edit': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_user_view': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'app': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['memberships.MembershipApp']", 'null': 'True'}),
            'application_abandoned': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'application_abandoned_dt': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True'}),
            'application_abandoned_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'application_abandond_set'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'application_approved': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'application_approved_denied_dt': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True'}),
            'application_approved_denied_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'application_approved_denied_set'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'application_approved_dt': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True'}),
            'application_approved_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'application_approved_set'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'application_complete': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'application_complete_dt': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True'}),
            'application_complete_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'application_complete_set'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'application_denied': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'areas_of_expertise': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'blank': 'True'}),
            'bod_dt': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'certifications': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'chapter': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'company_size': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '50', 'blank': 'True'}),
            'corp_profile_id': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'corporate_membership_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "u'memberships_membershipdefault_creator'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'directory': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['directories.Directory']", 'null': 'True', 'blank': 'True'}),
            'directory_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'memberships_membershipdefault_entity'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': u"orm['entities.Entity']", 'blank': 'True', 'null': 'True'}),
            'expire_dt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'exported': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'government_agency': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '250', 'blank': 'True'}),
            'government_worker': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['user_groups.Group']", 'null': 'True', 'symmetrical': 'False'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'home_state': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '50', 'blank': 'True'}),
            'how_long_in_practice': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '50', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'industry': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['industries.Industry']", 'null': 'True', 'blank': 'True'}),
            'join_dt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'lang': ('django.db.models.fields.CharField', [], {'default': "'eng'", 'max_length': '10'}),
            'license_number': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '50', 'blank': 'True'}),
            'license_state': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '50', 'blank': 'True'}),
            'member_number': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'membership_set': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['memberships.MembershipSet']", 'null': 'True', 'blank': 'True'}),
            'membership_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['memberships.MembershipType']"}),
            'network_sectors': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '250', 'blank': 'True'}),
            'networking': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '250', 'blank': 'True'}),
            'newsletter_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'override': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'override_price': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "u'memberships_membershipdefault_owner'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'payment_method': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['payments.PaymentMethod']", 'null': 'True'}),
            'payment_received_dt': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'personnel_notified_dt': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'primary_practice': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '100', 'blank': 'True'}),
            'promotion_code': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '50', 'blank': 'True'}),
            'referer_url': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'referral_source': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'referral_source_member_name': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '50', 'blank': 'True'}),
            'referral_source_member_number': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '50', 'blank': 'True'}),
            'referral_source_other': ('django.db.models.fields.CharField', [], {'max_length': '150', 'blank': 'True'}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['regions.Region']", 'null': 'True', 'blank': 'True'}),
            'renew_dt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'renewal': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'work_experience': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'year_left_native_country': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'memberships.membershipset': {
            'Meta': {'object_name': 'MembershipSet'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['invoices.Invoice']"})
        },
        u'memberships.membershiptype': {
            'Meta': {'object_name': 'MembershipType'},
            'admin_fee': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '15', 'decimal_places': '2', 'blank': 'True'}),
            'admin_only': ('django.db.models.fields.NullBooleanField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'allow_anonymous_view': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'allow_member_edit': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_member_view': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_renewal': ('django.db.models.fields.NullBooleanField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'allow_user_edit': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_user_view': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "u'memberships_membershiptype_creator'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'memberships_membershiptype_entity'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': u"orm['entities.Entity']", 'blank': 'True', 'null': 'True'}),
            'expiration_grace_period': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'fixed_option': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'fixed_option1_day': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'fixed_option1_month': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'fixed_option1_year': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'fixed_option2_can_rollover': ('django.db.models.fields.NullBooleanField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'fixed_option2_day': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'fixed_option2_month': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'fixed_option2_rollover_days': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'membership_types'", 'to': u"orm['user_groups.Group']"}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'never_expires': ('django.db.models.fields.NullBooleanField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "u'memberships_membershiptype_owner'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'period': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'period_type': ('django.db.models.fields.CharField', [], {'default': "'rolling'", 'max_length': '10'}),
            'period_unit': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'position': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '15', 'decimal_places': '2', 'blank': 'True'}),
            'renewal': ('django.db.models.fields.NullBooleanField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'renewal_period_end': ('django.db.models.fields.IntegerField', [], {'default': '30'}),
            'renewal_period_start': ('django.db.models.fields.IntegerField', [], {'default': '30'}),
            'renewal_price': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '15', 'decimal_places': '2', 'blank': 'True'}),
            'renewal_require_approval': ('django.db.models.fields.NullBooleanField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'require_approval': ('django.db.models.fields.NullBooleanField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'require_payment_approval': ('django.db.models.fields.NullBooleanField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'rolling_option': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'rolling_option1_day': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'rolling_renew_option': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'rolling_renew_option1_day': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'rolling_renew_option2_day': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'status': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'meta.meta': {
            'Meta': {'object_name': 'Meta'},
            'canonical_url': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'payments.paymentmethod': {
            'Meta': {'object_name': 'PaymentMethod'},
            'admin_only': ('django.db.models.fields.NullBooleanField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'human_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_online': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'machine_name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'regions.region': {
            'Meta': {'object_name': 'Region'},
            'allow_anonymous_view': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'allow_member_edit': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_member_view': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_user_edit': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_user_view': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "u'regions_region_creator'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'regions_region_entity'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': u"orm['entities.Entity']", 'blank': 'True', 'null': 'True'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "u'regions_region_owner'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'region_code': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'region_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'status': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'user_groups.group': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Group'},
            'allow_anonymous_view': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'allow_member_edit': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_member_view': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_self_add': ('django.db.models.fields.NullBooleanField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'allow_self_remove': ('django.db.models.fields.NullBooleanField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'allow_user_edit': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_user_view': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'auto_respond': ('django.db.models.fields.NullBooleanField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'auto_respond_priority': ('django.db.models.fields.FloatField', [], {'default': '0', 'blank': 'True'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "u'user_groups_group_creator'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'dashboard_url': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'email_recipient': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'user_groups_group_entity'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': u"orm['entities.Entity']", 'blank': 'True', 'null': 'True'}),
            'group': ('django.db.models.fields.related.OneToOneField', [], {'default': 'None', 'to': u"orm['auth.Group']", 'unique': 'True', 'null': 'True'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.User']", 'through': u"orm['user_groups.GroupMembership']", 'symmetrical': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "u'user_groups_group_owner'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'group_permissions'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'show_as_option': ('django.db.models.fields.NullBooleanField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'slug': ('tendenci.apps.base.fields.SlugField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'status': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'sync_newsletters': ('django.db.models.fields.NullBooleanField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'distribution'", 'max_length': '75', 'blank': 'True'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'user_groups.groupmembership': {
            'Meta': {'unique_together': "(('group', 'member'),)", 'object_name': 'GroupMembership'},
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator_id': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user_groups.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'group_member'", 'to': u"orm['auth.User']"}),
            'owner_id': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'role': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'sort_order': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'status': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['corporate_memberships']