# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'NavItem.new_window'
        db.alter_column(u'navs_navitem', 'new_window', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Nav.status'
        db.alter_column(u'navs_nav', 'status', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Nav.allow_user_edit'
        db.alter_column(u'navs_nav', 'allow_user_edit', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Nav.allow_user_view'
        db.alter_column(u'navs_nav', 'allow_user_view', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Nav.creator'
        db.alter_column(u'navs_nav', 'creator_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.SET_NULL, to=orm['auth.User']))

        # Changing field 'Nav.allow_member_view'
        db.alter_column(u'navs_nav', 'allow_member_view', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Nav.entity'
        db.alter_column(u'navs_nav', 'entity_id', self.gf('django.db.models.fields.related.ForeignKey')(on_delete=models.SET_NULL, to=orm['entities.Entity'], null=True))

        # Changing field 'Nav.allow_member_edit'
        db.alter_column(u'navs_nav', 'allow_member_edit', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Nav.owner'
        db.alter_column(u'navs_nav', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, on_delete=models.SET_NULL, to=orm['auth.User']))

        # Changing field 'Nav.megamenu'
        db.alter_column(u'navs_nav', 'megamenu', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Nav.allow_anonymous_view'
        db.alter_column(u'navs_nav', 'allow_anonymous_view', self.gf('django.db.models.fields.NullBooleanField')(null=True))

    def backwards(self, orm):

        # Changing field 'NavItem.new_window'
        db.alter_column(u'navs_navitem', 'new_window', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Nav.status'
        db.alter_column(u'navs_nav', 'status', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Nav.allow_user_edit'
        db.alter_column(u'navs_nav', 'allow_user_edit', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Nav.allow_user_view'
        db.alter_column(u'navs_nav', 'allow_user_view', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Nav.creator'
        db.alter_column(u'navs_nav', 'creator_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['auth.User']))

        # Changing field 'Nav.allow_member_view'
        db.alter_column(u'navs_nav', 'allow_member_view', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Nav.entity'
        db.alter_column(u'navs_nav', 'entity_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['entities.Entity']))

        # Changing field 'Nav.allow_member_edit'
        db.alter_column(u'navs_nav', 'allow_member_edit', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Nav.owner'
        db.alter_column(u'navs_nav', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['auth.User']))

        # Changing field 'Nav.megamenu'
        db.alter_column(u'navs_nav', 'megamenu', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Nav.allow_anonymous_view'
        db.alter_column(u'navs_nav', 'allow_anonymous_view', self.gf('django.db.models.fields.BooleanField')())

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
        u'navs.nav': {
            'Meta': {'object_name': 'Nav'},
            'allow_anonymous_view': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'allow_member_edit': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_member_view': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_user_edit': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_user_view': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "u'navs_nav_creator'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'navs_nav_entity'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': u"orm['entities.Entity']", 'blank': 'True', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'megamenu': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "u'navs_nav_owner'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'status': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'navs.navitem': {
            'Meta': {'ordering': "('position',)", 'object_name': 'NavItem'},
            'css': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'level': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'nav': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['navs.Nav']"}),
            'new_window': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'page': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pages.Page']", 'null': 'True'}),
            'position': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        u'pages.headerimage': {
            'Meta': {'object_name': 'HeaderImage', '_ormbases': [u'files.File']},
            u'file_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['files.File']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'pages.page': {
            'Meta': {'object_name': 'Page'},
            'allow_anonymous_view': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'allow_member_edit': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_member_view': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_user_edit': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_user_view': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'content': ('tinymce.models.HTMLField', [], {}),
            'contributor_type': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "u'pages_page_creator'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'design_notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'pages_page_entity'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': u"orm['entities.Entity']", 'blank': 'True', 'null': 'True'}),
            'google_profile': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'header_image': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pages.HeaderImage']", 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'meta': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['meta.Meta']", 'unique': 'True', 'null': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "u'pages_page_owner'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'slug': ('tendenci.apps.base.fields.SlugField', [], {'max_length': '100', 'db_index': 'True'}),
            'status': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'syndicate': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'tags': ('tagging.fields.TagField', [], {}),
            'template': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500', 'blank': 'True'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'view_contact_form': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'})
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

    complete_apps = ['navs']