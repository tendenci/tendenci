# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Pricing.taxable'
        db.alter_column(u'forms_pricing', 'taxable', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Pricing.has_trial_period'
        db.alter_column(u'forms_pricing', 'has_trial_period', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Form.allow_user_view'
        db.alter_column(u'forms_form', 'allow_user_view', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Form.send_email'
        db.alter_column(u'forms_form', 'send_email', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Form.custom_payment'
        db.alter_column(u'forms_form', 'custom_payment', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Form.allow_anonymous_view'
        db.alter_column(u'forms_form', 'allow_anonymous_view', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Form.status'
        db.alter_column(u'forms_form', 'status', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Form.recurring_payment'
        db.alter_column(u'forms_form', 'recurring_payment', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Form.allow_user_edit'
        db.alter_column(u'forms_form', 'allow_user_edit', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Form.allow_member_view'
        db.alter_column(u'forms_form', 'allow_member_view', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Form.allow_member_edit'
        db.alter_column(u'forms_form', 'allow_member_edit', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Field.required'
        db.alter_column(u'forms_field', 'required', self.gf('django.db.models.fields.BooleanField')())

        # Changing field 'Field.visible'
        db.alter_column(u'forms_field', 'visible', self.gf('django.db.models.fields.BooleanField')())

    def backwards(self, orm):

        # Changing field 'Pricing.taxable'
        db.alter_column(u'forms_pricing', 'taxable', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Pricing.has_trial_period'
        db.alter_column(u'forms_pricing', 'has_trial_period', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Form.allow_user_view'
        db.alter_column(u'forms_form', 'allow_user_view', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Form.send_email'
        db.alter_column(u'forms_form', 'send_email', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Form.custom_payment'
        db.alter_column(u'forms_form', 'custom_payment', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Form.allow_anonymous_view'
        db.alter_column(u'forms_form', 'allow_anonymous_view', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Form.status'
        db.alter_column(u'forms_form', 'status', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Form.recurring_payment'
        db.alter_column(u'forms_form', 'recurring_payment', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Form.allow_user_edit'
        db.alter_column(u'forms_form', 'allow_user_edit', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Form.allow_member_view'
        db.alter_column(u'forms_form', 'allow_member_view', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Form.allow_member_edit'
        db.alter_column(u'forms_form', 'allow_member_edit', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Field.required'
        db.alter_column(u'forms_field', 'required', self.gf('django.db.models.fields.NullBooleanField')(null=True))

        # Changing field 'Field.visible'
        db.alter_column(u'forms_field', 'visible', self.gf('django.db.models.fields.NullBooleanField')(null=True))

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
            'allow_anonymous_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_anonymous_view': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'allow_member_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_member_view': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'allow_user_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_user_view': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
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
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'summary': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'website': ('django.db.models.fields.CharField', [], {'max_length': '300', 'blank': 'True'})
        },
        u'forms.field': {
            'Meta': {'object_name': 'Field'},
            'choices': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'blank': 'True'}),
            'default': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'blank': 'True'}),
            'field_function': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'field_type': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'form': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fields'", 'to': u"orm['forms.Form']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '2000'}),
            'position': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'forms.fieldentry': {
            'Meta': {'object_name': 'FieldEntry'},
            'entry': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'fields'", 'to': u"orm['forms.FormEntry']"}),
            'field': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'field'", 'to': u"orm['forms.Field']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '2000'})
        },
        u'forms.form': {
            'Meta': {'object_name': 'Form'},
            'allow_anonymous_view': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'allow_member_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_member_view': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'allow_user_edit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allow_user_view': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'completion_url': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "u'forms_form_creator'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'custom_payment': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'email_copies': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'blank': 'True'}),
            'email_from': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'email_text': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '2000', 'blank': 'True'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'forms_form_entity'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': u"orm['entities.Entity']", 'blank': 'True', 'null': 'True'}),
            'fields_name': ('django.db.models.fields.CharField', [], {'default': "u'Fields'", 'max_length': '50', 'blank': 'True'}),
            'fields_position': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intro': ('django.db.models.fields.TextField', [], {'max_length': '2000', 'blank': 'True'}),
            'intro_name': ('django.db.models.fields.CharField', [], {'default': "u'Intro'", 'max_length': '50', 'blank': 'True'}),
            'intro_position': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "u'forms_form_owner'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'payment_methods': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['payments.PaymentMethod']", 'symmetrical': 'False', 'blank': 'True'}),
            'pricing_name': ('django.db.models.fields.CharField', [], {'default': "u'Pricings'", 'max_length': '50', 'blank': 'True'}),
            'pricing_position': ('django.db.models.fields.IntegerField', [], {'default': '3'}),
            'recurring_payment': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'response': ('django.db.models.fields.TextField', [], {'max_length': '2000', 'blank': 'True'}),
            'send_email': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'}),
            'status': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'status_detail': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '50'}),
            'subject_template': ('django.db.models.fields.CharField', [], {'default': "'[title] - [first name]  [last name] - [phone]'", 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'template': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'forms.formentry': {
            'Meta': {'object_name': 'FormEntry'},
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'formentry_creator'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'entry_path': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'entry_time': ('django.db.models.fields.DateTimeField', [], {}),
            'form': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'entries'", 'to': u"orm['forms.Form']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'payment_method': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['payments.PaymentMethod']", 'null': 'True'}),
            'pricing': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['forms.Pricing']", 'null': 'True'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'forms.pricing': {
            'Meta': {'ordering': "['pk']", 'object_name': 'Pricing'},
            'billing_frequency': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'billing_period': ('django.db.models.fields.CharField', [], {'default': "'month'", 'max_length': '50'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'due_sore': ('django.db.models.fields.CharField', [], {'default': "'start'", 'max_length': '20'}),
            'form': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['forms.Form']"}),
            'has_trial_period': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'num_days': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'price': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'tax_rate': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '5', 'decimal_places': '4', 'blank': 'True'}),
            'taxable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'trial_amount': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'null': 'True', 'max_digits': '15', 'decimal_places': '2', 'blank': 'True'}),
            'trial_period_days': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'payments.paymentmethod': {
            'Meta': {'object_name': 'PaymentMethod'},
            'admin_only': ('django.db.models.fields.NullBooleanField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'human_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_online': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'machine_name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['forms']