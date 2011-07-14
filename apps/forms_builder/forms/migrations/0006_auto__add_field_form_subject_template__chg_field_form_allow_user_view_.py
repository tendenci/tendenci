# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Form.subject_template'
        db.add_column('forms_form', 'subject_template', self.gf('django.db.models.fields.CharField')(default='[title] - [first name]  [last name] - [phone]', max_length=200, null=True, blank=True), keep_default=False)

        # Changing field 'Form.allow_user_view'
        db.alter_column('forms_form', 'allow_user_view', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'Form.send_email'
        db.alter_column('forms_form', 'send_email', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'Form.allow_anonymous_edit'
        db.alter_column('forms_form', 'allow_anonymous_edit', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'Form.allow_anonymous_view'
        db.alter_column('forms_form', 'allow_anonymous_view', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'Form.status'
        db.alter_column('forms_form', 'status', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'Form.allow_user_edit'
        db.alter_column('forms_form', 'allow_user_edit', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'Form.allow_member_view'
        db.alter_column('forms_form', 'allow_member_view', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'Form.allow_member_edit'
        db.alter_column('forms_form', 'allow_member_edit', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'Field.required'
        db.alter_column('forms_field', 'required', self.gf('django.db.models.fields.BooleanField')(blank=True))

        # Changing field 'Field.visible'
        db.alter_column('forms_field', 'visible', self.gf('django.db.models.fields.BooleanField')(blank=True))


    def backwards(self, orm):
        
        # Deleting field 'Form.subject_template'
        db.delete_column('forms_form', 'subject_template')

        # Changing field 'Form.allow_user_view'
        db.alter_column('forms_form', 'allow_user_view', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Form.send_email'
        db.alter_column('forms_form', 'send_email', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Form.allow_anonymous_edit'
        db.alter_column('forms_form', 'allow_anonymous_edit', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Form.allow_anonymous_view'
        db.alter_column('forms_form', 'allow_anonymous_view', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Form.status'
        db.alter_column('forms_form', 'status', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Form.allow_user_edit'
        db.alter_column('forms_form', 'allow_user_edit', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Form.allow_member_view'
        db.alter_column('forms_form', 'allow_member_view', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Form.allow_member_edit'
        db.alter_column('forms_form', 'allow_member_edit', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Field.required'
        db.alter_column('forms_field', 'required', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Field.visible'
        db.alter_column('forms_field', 'visible', self.gf('django.db.models.fields.BooleanField')())


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
        'forms.field': {
            'Meta': {'object_name': 'Field'},
            '_order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'choices': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'blank': 'True'}),
            'field_function': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'field_type': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'form': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fields'", 'to': "orm['forms.Form']"}),
            'function_params': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'position': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'})
        },
        'forms.fieldentry': {
            'Meta': {'object_name': 'FieldEntry'},
            'entry': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fields'", 'to': "orm['forms.FormEntry']"}),
            'field': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'field'", 'to': "orm['forms.Field']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '2000'})
        },
        'forms.form': {
            'Meta': {'object_name': 'Form'},
            'allow_anonymous_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'allow_anonymous_view': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'allow_member_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'allow_member_view': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'allow_user_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'allow_user_view': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'form_creator'", 'to': "orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'email_copies': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'email_from': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intro': ('django.db.models.fields.TextField', [], {'max_length': '2000'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'form_owner'", 'to': "orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'response': ('django.db.models.fields.TextField', [], {'max_length': '2000'}),
            'send_email': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'subject_template': ('django.db.models.fields.CharField', [], {'default': "'[title] - [first name]  [last name] - [phone]'", 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'forms.formentry': {
            'Meta': {'object_name': 'FormEntry'},
            'entry_time': ('django.db.models.fields.DateTimeField', [], {}),
            'form': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'entries'", 'to': "orm['forms.Form']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['forms']
