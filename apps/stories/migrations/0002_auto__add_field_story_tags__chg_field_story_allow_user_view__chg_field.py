# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Story.tags'
        db.add_column('stories_story', 'tags', self.gf('tagging.fields.TagField')(default=''), keep_default=False)

        # Changing field 'Story.allow_user_view'
        db.alter_column('stories_story', 'allow_user_view', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'Story.allow_anonymous_edit'
        db.alter_column('stories_story', 'allow_anonymous_edit', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'Story.content'
        db.alter_column('stories_story', 'content', self.gf('django.db.models.fields.TextField')(blank=True))

        # Changing field 'Story.allow_anonymous_view'
        db.alter_column('stories_story', 'allow_anonymous_view', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'Story.status'
        db.alter_column('stories_story', 'status', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'Story.syndicate'
        db.alter_column('stories_story', 'syndicate', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'Story.allow_user_edit'
        db.alter_column('stories_story', 'allow_user_edit', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'Story.allow_member_view'
        db.alter_column('stories_story', 'allow_member_view', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'Story.allow_member_edit'
        db.alter_column('stories_story', 'allow_member_edit', self.gf('django.db.models.fields.BooleanField')(blank=True))


    def backwards(self, orm):
        
        # Deleting field 'Story.tags'
        db.delete_column('stories_story', 'tags')

        # Changing field 'Story.allow_user_view'
        db.alter_column('stories_story', 'allow_user_view', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Story.allow_anonymous_edit'
        db.alter_column('stories_story', 'allow_anonymous_edit', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Story.content'
        db.alter_column('stories_story', 'content', self.gf('tinymce.models.HTMLField')())

        # Changing field 'Story.allow_anonymous_view'
        db.alter_column('stories_story', 'allow_anonymous_view', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Story.status'
        db.alter_column('stories_story', 'status', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Story.syndicate'
        db.alter_column('stories_story', 'syndicate', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Story.allow_user_edit'
        db.alter_column('stories_story', 'allow_user_edit', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Story.allow_member_view'
        db.alter_column('stories_story', 'allow_member_view', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Story.allow_member_edit'
        db.alter_column('stories_story', 'allow_member_edit', self.gf('django.db.models.fields.BooleanField')())


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'entities.entity': {
            'Meta': {'object_name': 'Entity'},
            'admin_notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'allow_anonymous_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'allow_anonymous_view': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'allow_member_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'allow_member_view': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'allow_user_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'allow_user_view': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'contact_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'entity_creator'", 'to': "orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '120', 'blank': 'True'}),
            'entity_name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'entity_parent_id': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'entity_type': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'entity_owner'", 'to': "orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'summary': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'website': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'})
        },
        'stories.story': {
            'Meta': {'object_name': 'Story'},
            'allow_anonymous_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'allow_anonymous_view': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'allow_member_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'allow_member_view': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'allow_user_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'allow_user_view': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'story_creator'", 'to': "orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'end_dt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['entities.Entity']", 'null': 'True'}),
            'full_story_link': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ncsortorder': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'story_owner'", 'to': "orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'photo': ('django.db.models.fields.files.FileField', [], {'max_length': '260', 'null': 'True', 'blank': 'True'}),
            'start_dt': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'syndicate': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'tags': ('tagging.fields.TagField', [], {'default': "''"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['stories']
