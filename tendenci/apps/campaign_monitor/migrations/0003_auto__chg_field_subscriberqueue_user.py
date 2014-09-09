# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'SubscriberQueue.user'
        db.alter_column(u'campaign_monitor_subscriberqueue', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, on_delete=models.SET_NULL))

    def backwards(self, orm):

        # Changing field 'SubscriberQueue.user'
        db.alter_column(u'campaign_monitor_subscriberqueue', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True))

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
        u'campaign_monitor.campaign': {
            'Meta': {'object_name': 'Campaign'},
            'campaign_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'from_email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'from_name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lists': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['campaign_monitor.ListMap']", 'symmetrical': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'preview_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'reply_to': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'scheduled_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'scheduled_time_zone': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'sent_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'D'", 'max_length': '1'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'template': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['campaign_monitor.Template']", 'null': 'True', 'blank': 'True'}),
            'total_recipients': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'web_version_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        u'campaign_monitor.groupqueue': {
            'Meta': {'object_name': 'GroupQueue'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user_groups.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'campaign_monitor.listmap': {
            'Meta': {'object_name': 'ListMap'},
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user_groups.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_sync_dt': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'list_id': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'campaign_monitor.subscriberqueue': {
            'Meta': {'object_name': 'SubscriberQueue'},
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['user_groups.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'subscriber': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['forms.FormEntry']", 'null': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'on_delete': 'models.SET_NULL'})
        },
        u'campaign_monitor.template': {
            'Meta': {'object_name': 'Template'},
            'cm_preview_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True'}),
            'cm_screenshot_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'html_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'template_id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'unique': 'True', 'null': 'True'}),
            'update_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'zip_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True'})
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
        u'forms.form': {
            'Meta': {'object_name': 'Form'},
            'allow_anonymous_view': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
            'allow_member_edit': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_member_view': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_user_edit': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'allow_user_view': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'completion_url': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'null': 'True', 'blank': 'True'}),
            'create_dt': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "u'forms_form_creator'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'creator_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'custom_payment': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'email_copies': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'blank': 'True'}),
            'email_from': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'email_text': ('django.db.models.fields.TextField', [], {'default': "''", 'max_length': '2000', 'blank': 'True'}),
            'entity': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'forms_form_entity'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': u"orm['entities.Entity']", 'blank': 'True', 'null': 'True'}),
            'fields_name': ('django.db.models.fields.CharField', [], {'default': "'Fields'", 'max_length': '50', 'blank': 'True'}),
            'fields_position': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intro': ('django.db.models.fields.TextField', [], {'max_length': '2000', 'blank': 'True'}),
            'intro_name': ('django.db.models.fields.CharField', [], {'default': "'Intro'", 'max_length': '50', 'blank': 'True'}),
            'intro_position': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "u'forms_form_owner'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['auth.User']"}),
            'owner_username': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'payment_methods': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['payments.PaymentMethod']", 'symmetrical': 'False', 'blank': 'True'}),
            'pricing_name': ('django.db.models.fields.CharField', [], {'default': "'Pricings'", 'max_length': '50', 'blank': 'True'}),
            'pricing_position': ('django.db.models.fields.IntegerField', [], {'default': '3'}),
            'recurring_payment': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'response': ('django.db.models.fields.TextField', [], {'max_length': '2000', 'blank': 'True'}),
            'send_email': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'}),
            'status': ('django.db.models.fields.NullBooleanField', [], {'default': 'True', 'null': 'True', 'blank': 'True'}),
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
            'has_trial_period': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'num_days': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'price': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '10', 'decimal_places': '2', 'blank': 'True'}),
            'tax_rate': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '5', 'decimal_places': '4', 'blank': 'True'}),
            'taxable': ('django.db.models.fields.NullBooleanField', [], {'default': 'False', 'null': 'True', 'blank': 'True'}),
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

    complete_apps = ['campaign_monitor']