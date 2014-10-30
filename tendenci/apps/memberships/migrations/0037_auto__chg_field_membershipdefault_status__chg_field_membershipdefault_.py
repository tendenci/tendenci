# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'MembershipDefault.status'
        db.alter_column(u'memberships_membershipdefault', 'status', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'MembershipDefault.allow_member_edit'
        db.alter_column(u'memberships_membershipdefault', 'allow_member_edit', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'MembershipDefault.application_approved'
        db.alter_column(u'memberships_membershipdefault', 'application_approved', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'MembershipDefault.allow_user_view'
        db.alter_column(u'memberships_membershipdefault', 'allow_user_view', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'MembershipDefault.allow_anonymous_view'
        db.alter_column(u'memberships_membershipdefault', 'allow_anonymous_view', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'MembershipDefault.application_abandoned'
        db.alter_column(u'memberships_membershipdefault', 'application_abandoned', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'MembershipDefault.override'
        db.alter_column(u'memberships_membershipdefault', 'override', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'MembershipDefault.application_denied'
        db.alter_column(u'memberships_membershipdefault', 'application_denied', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'MembershipDefault.application_complete'
        db.alter_column(u'memberships_membershipdefault', 'application_complete', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'MembershipDefault.renewal'
        db.alter_column(u'memberships_membershipdefault', 'renewal', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'MembershipDefault.allow_member_view'
        db.alter_column(u'memberships_membershipdefault', 'allow_member_view', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'MembershipDefault.government_worker'
        db.alter_column(u'memberships_membershipdefault', 'government_worker', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'MembershipDefault.allow_user_edit'
        db.alter_column(u'memberships_membershipdefault', 'allow_user_edit', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'MembershipDefault.exported'
        db.alter_column(u'memberships_membershipdefault', 'exported', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'MembershipAppField.admin_only'
        db.alter_column(u'memberships_membershipappfield', 'admin_only', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'MembershipAppField.required'
        db.alter_column(u'memberships_membershipappfield', 'required', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'MembershipAppField.display'
        db.alter_column(u'memberships_membershipappfield', 'display', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Notice.status'
        db.alter_column(u'memberships_notice', 'status', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Notice.system_generated'
        db.alter_column(u'memberships_notice', 'system_generated', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'NoticeDefaultLogRecord.action_taken'
        db.alter_column(u'memberships_noticedefaultlogrecord', 'action_taken', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'MembershipType.allow_user_view'
        db.alter_column(u'memberships_membershiptype', 'allow_user_view', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'MembershipType.allow_renewal'
        db.alter_column(u'memberships_membershiptype', 'allow_renewal', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'MembershipType.require_approval'
        db.alter_column(u'memberships_membershiptype', 'require_approval', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'MembershipType.renewal_require_approval'
        db.alter_column(u'memberships_membershiptype', 'renewal_require_approval', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'MembershipType.fixed_option2_can_rollover'
        db.alter_column(u'memberships_membershiptype', 'fixed_option2_can_rollover', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'MembershipType.allow_anonymous_view'
        db.alter_column(u'memberships_membershiptype', 'allow_anonymous_view', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'MembershipType.status'
        db.alter_column(u'memberships_membershiptype', 'status', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'MembershipType.admin_only'
        db.alter_column(u'memberships_membershiptype', 'admin_only', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'MembershipType.renewal'
        db.alter_column(u'memberships_membershiptype', 'renewal', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'MembershipType.never_expires'
        db.alter_column(u'memberships_membershiptype', 'never_expires', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'MembershipType.allow_user_edit'
        db.alter_column(u'memberships_membershiptype', 'allow_user_edit', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'MembershipType.allow_member_view'
        db.alter_column(u'memberships_membershiptype', 'allow_member_view', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'MembershipType.allow_member_edit'
        db.alter_column(u'memberships_membershiptype', 'allow_member_edit', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'MembershipType.require_payment_approval'
        db.alter_column(u'memberships_membershiptype', 'require_payment_approval', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'MembershipApp.use_captcha'
        db.alter_column(u'memberships_membershipapp', 'use_captcha', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'MembershipApp.allow_user_view'
        db.alter_column(u'memberships_membershipapp', 'allow_user_view', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'MembershipApp.discount_eligible'
        db.alter_column(u'memberships_membershipapp', 'discount_eligible', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'MembershipApp.include_tax'
        db.alter_column(u'memberships_membershipapp', 'include_tax', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'MembershipApp.allow_anonymous_view'
        db.alter_column(u'memberships_membershipapp', 'allow_anonymous_view', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'MembershipApp.status'
        db.alter_column(u'memberships_membershipapp', 'status', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'MembershipApp.allow_multiple_membership'
        db.alter_column(u'memberships_membershipapp', 'allow_multiple_membership', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'MembershipApp.allow_user_edit'
        db.alter_column(u'memberships_membershipapp', 'allow_user_edit', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'MembershipApp.allow_member_view'
        db.alter_column(u'memberships_membershipapp', 'allow_member_view', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'MembershipApp.use_for_corp'
        db.alter_column(u'memberships_membershipapp', 'use_for_corp', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'MembershipApp.allow_member_edit'
        db.alter_column(u'memberships_membershipapp', 'allow_member_edit', self.gf('django.db.models.fields.NullBooleanField')(null=True))

    def backwards(self, orm):

        # Changing field 'MembershipDefault.status'
        db.alter_column(u'memberships_membershipdefault', 'status', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'MembershipDefault.allow_member_edit'
        db.alter_column(u'memberships_membershipdefault', 'allow_member_edit', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'MembershipDefault.application_approved'
        db.alter_column(u'memberships_membershipdefault', 'application_approved', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'MembershipDefault.allow_user_view'
        db.alter_column(u'memberships_membershipdefault', 'allow_user_view', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'MembershipDefault.allow_anonymous_view'
        db.alter_column(u'memberships_membershipdefault', 'allow_anonymous_view', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'MembershipDefault.application_abandoned'
        db.alter_column(u'memberships_membershipdefault', 'application_abandoned', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'MembershipDefault.override'
        db.alter_column(u'memberships_membershipdefault', 'override', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'MembershipDefault.application_denied'
        db.alter_column(u'memberships_membershipdefault', 'application_denied', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'MembershipDefault.application_complete'
        db.alter_column(u'memberships_membershipdefault', 'application_complete', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'MembershipDefault.renewal'
        db.alter_column(u'memberships_membershipdefault', 'renewal', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'MembershipDefault.allow_member_view'
        db.alter_column(u'memberships_membershipdefault', 'allow_member_view', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'MembershipDefault.government_worker'
        db.alter_column(u'memberships_membershipdefault', 'government_worker', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'MembershipDefault.allow_user_edit'
        db.alter_column(u'memberships_membershipdefault', 'allow_user_edit', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'MembershipDefault.exported'
        db.alter_column(u'memberships_membershipdefault', 'exported', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'MembershipAppField.admin_only'
        db.alter_column(u'memberships_membershipappfield', 'admin_only', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'MembershipAppField.required'
        db.alter_column(u'memberships_membershipappfield', 'required', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'MembershipAppField.display'
        db.alter_column(u'memberships_membershipappfield', 'display', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Notice.status'
        db.alter_column(u'memberships_notice', 'status', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Notice.system_generated'
        db.alter_column(u'memberships_notice', 'system_generated', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'NoticeDefaultLogRecord.action_taken'
        db.alter_column(u'memberships_noticedefaultlogrecord', 'action_taken', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'MembershipType.allow_user_view'
        db.alter_column(u'memberships_membershiptype', 'allow_user_view', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'MembershipType.allow_renewal'
        db.alter_column(u'memberships_membershiptype', 'allow_renewal', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'MembershipType.require_approval'
        db.alter_column(u'memberships_membershiptype', 'require_approval', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'MembershipType.renewal_require_approval'
        db.alter_column(u'memberships_membershiptype', 'renewal_require_approval', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'MembershipType.fixed_option2_can_rollover'
        db.alter_column(u'memberships_membershiptype', 'fixed_option2_can_rollover', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'MembershipType.allow_anonymous_view'
        db.alter_column(u'memberships_membershiptype', 'allow_anonymous_view', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'MembershipType.status'
        db.alter_column(u'memberships_membershiptype', 'status', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'MembershipType.admin_only'
        db.alter_column(u'memberships_membershiptype', 'admin_only', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'MembershipType.renewal'
        db.alter_column(u'memberships_membershiptype', 'renewal', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'MembershipType.never_expires'
        db.alter_column(u'memberships_membershiptype', 'never_expires', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'MembershipType.allow_user_edit'
        db.alter_column(u'memberships_membershiptype', 'allow_user_edit', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'MembershipType.allow_member_view'
        db.alter_column(u'memberships_membershiptype', 'allow_member_view', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'MembershipType.allow_member_edit'
        db.alter_column(u'memberships_membershiptype', 'allow_member_edit', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'MembershipType.require_payment_approval'
        db.alter_column(u'memberships_membershiptype', 'require_payment_approval', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'MembershipApp.use_captcha'
        db.alter_column(u'memberships_membershipapp', 'use_captcha', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'MembershipApp.allow_user_view'
        db.alter_column(u'memberships_membershipapp', 'allow_user_view', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'MembershipApp.discount_eligible'
        db.alter_column(u'memberships_membershipapp', 'discount_eligible', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'MembershipApp.include_tax'
        db.alter_column(u'memberships_membershipapp', 'include_tax', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'MembershipApp.allow_anonymous_view'
        db.alter_column(u'memberships_membershipapp', 'allow_anonymous_view', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'MembershipApp.status'
        db.alter_column(u'memberships_membershipapp', 'status', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'MembershipApp.allow_multiple_membership'
        db.alter_column(u'memberships_membershipapp', 'allow_multiple_membership', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'MembershipApp.allow_user_edit'
        db.alter_column(u'memberships_membershipapp', 'allow_user_edit', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'MembershipApp.allow_member_view'
        db.alter_column(u'memberships_membershipapp', 'allow_member_view', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'MembershipApp.use_for_corp'
        db.alter_column(u'memberships_membershipapp', 'use_for_corp', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'MembershipApp.allow_member_edit'
        db.alter_column(u'memberships_membershipapp', 'allow_member_edit', self.gf('django.db.models.fields.BooleanField')())

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
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user_groups.Group']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
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
        u'memberships.membershipappfield': {
            'Meta': {'ordering': "('position',)", 'object_name': 'MembershipAppField'},
            'admin_only': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'choices': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'blank': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'null': 'True'}),
            'css_class': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'default_value': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'display': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'field_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'field_type': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'help_text': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '300', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '2000'}),
            'membership_app': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fields'", 'to': u"orm['memberships.MembershipApp']"}),
            'position': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'required': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'})
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
        u'memberships.membershipdemographic': {
            'Meta': {'object_name': 'MembershipDemographic'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ud1': ('django.db.models.fields.TextField', [], {'default': "u''", 'null': 'True', 'blank': 'True'}),
            'ud10': ('django.db.models.fields.TextField', [], {'default': "u''", 'null': 'True', 'blank': 'True'}),
            'ud11': ('django.db.models.fields.TextField', [], {'default': "u''", 'null': 'True', 'blank': 'True'}),
            'ud12': ('django.db.models.fields.TextField', [], {'default': "u''", 'null': 'True', 'blank': 'True'}),
            'ud13': ('django.db.models.fields.TextField', [], {'default': "u''", 'null': 'True', 'blank': 'True'}),
            'ud14': ('django.db.models.fields.TextField', [], {'default': "u''", 'null': 'True', 'blank': 'True'}),
            'ud15': ('django.db.models.fields.TextField', [], {'default': "u''", 'null': 'True', 'blank': 'True'}),
            'ud16': ('django.db.models.fields.TextField', [], {'default': "u''", 'null': 'True', 'blank': 'True'}),
            'ud17': ('django.db.models.fields.TextField', [], {'default': "u''", 'null': 'True', 'blank': 'True'}),
            'ud18': ('django.db.models.fields.TextField', [], {'default': "u''", 'null': 'True', 'blank': 'True'}),
            'ud19': ('django.db.models.fields.TextField', [], {'default': "u''", 'null': 'True', 'blank': 'True'}),
            'ud2': ('django.db.models.fields.TextField', [], {'default': "u''", 'null': 'True', 'blank': 'True'}),
            'ud20': ('django.db.models.fields.TextField', [], {'default': "u''", 'null': 'True', 'blank': 'True'}),
            'ud21': ('django.db.models.fields.TextField', [], {'default': "u''", 'null': 'True', 'blank': 'True'}),
            'ud22': ('django.db.models.fields.TextField', [], {'default': "u''", 'null': 'True', 'blank': 'True'}),
            'ud23': ('django.db.models.fields.TextField', [], {'default': "u''", 'null': 'True', 'blank': 'True'}),
            'ud24': ('django.db.models.fields.TextField', [], {'default': "u''", 'null': 'True', 'blank': 'True'}),
            'ud25': ('django.db.models.fields.TextField', [], {'default': "u''", 'null': 'True', 'blank': 'True'}),
            'ud26': ('django.db.models.fields.TextField', [], {'default': "u''", 'null': 'True', 'blank': 'True'}),
            'ud27': ('django.db.models.fields.TextField', [], {'default': "u''", 'null': 'True', 'blank': 'True'}),
            'ud28': ('django.db.models.fields.TextField', [], {'default': "u''", 'null': 'True', 'blank': 'True'}),
            'ud29': ('django.db.models.fields.TextField', [], {'default': "u''", 'null': 'True', 'blank': 'True'}),
            'ud3': ('django.db.models.fields.TextField', [], {'default': "u''", 'null': 'True', 'blank': 'True'}),
            'ud30': ('django.db.models.fields.TextField', [], {'default': "u''", 'null': 'True', 'blank': 'True'}),
            'ud4': ('django.db.models.fields.TextField', [], {'default': "u''", 'null': 'True', 'blank': 'True'}),
            'ud5': ('django.db.models.fields.TextField', [], {'default': "u''", 'null': 'True', 'blank': 'True'}),
            'ud6': ('django.db.models.fields.TextField', [], {'default': "u''", 'null': 'True', 'blank': 'True'}),
            'ud7': ('django.db.models.fields.TextField', [], {'default': "u''", 'null': 'True', 'blank': 'True'}),
            'ud8': ('django.db.models.fields.TextField', [], {'default': "u''", 'null': 'True', 'blank': 'True'}),
            'ud9': ('django.db.models.fields.TextField', [], {'default': "u''", 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'demographics'", 'unique': 'True', 'to': u"orm['auth.User']"})
        },
        u'memberships.membershipfile': {
            'Meta': {'object_name': 'MembershipFile', '_ormbases': [u'files.File']},
            u'file_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['files.File']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'memberships.membershipimport': {
            'Meta': {'object_name': 'MembershipImport'},
            'complete_dt': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'header_line': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '3000'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interactive': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'key': ('django.db.models.fields.CharField', [], {'default': "'email/member_number/fn_ln_phone'", 'max_length': '50'}),
            'num_processed': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'override': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'recap_file': ('django.db.models.fields.files.FileField', [], {'max_length': '260', 'null': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'not_started'", 'max_length': '50'}),
            'summary': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '500', 'null': 'True'}),
            'total_rows': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'upload_file': ('django.db.models.fields.files.FileField', [], {'max_length': '260', 'null': 'True'})
        },
        u'memberships.membershipimportdata': {
            'Meta': {'object_name': 'MembershipImportData'},
            'action_taken': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True'}),
            'error': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '500'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mimport': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'membership_import_data'", 'to': u"orm['memberships.MembershipImport']"}),
            'row_data': ('tendenci.apps.base.fields.DictField', [], {}),
            'row_num': ('django.db.models.fields.IntegerField', [], {})
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
        u'memberships.notice': {
            'Meta': {'object_name': 'Notice'},
            'content_type': ('django.db.models.fields.CharField', [], {'default': "'html'", 'max_length': '10'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'membership_notice_creator'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'email_content': ('tinymce.models.HTMLField', [], {}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'membership_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['memberships.MembershipType']", 'null': 'True', 'blank': 'True'}),
            'notice_name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'notice_time': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'notice_type': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'num_days': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'membership_notice_owner'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True'}),
            'sender': ('django.db.models.fields.EmailField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'sender_display': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'system_generated': ('django.db.models.fields.NullBooleanField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'memberships.noticedefaultlogrecord': {
            'Meta': {'object_name': 'NoticeDefaultLogRecord'},
            'action_taken': ('django.db.models.fields.NullBooleanField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'action_taken_dt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'membership': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'default_log_records'", 'to': u"orm['memberships.MembershipDefault']"}),
            'notice_log': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'default_log_records'", 'to': u"orm['memberships.NoticeLog']"})
        },
        u'memberships.noticelog': {
            'Meta': {'object_name': 'NoticeLog'},
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notice': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'logs'", 'to': u"orm['memberships.Notice']"}),
            'notice_sent_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'num_sent': ('django.db.models.fields.IntegerField', [], {})
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

    complete_apps = ['memberships']